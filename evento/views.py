from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from .models import Evento, Convidado, Confirmacao
from .forms import RSVPForm, ConvidadoForm, UploadFileForm, EventoForm

import pandas as pd
from django.contrib import messages

from django.core.paginator import Paginator

from django.http import JsonResponse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

import qrcode
import io
import base64
from django.core.files.base import ContentFile


from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .utils import generate_token
import datetime
from rsvp_evento import settings



#import logging

from django.views.decorators.csrf import csrf_exempt, csrf_protect 
import json
from django.views.decorators.http import require_GET, require_POST

from django.db.models import Q


# Configuração do logger
#logger = logging.getLogger(__name__)

@login_required
def home(request):
    eventos = Evento.objects.all().order_by('-data')  # Carregar eventos ordenados por data
    return render(request, 'evento/home.html', {'eventos': eventos})

@login_required
def lista_eventos(request):
    query = request.GET.get('q')
    if query:
        eventos = Evento.objects.filter(nome__icontains=query)
    else:
        eventos = Evento.objects.all()
    
    return render(request, 'evento/lista_eventos.html', {'eventos': eventos, 'query': query})


@login_required
def adicionar_evento(request):
    if request.method == "POST":
        form = EventoForm(request.POST, request.FILES)   #adicionar imagem
        if form.is_valid():
            form.save()
            return redirect('lista_eventos') 
    else:
        form = EventoForm()
    
    return render(request, 'evento/adicionar_evento.html', {'form': form})

@login_required
def cadastrar_convidado(request):
    if request.method == 'POST':
        form = ConvidadoForm(request.POST)
        if form.is_valid():
            convidado = form.save(commit=False)  # Não salva ainda
            convidado.save()  # Salva o convidado no banco de dados

            # Gera o QR Code para o convidado
            convidado.generate_qrcode()
            convidado.save()  # Salva o QR Code no banco

            return redirect('lista_eventos')  # Redireciona para a lista de eventos
    else:
        form = ConvidadoForm()
    return render(request, 'evento/cadastrar_convidado.html', {'form': form})

    
# Mostra os detalhes do evento e seu convidados associados
@login_required
def detalhes_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)

    # Busca por nome ou email ou cpf
    query = request.GET.get('q')
    convidados = Convidado.objects.filter(evento=evento).select_related('confirmacao')

    if query:
        convidados = convidados.filter(
            Q(nome__icontains=query) | 
            Q(email__icontains=query) | 
            Q(cpf__icontains=query)
        )

    # Ação de enviar convite
    if request.method == 'POST' and 'enviar_convite' in request.POST:
        convidado_id = request.POST.get('convidado_id')
        convidado = get_object_or_404(Convidado, id=convidado_id, evento=evento)
        
        # Gerar token único para o convidado
        token = generate_token(convidado.email)
        
        # Renderizar template de email
        subject = f"Convite para o evento {evento.nome}"
        html_message = render_to_string('evento/convite_evento.html', {
            'evento': evento,
            'convidado': convidado,
            'token': token,
        })
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [convidado.email],
                html_message=html_message,
                fail_silently=False,
            )
            # Atualizar status do convidado
            convidado.convite_enviado = True
            convidado.data_envio_convite = datetime.datetime.now()
            convidado.save()
            messages.success(request, f'Convite enviado com sucesso para {convidado.email}')
        except Exception as e:
            messages.error(request, f'Erro ao enviar email: {str(e)}')
        
        return redirect('detalhes_evento', evento_id=evento.id)

    # Paginação (10 convidados por página)
    paginator = Paginator(convidados, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'evento/detalhes_evento.html', {
        'evento': evento, 
        'convidados': page_obj, 
        'query': query
    })




@login_required
def marcar_checkin(request, convidado_id):
    convidado = get_object_or_404(Convidado, id=convidado_id)
    confirmacao, created = Confirmacao.objects.get_or_create(convidado=convidado)
    
    # Alternar o status de check-in
    confirmacao.entrou = not confirmacao.entrou
    confirmacao.save()
    
    messages.success(request, f'Check-in de {convidado.nome} atualizado com sucesso!')
    return redirect('detalhes_evento', evento_id=convidado.evento.id)





