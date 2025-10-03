from app import mark_attendance_use_case
import os

print("📧 Correo de la dueña configurado:", os.getenv('EMAIL_EMPRESA'))
print("📧 Correo remitente:", os.getenv('EMAIL_USER'))
print("\n🚀 Enviando reportes de prueba...\n")

# Probar reporte a la dueña
mark_attendance_use_case.generar_reporte_semanal()

# Probar reportes a empleados (opcional)
# mark_attendance_use_case.enviar_reporte_individual_empleados()

print("\n✅ Prueba completada. Revisa el correo de Jaloyda@hotmail.com")