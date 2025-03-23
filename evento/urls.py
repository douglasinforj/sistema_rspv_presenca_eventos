from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('eventos', views.lista_eventos, name='lista_eventos'),
    path('adicionar/', views.adicionar_evento, name='adicionar_evento'),
    
    path('evento/<int:evento_id>/', views.detalhes_evento, name='detalhes_evento'),
    
    #TODO: vai ser preciso retirar não vai fazer sentido
    path('rsvp/convidado/', views.rsvp_convidado, name='rsvp_convidado'),
    path('rsvp/atendente/<int:convidado_id>/', views.rsvp_atendente, name='rsvp_atendente'),
    path('rsvp/sucesso/', views.rsvp_sucesso, name='rsvp_sucesso'),

    path('rsvp/<int:convidado_id>/', views.rsvp, name='rsvp'),
    path('cadastrar_convidado/', views.cadastrar_convidado, name='cadastrar_convidado'),
    path("importar_convidados/", views.importar_convidados, name="importar_convidados"),




]
