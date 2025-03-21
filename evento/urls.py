from django.urls import path
from . import views


urlpatterns = [
    path('', views.lista_eventos, name='lista_eventos'),
    path('evento/<int:evento_id>/', views.detalhes_evento, name='detalhes_evento'),
    path('rsvp/<int:convidado>/', views.rsvp, name='rsvp'),
]
