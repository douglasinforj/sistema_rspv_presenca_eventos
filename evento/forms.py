from django import forms 
from .models import Confirmacao

class RSVPForm(forms.ModelForm):
    class Meta:
        model = Confirmacao
        fields = ['confirmado', 'restricoes_alimentares']