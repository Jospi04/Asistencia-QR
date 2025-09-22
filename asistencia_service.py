# asistencia_service.py
import win32serviceutil
import win32service
import win32event
import win32evtlogutil
import os
import sys
import subprocess
from pathlib import Path

class AsistenciaQRService(win32serviceutil.ServiceFramework):
    _svc_name_ = "AsistenciaQR"
    _svc_display_name_ = "Sistema de Asistencia QR"
    _svc_description_ = "Servicio para el sistema de asistencia por QR"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.process = None

    def SvcDoRun(self):
        # Ruta al entorno virtual o Python
        python_exe = sys.executable
        
        # Ruta a tu proyecto
        project_path = r"C:\Users\piero\Documents\Asistencia QR"  # CAMBIA ESTA RUTA
        
        # Archivo WSGI
        wsgi_script = os.path.join(project_path, "wsgi.py")

        # Comando para ejecutar con waitress
        cmd = [
            python_exe,
            "-c",
            f"import sys; sys.path.insert(0, '{project_path}'); from wsgi import app; from waitress import serve; serve(app, host='0.0.0.0', port=5000)"
        ]

        # Cambiar al directorio del proyecto
        os.chdir(project_path)

        # Ejecutar el servidor
        self.process = subprocess.Popen(cmd)

        # Esperar a que se detenga
        self.process.wait()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.process:
            self.process.terminate()
            self.process.wait()
        win32event.SetEvent(self.hWaitStop)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AsistenciaQRService)