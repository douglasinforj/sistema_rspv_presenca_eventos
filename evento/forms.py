from django import forms 
from .models import Confirmacao

class RSVPForm(forms.modelsForm):
    class Meta:
        model = Confirmacao
        fields = ['confirmado', 'restricoes_alimentares']