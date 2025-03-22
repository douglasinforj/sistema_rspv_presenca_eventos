from django.shortcuts import render, get_object_or_404, redirect
from .models import Evento, Convidado, Confirmacao
from .forms import RSVPForm, ConvidadoForm, UploadFileForm, EventoForm

import pandas as pd
from django.contrib import messages

from django.core.paginator import Paginator



def home(request):
    return render(request, 'evento/home.html')


def lista_eventos(request):
    query = request.GET.get('q')
    if query:
        eventos = Evento.objects.filter(nome__icontains=query)
    else:
        eventos = Evento.objects.all()
    
    return render(request, 'evento/lista_eventos.html', {'eventos': eventos, 'query': query})



def adicionar_evento(request):
    if request.method == "POST":
        form = EventoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_eventos') 
    else:
        form = EventoForm()
    
    return render(request, 'evento/adicionar_evento.html', {'form': form})
    




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





# TODO: descontinuar este codigo, ficou meio sem sentido
def rsvp(request, convidado_id):
    convidado = get_object_or_404(Convidado, id=convidado_id)

    # Verifica se a confirmação já existe, caso contrário, não cria automaticamente
    confirmacao = getattr(convidado, 'confirmacao', None)

    if request.method == 'POST':
        if not confirmacao:
            confirmacao = Confirmacao(convidado=convidado)  # Cria apenas quando necessário
        
        form = RSVPForm(request.POST, instance=confirmacao)
        if form.is_valid():
            form.save()
            return redirect('detalhes_evento', evento_id=convidado.evento.id)
    else:
        form = RSVPForm(instance=confirmacao)

    return render(request, 'evento/rsvp.html', {'form': form, 'convidado': convidado})


"""
Lista os convidados do evento.
O atendente pode editar os dados e confirmar manualmente.
Mostra um botão "Editar" ao lado do nome do convidado.

"""
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



"""
O convidado acessa um link e insere o CPF.
Se o CPF existir, ele pode confirmar presença.
Após confirmar, exibe uma mensagem de sucesso.
"""

def rsvp_convidado(request):
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        try:
            convidado = Convidado.objects.get(cpf=cpf)
            confirmacao, created = Confirmacao.objects.get_or_create(convidado=convidado)

            if request.POST.get('confirmar'):
                confirmacao.confirmado = True
                confirmacao.save()
                messages.success(request, "Presença confirmada com sucesso!")
                return redirect('rsvp_sucesso')
        except Convidado.DoesNotExist:
            messages.error(request, "CPF não encontrado. Verifique e tente novamente.")

    return render(request, 'evento/rsvp_convidado.html')



"""
Após após confirmações dos convidados
"""

def rsvp_sucesso(request):
    return render(request, 'evento/rsvp_sucesso.html')












def cadastrar_convidado(request):
    if request.method == 'POST':
        form = ConvidadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_eventos') 
    else:
        form = ConvidadoForm()
    return render(request, 'evento/cadastrar_convidado.html', {'form': form})


# importação de dados:

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