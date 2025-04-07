from django.db import models


import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

class Evento(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    data = models.DateTimeField()
    local = models.CharField(max_length=255)
    imagem = models.ImageField(upload_to='eventos/', blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
    

class Convidado(models.Model):
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=11)
    email = models.EmailField(unique=True, max_length=50)
    telefone = models.CharField(blank=True, null=True, max_length=15)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    qrcode = models.ImageField(upload_to='convidados_qrcodes/', null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cpf', 'evento'], name='unique_cpf_evento')
        ]

    def __str__(self):
        return f"{self.nome} ({self.email})"

    def generate_qrcode(self, force_update=False):
        """Gera o QR Code baseado no CPF e ID do Evento."""
        if self.qrcode and not force_update:
            return                                # Evita reprocessamento se já existir

        qr_data = f"{self.cpf}_{self.evento.id}"  # Inclui ID do evento para diferenciação
        qr = qrcode.make(qr_data)                 # Gera QR Code

        qr_file = BytesIO()
        qr.save(qr_file, format='PNG')

        # Nome do arquivo inclui CPF e ID do evento para evitar duplicidade
        file_name = f"{self.cpf}_{self.evento.id}.png"
        self.qrcode.save(file_name, ContentFile(qr_file.getvalue()), save=True)
        qr_file.close()
    

    
class Confirmacao(models.Model):
    convidado = models.OneToOneField(Convidado, on_delete=models.CASCADE, null=True, blank=True)
    confirmado = models.BooleanField(default=False)
    restricoes_alimentares = models.TextField(blank=True, null=True)
    entrou = models.BooleanField(default=False)  #campo de check-in
    

    def __str__(self):
        return f"{self.convidado.nome} - {'Confirmado' if self.confirmado else 'Não Confirmado'}"

