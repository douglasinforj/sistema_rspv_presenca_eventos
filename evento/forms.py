from django import forms 
from .models import Confirmacao, Convidado

class RSVPForm(forms.ModelForm):
    class Meta:
        model = Confirmacao
        fields = ['confirmado', 'restricoes_alimentares']


class ConvidadoForm(forms.ModelForm):
    class Meta:
        model = Convidado 
        fields = ['nome', 'cpf','email', 'telefone', 'evento']

        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'evento': forms.Select(attrs={'class': 'form-control'}),
        }


class UploadFileForm(forms.Form):
    file = forms.FileField(label="Selecione um aqruivo CSV ou Excel")