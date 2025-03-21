from django.shortcuts import render, get_object_or_404, redirect
from .models import Evento, Convidado, Confirmacao
from .forms import RSVPForm

def lista_eventos(request):
    eventos = Evento.objects.all()
    return render(request, 'evento/lista_eventos.html', {'eventos': eventos})

def detalhes_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    convidados = Convidado.objects.filter(evento=evento)
    return render(request, 'evento/detalhes_evento.html', {'evento': evento, 'convidados': convidados})

