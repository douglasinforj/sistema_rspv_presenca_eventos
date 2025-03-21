from django.shortcuts import render, get_object_or_404, redirect
from .models import Evento, Convidado, Confirmacao
from .forms import RSVPForm

def lista_eventos(request):
    eventos = Evento.objects.all()
    return render(render, 'evento/lista_eventos.html')



