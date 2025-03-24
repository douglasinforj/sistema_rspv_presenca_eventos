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

import logging


# Configuração do logger
logger = logging.getLogger(__name__)


def home(request):
    eventos = Evento.objects.all().order_by('-data')  # Carregar eventos ordenados por data
    return render(request, 'evento/home.html', {'eventos': eventos})


def lista_eventos(request):
    query = request.GET.get('q')
    if query:
        eventos = Evento.objects.filter(nome__icontains=query)
    else:
        eventos = Evento.objects.all()
    
    return render(request, 'evento/lista_eventos.html', {'eventos': eventos, 'query': query})



def adicionar_evento(request):
    if request.method == "POST":
        form = EventoForm(request.POST, request.FILES)   #adicionar imagem
        if form.is_valid():
            form.save()
            return redirect('lista_eventos') 
    else:
        form = EventoForm()
    
    return render(request, 'evento/adicionar_evento.html', {'form': form})


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
def detalhes_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)

    # Busca por nome ou email ou cpf
    query = request.GET.get('q')
    convidados = Convidado.objects.filter(evento=evento)

    if query:
        convidados = convidados.filter(nome__icontains=query) | convidados.filter(email__icontains=query) | convidados.filter(cpf__icontains=query)

    # Paginação (10 convidados por página)
    paginator = Paginator(convidados, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'evento/detalhes_evento.html', {
        'evento': evento, 
        'convidados': page_obj, 
        'query': query
    })

# importação de dados de arquivos csv e excel:

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
                    if created:
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
        cpf = request.POST.get('cpf', '').strip()  # Agora o CPF será capturado da requisição POST
        logger.debug(f"Recebido CPF: {cpf}")

        try:
            convidado = Convidado.objects.get(cpf=cpf)
            logger.debug(f"Convidado encontrado: {convidado.nome}")
            confirmacao, created = Confirmacao.objects.get_or_create(convidado=convidado)
            
            if 'confirmar' in request.POST:
                logger.debug("Botão 'Confirmar' pressionado.")
                
                form = RSVPForm(request.POST, instance=confirmacao)
                if form.is_valid():
                    confirmacao = form.save(commit=False)
                    confirmacao.confirmado = True
                    confirmacao.save()
                    
                    logger.debug(f"Confirmação salva para: {convidado.nome}")

                    qr_code = convidado.qrcode.url if convidado.qrcode else None
                    logger.debug(f"QR Code gerado: {qr_code}")

                    return render(request, 'evento/rsvp_sucesso.html', {'convidado': convidado, 'qr_code': qr_code})
                else:
                    logger.debug("Formulário não válido.")
            else:
                logger.debug("Formulário de confirmação não enviado.")

        except Convidado.DoesNotExist:
            logger.error(f"Convidado com CPF {cpf} não encontrado.")
            return render(request, 'evento/rsvp_convidado.html', {'erro': 'CPF não encontrado'})

    return render(request, 'evento/rsvp_convidado.html', {'form': form, 'convidado': convidado})




"""
Após após confirmações dos convidados
"""

def rsvp_sucesso(request):
    return render(request, 'evento/rsvp_sucesso.html')



def validar_qr_code(request):
    qr_code = request.GET.get("qr_code")

    try:
        convidado = Convidado.objects.get(qr_code=qr_code)
        confirmacao = Confirmacao.objects.get(convidado=convidado)

        if not confirmacao.confirmado:
            return JsonResponse({"status": "erro", "mensagem": "Convidado ainda não confirmou presença."}, status=400)
        
        # Realiza o check-in
        confirmacao.entrou = True
        confirmacao.save()

        return JsonResponse({"status": "sucesso", "mensagem": "Check-in realizado com sucesso!"})


    
    except Convidado.DoesNotExist:
        return JsonResponse({"status": "erro", "mensagem": "QR Code inválido."}, status=404)

    except Confirmacao.DoesNotExist:
        return JsonResponse({"status": "erro", "mensagem": "Confirmação não encontrada."}, status=404)



def checkin_view(request):
    return render(request, "evento/checkin_view.html")



#Login e Logout
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login realizado com sucesso!")
            return redirect('home')
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    return render(request, "auth/login.html")
            

def logout_view(request):
    logout(request)
    messages.success(request, "Você saiu do sistema.")
    return redirect("login")