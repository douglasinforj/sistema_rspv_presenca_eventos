from django.urls import path
from . import views


urlpatterns = [
    path('', views.lista_eventos, name='lista_eventos'),
    path('detalhes_evento/<int:evento_id>/', views.detalhes_eventos, name='detalhes_eventos'),
]
