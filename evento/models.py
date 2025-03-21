from django.db import models

class Evento(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    data = models.DateTimeField()
    local = models.CharField(max_length=255)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
    

class Convidado(models.Model):
    nome = models.CharField(max_length=255)
    cpf = models.CharField(blank=False, null=False, unique=True, max_length=11)
    email = models.CharField(blank=False, null=False, unique=True, max_length=50)
    telefone = models.CharField(blank=True, null=True, max_length=11)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nome} ({self.email})"
    
class Confirmacao(models.Model):
    convidado = models.OneToOneField(Convidado, on_delete=models.CASCADE, null=True, blank=True)
    confirmado = models.BooleanField(default=False)
    restricoes_alimentares = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.convidado.nome} - {'Confirmado' if self.confirmado else 'Não Confirmado'}"
