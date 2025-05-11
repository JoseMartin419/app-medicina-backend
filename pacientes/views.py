from rest_framework.generics import ListCreateAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Paciente, Consulta
from .serializers import PacienteSerializer, ConsultaSerializer
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.generics import RetrieveAPIView
from datetime import date
from django.conf import settings
import os
from django.templatetags.static import static
from rest_framework.decorators import api_view

@api_view(['GET'])
def obtener_consultas(request):
    consultas = Consulta.objects.all().order_by('-fecha')
    serializer = ConsultaSerializer(consultas, many=True)
    return Response(serializer.data)



class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer


class PacienteRetrieveView(RetrieveAPIView):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer

class PacienteListCreateView(ListCreateAPIView):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer

class ConsultaCreateView(CreateAPIView):
    queryset = Consulta.objects.all()
    serializer_class = ConsultaSerializer

 
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            consulta = serializer.save()
            receta_url = f"/api/recetas/{consulta.id}/"
            return Response({
                "mensaje": "Consulta guardada correctamente",
                "consulta_id": consulta.id,
                "url_receta": receta_url
            }, status=status.HTTP_201_CREATED)
        else:
            print("❌ Errores de validación:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConsultaRetrieveView(APIView):
    def get(self, request, consulta_id):
        consulta = get_object_or_404(Consulta, id=consulta_id)
        serializer = ConsultaSerializer(consulta)
        return Response(serializer.data, status=status.HTTP_200_OK)

class HistorialPorPaciente(APIView):
    def get(self, request, paciente_id):
        consultas = Consulta.objects.filter(paciente__id=paciente_id).order_by('-fecha')
        serializer = ConsultaSerializer(consultas, many=True)
        return Response(serializer.data)


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from django.http import HttpResponse
from .models import Consulta
from datetime import date

def calcular_edad(fecha_nacimiento):
    hoy = date.today()
    return hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

def generar_receta_pdf(request, consulta_id):
    consulta = Consulta.objects.get(id=consulta_id)
    paciente = consulta.paciente
    edad = calcular_edad(paciente.fecha_nacimiento)

    # Colores
    azul_oscuro = HexColor("#1E3A8A")
    gris_claro = HexColor("#F9FAFB")
    gris_texto = HexColor("#374151")
    gris_linea = HexColor("#9CA3AF")

    # Crear PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="receta_profesional.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    def dibujar_receta(y_start, c):
        # Fondo
        p.setFillColor(gris_claro)
        p.roundRect(40, y_start - 320, width - 80, 250, 12, stroke=0, fill=1)

        # Encabezado
        p.setFillColor(azul_oscuro)
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, y_start, "Consultorio Médico Gondur")

        p.setFont("Helvetica-Bold", 11)
        p.drawCentredString(width / 2, y_start - 20, "Dr. José Martín González Durán")
        p.setFont("Helvetica", 9)
        p.drawCentredString(width / 2, y_start - 34, "Cédula Profesional: 12345678    •    U.A.N.L.")
        p.drawRightString(width - 50, y_start - 10, f"Fecha: {c.fecha.strftime('%d/%m/%Y')}")

        # Datos del paciente
        p.setFillColor(gris_texto)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(55, y_start - 60, "Nombre:")
        p.setFont("Helvetica", 10)
        p.drawString(110, y_start - 60, paciente.nombre)

        p.setFont("Helvetica-Bold", 10)
        p.drawString(350, y_start - 60, "Edad:")
        p.setFont("Helvetica", 10)
        p.drawString(390, y_start - 60, f"{edad} años")

        p.setFont("Helvetica-Bold", 10)
        p.drawString(450, y_start - 60, "Nacimiento:")
        p.setFont("Helvetica", 10)
        p.drawString(525, y_start - 60, paciente.fecha_nacimiento.strftime('%d/%m/%Y'))

        p.setFont("Helvetica-Bold", 10)
        p.drawString(55, y_start - 80, "Antecedentes:")
        p.setFont("Helvetica", 10)
        p.drawString(140, y_start - 80, c.antecedentes)

        # Tratamiento
        p.setFont("Helvetica-Bold", 11)
        p.setFillColor(azul_oscuro)
        p.drawString(55, y_start - 105, "Tratamiento:")

        y = y_start - 120
        for i, item in enumerate(c.tratamiento):
            p.setFont("Helvetica-Bold", 10)
            p.setFillColor(gris_texto)
            p.drawString(65, y, f"{i+1}. {item['nombre']}")
            p.setStrokeColor(gris_linea)
            p.line(60, y - 2, 360, y - 2)
            p.setFont("Helvetica-Oblique", 9)
            p.setFillColor(HexColor("#6B7280"))
            p.drawString(80, y - 12, item['posologia'])
            y -= 28

        # Signos vitales (solo los que están llenos)
        signos_y = y_start - 110  # Posición inicial fija arriba a la derecha
        p.setFont("Helvetica-Bold", 11)
        p.setFillColor(azul_oscuro)
        p.drawString(430, signos_y, "Signos vitales:")

        p.setFont("Helvetica", 9)
        p.setFillColor(gris_texto)

        signos = []
        if c.presion_arterial:
            signos.append(f"T/A: {c.presion_arterial}")
        if c.frecuencia_cardiaca:
            signos.append(f"FC: {c.frecuencia_cardiaca}")
        if c.frecuencia_respiratoria:
            signos.append(f"FR: {c.frecuencia_respiratoria}")
        if c.glucometria:
            signos.append(f"Gluco: {c.glucometria}")
        if c.oximetria:
            signos.append(f"Sat O2: {c.oximetria}")
        if c.peso:
            signos.append(f"Peso: {c.peso} kg")
        if c.talla:
            signos.append(f"Talla: {c.talla} m")
        if c.imc:
            signos.append(f"IMC: {c.imc}")

        y_actual = signos_y - 15
        for signo in signos:
            p.drawString(430, y_actual, signo)
            y_actual -= 15


        # Dibuja la línea primero
        firma_y = y_start - 290  # o el valor que desees para la altura

        # Dibuja la línea primero
        p.line(width - 200, firma_y, width - 60, firma_y)

        # Dibuja el texto unos 12 puntos debajo de la línea
        p.drawRightString(width - 60, firma_y - 12, "Firma del médico")


    # Parte superior
    dibujar_receta(763, consulta)

    # Línea punteada divisoria
    p.setDash(1, 3)
    p.line(40, height / 2, width - 40, height / 2)
    p.setDash()

    # Parte inferior (duplicada)
    dibujar_receta(360, consulta)

    p.showPage()
    p.save()
    return response
