import os
from dotenv import load_dotenv
load_dotenv()

from src.infrastructure.email_service import EmailService

def test_email():
    print("📧 Probando sistema de correo...")
    
    # Verificar que las variables de entorno estén cargadas
    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')
    
    if not email_user or not email_password:
        print("❌ Error: No se encontraron las credenciales de correo en .env")
        return
    
    print(f"📧 Usando correo: {email_user}")
    
    email_service = EmailService()
    
    # Prueba de envío - se envía a tu mismo correo para probar
    exito = email_service.enviar_alerta_faltas(
        nombre_empleado="Juan Pérez",
        email_empleado=os.getenv('EMAIL_EMPRESA'),  # Te envía a ti mismo para probar
        numero_faltas=4,
        empresa_nombre="ENTI MAX"
    )
    
    if exito:
        print("✅ ¡Prueba exitosa! Revisa tu correo.")
    else:
        print("❌ Hubo un error en la prueba.")

if __name__ == "__main__":
    test_email()