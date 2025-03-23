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
    cpf = models.CharField(blank=False, null=False, unique=True, max_length=11)
    email = models.CharField(blank=False, null=False, unique=True, max_length=50)
    telefone = models.CharField(blank=True, null=True, max_length=11)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    qrcode = models.ImageField(upload_to='convidados_qrcodes/', null=True, blank=True)

    def __str__(self):
        return f"{self.nome} ({self.email})"
    
    def generate_qrcode(self):
        # Gerar QR Code com base no CPF
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(self.cpf)
        qr.make(fit=True)

        # Criar a imagem do QR Code
        img = qr.make_image(fill='black', back_color='white')

        # Salvar imagem em formato de arquivo
        qr_file = BytesIO()
        img.save(qr_file, 'PNG')
        qr_file.seek(0)

        # Salvar a imagem no campo ImageField
        self.qrcode.save(f"{self.cpf}_qrcode.png", ContentFile(qr_file.read()), save=False)
        qr_file.close()
    

    
class Confirmacao(models.Model):
    convidado = models.OneToOneField(Convidado, on_delete=models.CASCADE, null=True, blank=True)
    confirmado = models.BooleanField(default=False)
    restricoes_alimentares = models.TextField(blank=True, null=True)
    

    def __str__(self):
        return f"{self.convidado.nome} - {'Confirmado' if self.confirmado else 'Não Confirmado'}"

