from rest_framework import serializers
from .models import Consulta, Paciente
from datetime import date

# Serializer para tratamiento individual (nombre y posología)
class TratamientoSerializer(serializers.Serializer):
    nombre = serializers.CharField()
    posologia = serializers.CharField()

# Serializer para crear una consulta junto con un paciente nuevo
class PacienteConConsultaSerializer(serializers.Serializer):
    nombre = serializers.CharField()
    fecha_nacimiento = serializers.DateField()
    telefono = serializers.CharField()
    correo = serializers.EmailField()
    motivo = serializers.CharField()
    diagnostico = serializers.CharField()
    tratamiento = TratamientoSerializer(many=True)

# Serializer para mostrar los detalles de una consulta
class ConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consulta
        fields = '__all__'
        extra_kwargs = {
            'peso': {'required': False, 'allow_null': True},
            'talla': {'required': False, 'allow_null': True},
            'imc': {'required': False, 'allow_null': True},
            'frecuencia_cardiaca': {'required': False, 'allow_null': True},
            'frecuencia_respiratoria': {'required': False, 'allow_null': True},
            'presion_arterial': {'required': False, 'allow_null': True},
            'glucometria': {'required': False, 'allow_null': True},
            'oximetria': {'required': False, 'allow_null': True},
            'tratamiento': {'required': False, 'allow_null': True},
            'antecedentes': {'required': False, 'allow_null': True},
        }

    def get_edad_paciente(self, obj):
        if obj.paciente and obj.paciente.fecha_nacimiento:
            hoy = date.today()
            nacimiento = obj.paciente.fecha_nacimiento
            edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
            return edad
        return None

    def validate(self, data):
        peso = data.get('peso')
        talla_cm = data.get('talla')

        if peso and talla_cm and peso > 0 and talla_cm > 0:
            talla_m = talla_cm / 100
            imc = round(peso / (talla_m * talla_m), 2)
            data['imc'] = imc

        return data



# Serializer clásico para listar pacientes
class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'
