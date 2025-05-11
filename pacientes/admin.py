from django.contrib import admin
from .models import Paciente, Consulta

admin.site.register(Paciente)
admin.site.register(Consulta)  # ✅ Corregido
