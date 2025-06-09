from django import forms 
from .models import Confirmacao, Convidado, Evento
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

class RSVPForm(forms.ModelForm):
    class Meta:
        model = Confirmacao
        fields = ['confirmado']


class ConvidadoForm(forms.Form):
    nome = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Digite o nome', 'class': 'form-control'})
    )
    cpf = forms.CharField(
        max_length=11,
        widget=forms.TextInput(attrs={'placeholder': 'Digite o CPF (somente números)', 'class': 'form-control'})
    )
    email = forms.EmailField(
        max_length=50,
        widget=forms.EmailInput(attrs={'placeholder': 'Digite o e-mail', 'class': 'form-control'})
    )
    telefone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Digite o telefone (opcional)', 'class': 'form-control'})
    )
    eventos = forms.ModelMultipleChoiceField(
        queryset=Evento.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True
    )

    def clean_cpf(self):
        cpf = self.cleaned_data['cpf'].replace('.', '').replace('-', '')
        if not cpf.isdigit() or len(cpf) != 11:
            raise forms.ValidationError('CPF deve conter exatamente 11 dígitos numéricos.')
        return cpf

    def clean(self):
        cleaned_data = super().clean()
        cpf = cleaned_data.get('cpf')
        eventos = cleaned_data.get('eventos')
        if eventos:
            logger.debug(f"Eventos recebidos no formulário: {[evento.nome for evento in eventos]}")
        if cpf and eventos:
            for evento in eventos:
                if Convidado.objects.filter(cpf=cpf, evento=evento).exists():
                    raise forms.ValidationError(f'O CPF {cpf} já está cadastrado no evento {evento.nome}.')
        return cleaned_data





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