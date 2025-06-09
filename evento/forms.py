from django import forms 
from .models import Confirmacao, Convidado, Evento

class RSVPForm(forms.ModelForm):
    class Meta:
        model = Confirmacao
        fields = ['confirmado']


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




class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['nome', 'descricao', 'data', 'local', 'imagem']  # Adicionando 'imagem'
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'data': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'local': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    imagem = forms.ImageField(
        required=False, 
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )  # Adicionando o campo de upload