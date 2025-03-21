from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('eventos', views.lista_eventos, name='lista_eventos'),
    path('evento/<int:evento_id>/', views.detalhes_evento, name='detalhes_evento'),
    path('rsvp/<int:convidado_id>/', views.rsvp, name='rsvp'),
    path('cadastrar_convidado/', views.cadastrar_convidado, name='cadastrar_convidado'),
    path("importar_convidados/", views.importar_convidados, name="importar_convidados"),
]
