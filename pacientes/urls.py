from django.urls import path
from .views import (
    PacienteListCreateView,
    ConsultaCreateView,
    HistorialPorPaciente,
    ConsultaRetrieveView,
    PacienteRetrieveView
)

urlpatterns = [
    path('', PacienteListCreateView.as_view(), name='lista-crea-pacientes'),
    path('<int:pk>/', PacienteRetrieveView.as_view(), name='detalle-paciente'),
    path('consultas/', ConsultaCreateView.as_view(), name='crear-consulta'),
    path('historial/<int:paciente_id>/', HistorialPorPaciente.as_view(), name='historial_por_paciente'),    path('consultas/<int:consulta_id>/', ConsultaRetrieveView.as_view(), name='ver-consulta'),
]
