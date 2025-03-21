from django.shortcuts import render, get_object_or_404, redirect
from .models import Evento, Convidado, Confirmacao
from .forms import RSVPForm, ConvidadoForm



def home(request):
    return render(request, 'evento/home.html')




def lista_eventos(request):
    eventos = Evento.objects.all()
    return render(request, 'evento/lista_eventos.html', {'eventos': eventos})

def detalhes_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    convidados = Convidado.objects.filter(evento=evento)
    return render(request, 'evento/detalhes_evento.html', {'evento': evento, 'convidados': convidados})



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



def cadastrar_convidado(request):
    if request.method == 'POST':
        form = ConvidadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_eventos') 
    else:
        form = ConvidadoForm()
    return render(request, 'evento/cadastrar_convidado.html', {'form': form})

