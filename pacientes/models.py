from django.db import models
from datetime import date

class Paciente(models.Model):
    nombre = models.CharField(max_length=255)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre
    

    def edad(self):
        hoy = date.today()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )


def calcular_imc(peso, talla):
    try:
        return round(peso / (talla * talla), 2)
    except:
        return None

class Consulta(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    motivo = models.TextField()
    antecedentes = models.TextField(blank=True, null=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    talla = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    imc = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    frecuencia_cardiaca = models.IntegerField(blank=True, null=True)
    frecuencia_respiratoria = models.IntegerField(blank=True, null=True)
    presion_arterial = models.CharField(max_length=10, blank=True, null=True)
    glucometria = models.IntegerField(blank=True, null=True)
    oximetria = models.IntegerField(blank=True, null=True)
    diagnostico = models.TextField()
    tratamiento = models.JSONField()
    medico = models.CharField(max_length=100)
    fecha = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.peso and self.talla:
            try:
                self.imc = round(float(self.peso) / (float(self.talla) ** 2), 2)
            except ZeroDivisionError:
                self.imc = None
        super().save(*args, **kwargs)