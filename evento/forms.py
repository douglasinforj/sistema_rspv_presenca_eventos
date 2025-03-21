from django import forms 
from .models import Confirmacao, Convidado

class RSVPForm(forms.ModelForm):
    class Meta:
        model = Confirmacao
        fields = ['confirmado', 'restricoes_alimentares']


class ConvidadoForm(forms.ModelForm):
    class Meta:
        model = Convidado 
        fields = ['nome', 'cpf','email', 'evento']