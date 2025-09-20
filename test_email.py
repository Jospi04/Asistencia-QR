import os
from dotenv import load_dotenv
from datetime import datetime
from src.infrastructure.email_service import EmailService

# ✅ Cargar variables de entorno
load_dotenv()

def test_enviar_reportes_prueba():
    """Test para enviar reportes de prueba a djjhotamix@gmail.com"""
    print("\n" + "="*60)
    print("🚀 TEST: Enviar Reportes de Prueba a djjhotamix@gmail.com")
    print("="*60)
    
    email_service = EmailService()
    
    # ✅ Validar configuración
    if not email_service.email_user or not email_service.email_password:
        print("❌ ERROR: Configuración de correo incompleta")
        print("✅ Por favor, configura tu archivo .env con EMAIL_USER y EMAIL_PASSWORD")
        return False
    
    # ✅ Correo de destino (todos los correos irán a este correo)
    email_destino = "djjhotamix@gmail.com"
    print(f"📧 Todos los correos se enviarán a: {email_destino}")
    
    # ✅ 1. Enviar 3 correos a la dueña (uno por empresa)
    print("\n" + "="*50)
    print("📧 Enviando 3 correos a la dueña (uno por empresa)")
    print("="*50)
    
    empresas = ["Enti Max", "Enti Eirl", "Prentix"]
    for empresa in empresas:
        asunto = f"📊 Reporte Semanal de Asistencia - {empresa}"
        
        contenido = f"""
        <h2>📊 Reporte Semanal de Asistencia - {empresa}</h2>
        <p><strong>Período:</strong> {datetime.now().strftime('%d/%m/%Y')} (últimos 7 días)</p>
        <hr>
        <h3>✅ EMPLEADOS CON TARDANZAS:</h3>
        <ul>
            <li><strong>Joseph</strong>: 4 tardanza(s) → ¡Atención!</li>
            <li><strong>Pedro</strong>: 2 tardanza(s) → En observación</li>
        </ul>
        <h3>✅ EMPLEADOS CON FALTAS:</h3>
        <ul>
            <li><strong>Luis</strong>: 3 falta(s) → ¡Urgente!</li>
            <li><strong>Ana</strong>: 1 falta(s) → Leve</li>
        </ul>
        <h3>✅ EMPLEADOS SIN INCIDENCIAS:</h3>
        <p>Carlos, Rosa, Juan</p>
        <hr>
        <p>Por favor, revisa con el equipo para mejorar la puntualidad.</p>
        <p>¡Gracias por tu liderazgo Jacque!</p>
        <p><em>Este reporte se genera automáticamente cada semana.</em></p>
        """
        
        print(f"Enviando reporte de {empresa} a {email_destino}...")
        exito = email_service.enviar_correo(
            destinatario=email_destino,
            asunto=asunto,
            mensaje_html=contenido
        )
        
        if exito:
            print(f"✅ ¡Reporte de {empresa} enviado con éxito!")
        else:
            print(f"❌ Error al enviar reporte de {empresa}")
    
    # ✅ 2. Enviar 1 correo al empleado (tú)
    print("\n" + "="*50)
    print("📧 Enviando 1 correo al empleado (tú)")
    print("="*50)
    
    asunto_empleado = f"📊 Tu Reporte Semanal de Asistencia - {datetime.now().strftime('%d/%m/%Y')}"
    
    contenido_empleado = f"""
    <h2>📊 Tu Reporte Semanal de Asistencia</h2>
    <p><strong>Hola Joseph</strong>,</p>
    <p>Este es tu resumen de asistencia de la semana pasada:</p>
    <hr>
    <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 8px; margin: 15px 0;">
        <p style="margin: 0; font-size: 16px;">
            <strong>🚨 Faltas:</strong> 2 día(s) sin registrar asistencia.
        </p>
    </div>
    <div style="background-color: #e3f2fd; border: 1px solid #2196f3; padding: 15px; border-radius: 8px; margin: 15px 0;">
        <p style="margin: 0; font-size: 16px;">
            <strong>⏰ Tardanzas:</strong> Llegaste tarde 3 vez/veces.
        </p>
    </div>
    <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 8px; margin: 15px 0;">
        <p style="margin: 0; font-size: 16px;">
            <strong>📋 Recomendación:</strong> Por favor, regulariza tu asistencia para evitar sanciones.
        </p>
    </div>
    <hr>
    <p>Este reporte se genera automáticamente cada semana.</p>
    <p>¡Gracias por tu compromiso!</p>
    """
    
    print(f"Enviando reporte al empleado a {email_destino}...")
    exito_empleado = email_service.enviar_correo(
        destinatario=email_destino,
        asunto=asunto_empleado,
        mensaje_html=contenido_empleado
    )
    
    if exito_empleado:
        print("✅ ¡Reporte al empleado enviado con éxito!")
    else:
        print("❌ Error al enviar reporte al empleado")
    
    print("\n" + "="*60)
    print("🎉 ¡Todos los tests completados!")
    print("="*60)

if __name__ == "__main__":
    test_enviar_reportes_prueba()