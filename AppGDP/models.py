from django.db import models

    
class Senai(models.Model):
    titulo = models.CharField(max_length=50)
    descricao = models.TextField(max_length=1500)
    logo = models.ImageField(upload_to='logo/')

    def __str__(self):
        return self.titulo
    


class Inventario(models.Model):
    num_inventario = models.CharField(max_length=10, unique=True)
    denominacao = models.CharField(max_length=255)
    localizacao = models.CharField(max_length=10)
    link_imagem = models.URLField(max_length=500, blank=True, null=True) 
    sala = models.CharField(max_length=30, blank=True, null=True)
    responsavel = models.ForeignKey(
        'Sala',  # Usando string literal para evitar o erro
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        to_field='responsavel'
    )

    def __str__(self):
        return f"{self.num_inventario} - {self.denominacao}"
    

class Sala(models.Model):
    sala = models.CharField(max_length=30, unique=True)
    descricao = models.TextField(max_length=1500)
    localizacao = models.CharField(max_length=10)
    link_imagem = models.URLField(max_length=500, blank=True, null=True)
    responsavel = models.CharField(max_length=50, unique=True)
    quantidade_itens = models.IntegerField(default=0)
    email_responsavel = models.EmailField(max_length=100, blank=True, null=True)
    

    def __str__(self):
        return self.sala