# importação de dados de arquivos csv e excel:
@login_required
def importar_convidados(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            
            # Verifica se é CSV ou Excel
            if file.name.endswith(".csv"):
                df = pd.read_csv(file, delimiter=";")  # Ajuste o delimitador conforme necessário
            elif file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                messages.error(request, "Formato de arquivo inválido. Use CSV ou Excel.")
                return redirect("importar_convidados")

            # Verifica se as colunas necessárias existem no arquivo
            colunas_necessarias = {"nome", "cpf", "email", "evento_id"}
            if not colunas_necessarias.issubset(df.columns):
                messages.error(request, "O arquivo deve conter as colunas: nome, cpf, email, evento_id")
                return redirect("importar_convidados")

            # Processa cada linha e cria os convidados
            for _, row in df.iterrows():
                try:
                    evento = Evento.objects.get(id=row["evento_id"])
                    convidado, created = Convidado.objects.get_or_create(
                        cpf=row["cpf"],
                        defaults={
                            "nome": row["nome"],
                            "email": row["email"],
                            "evento": evento,
                        }
                    )
                    
                    # Se foi criado agora, gera o QR Code
                    if created:
                        convidado.generate_qrcode()    #chamando a função antes de salva os dados para gerar qrcode
                        convidado.save()               # Salva o QR Code no banco de dados
                        messages.success(request, f"Convidado {convidado.nome} importado com sucesso.")
                    else:
                        messages.warning(request, f"O convidado {convidado.nome} já existe.")
                
                except Evento.DoesNotExist:
                    messages.error(request, f"Evento ID {row['evento_id']} não encontrado.")
                except Exception as e:
                    messages.error(request, f"Erro ao importar {row['nome']}: {e}")

            return redirect("importar_convidados")

    else:
        form = UploadFileForm()
    
    return render(request, "evento/importar_convidados.html", {"form": form})


@login_required
def rsvp_atendente(request, convidado_id):
    convidado = get_object_or_404(Convidado, id=convidado_id)
    confirmacao, created = Confirmacao.objects.get_or_create(convidado=convidado)

    if request.method == 'POST':
        form = RSVPForm(request.POST, instance=confirmacao)
        if form.is_valid():
            form.save()
            messages.success(request, "Confirmação atualizada com sucesso!")
            return redirect('detalhes_evento', evento_id=convidado.evento.id)
    else:
        form = RSVPForm(instance=confirmacao)

    return render(request, 'evento/rsvp_atendente.html', {'form': form, 'convidado': convidado})


def rsvp_convidado(request):
    convidado = None
    form = None
    qr_code = None

    if request.method == 'POST':
        cpf = request.POST.get('cpf', '').strip()

        try:
            convidado = Convidado.objects.get(cpf=cpf)
            confirmacao, created = Confirmacao.objects.get_or_create(convidado=convidado)
            
            if 'confirmar' in request.POST:
                form = RSVPForm(request.POST, instance=confirmacao)
                if form.is_valid():
                    confirmacao = form.save(commit=False)
                    confirmacao.confirmado = True
                    confirmacao.save()

                    qr_code = convidado.qrcode.url if convidado.qrcode else None

                    return render(request, 'evento/rsvp_sucesso.html', {'convidado': convidado, 'qr_code': qr_code})

        except Convidado.DoesNotExist:
            return render(request, 'evento/rsvp_convidado.html', {'erro': 'CPF não encontrado'})

    return render(request, 'evento/rsvp_convidado.html', {'form': form, 'convidado': convidado})




"""
Após após confirmações dos convidados
"""

def rsvp_sucesso(request):
    return render(request, 'evento/rsvp_sucesso.html')


#@csrf_exempt
@require_POST
@csrf_protect
def validar_qr_code(request):
    try:
        data = json.loads(request.body)
        qr_code = data.get("qr_code", "").strip()
        evento_id = data.get("evento_id", "").strip()

        # Validação básica
        if not qr_code or not evento_id:
            return JsonResponse({
                "status": "error",
                "message": "QR Code e ID do Evento são obrigatórios."
            }, status=400)

        # Verifica formato do QR Code
        if "_" not in qr_code:
            return JsonResponse({
                "status": "error",
                "message": "Formato inválido do QR Code. Deve ser CPF_ID_EVENTO."
            }, status=400)

        # Separa CPF e ID do evento do QR Code
        try:
            cpf, qr_evento_id = qr_code.split("_")
            if not cpf.isdigit() or len(cpf) != 11:
                raise ValueError
            if not qr_evento_id.isdigit():
                raise ValueError
        except ValueError:
            return JsonResponse({
                "status": "error",
                "message": "Formato inválido do QR Code. CPF ou ID do evento incorretos."
            }, status=400)

        # Verifica se o ID do evento no QR corresponde ao evento selecionado
        if int(qr_evento_id) != int(evento_id):
            return JsonResponse({
                "status": "error",
                "message": "QR Code não pertence a este evento."
            }, status=400)

        # Busca o convidado
        try:
            convidado = Convidado.objects.get(cpf=cpf, evento_id=evento_id)
            confirmacao = Confirmacao.objects.get(convidado=convidado)
        except Convidado.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Convidado não encontrado para este evento."
            }, status=404)
        except Confirmacao.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Confirmação não encontrada para este convidado."
            }, status=404)

        # Verifica status da confirmação
        if not confirmacao.confirmado:
            return JsonResponse({
                "status": "error",
                "message": "Convidado ainda não confirmou presença."
            }, status=400)

        if confirmacao.entrou:
            return JsonResponse({
                "status": "error",
                "message": "Check-in já realizado anteriormente."
            }, status=400)

        # Realiza o check-in
        confirmacao.entrou = True
        confirmacao.data_checkin = timezone.now()
        confirmacao.save()

        return JsonResponse({
            "status": "success",
            "message": "Check-in realizado com sucesso!",
            "convidado": {
                "nome": convidado.nome,
                "cpf": convidado.cpf,
                "evento": convidado.evento.nome
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "Erro ao decodificar JSON."
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Erro inesperado: {str(e)}"
        }, status=500)







def checkin_view(request):
    eventos = Evento.objects.all()  # Busca todos os eventos
    return render(request, "evento/checkin_view.html", {"eventos": eventos})



#Login e Logout
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            #messages.success(request, "Login realizado com sucesso!")
            return redirect('home')
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    return render(request, "auth/login.html")
            

def logout_view(request):
    logout(request)
    #messages.success(request, "Você saiu do sistema.")
    return redirect("login_view")



def relatorio_evento(request):
    eventos = Evento.objects.all()
    evento_selecionado = request.GET.get("evento")

    convidados = Convidado.objects.filter(evento_id=evento_selecionado) if evento_selecionado else []
    confirmados = Confirmacao.objects.filter(convidado__evento_id=evento_selecionado, confirmado=True).count() if evento_selecionado else 0
    checkins = Confirmacao.objects.filter(convidado__evento_id=evento_selecionado, entrou=True).count() if evento_selecionado else 0

    context = {
        "eventos": eventos,
        "convidados": convidados,
        "confirmados": confirmados,
        "checkins": checkins,
        "evento_selecionado": evento_selecionado,
    }
    return render(request, "evento/relatorio_evento.html", context)