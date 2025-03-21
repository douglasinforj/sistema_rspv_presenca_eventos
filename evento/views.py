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

def rsvp(request, convidado_id):
    convidado = get_object_or_404(Convidado, id=convidado_id)
    if request.method == 'POST':
        form = RSVPForm(request.POST, instance=convidado.confirmacao)
        if form.is_valid():
            form.save()
            return redirect('detalhes_envido', evento_id=convidado.evneto.id)
        else:
            form = RSVPForm(instance=convidado.confirmacao)
        return render(request, 'evento/rsvp.html', {'form': form, 'convidado': convidado})
