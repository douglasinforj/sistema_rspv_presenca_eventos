from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('eventos', views.lista_eventos, name='lista_eventos'),
    path('adicionar/', views.adicionar_evento, name='adicionar_evento'),
    
    path('evento/<int:evento_id>/', views.detalhes_evento, name='detalhes_evento'),
    
    path('rsvp/convidado/', views.rsvp_convidado, name='rsvp_convidado'),
    path('rsvp/atendente/<int:convidado_id>/', views.rsvp_atendente, name='rsvp_atendente'),
    path('rsvp/sucesso/', views.rsvp_sucesso, name='rsvp_sucesso'),

    #TODO:path('rsvp/<int:convidado_id>/', views.rsvp, name='rsvp'),
    path('cadastrar_convidado/', views.cadastrar_convidado, name='cadastrar_convidado'),
    path("importar_convidados/", views.importar_convidados, name="importar_convidados"),


    path("api/validar_qr_code/", views.validar_qr_code, name="validar_qr_code"),
    path("checkin/", views.checkin_view, name="checkin_view"),

    path("login/", views.login_view, name="login_view"),
    path("logout/", views.logout_view, name="logout_view"),

    path("relatorio/", views.relatorio_evento, name="relatorio_evento"),

]
