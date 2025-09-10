from datetime import datetime, time
from src.infrastructure.email_service import EmailService
from src.domain.entities import Empleado, Asistencia
from src.domain.repositories import (
    EmpleadoRepository, 
    AsistenciaRepository, 
    HorarioEstandarRepository,
    EscaneoTrackingRepository
)
from src.infrastructure.mysql_connection import MySQLConnection
from typing import Optional

class MarkAttendanceUseCase:
    def __init__(self, 
                 empleado_repository: EmpleadoRepository,
                 asistencia_repository: AsistenciaRepository,
                 horario_repository: HorarioEstandarRepository,
                 escaneo_repository: EscaneoTrackingRepository):
        self.empleado_repository = empleado_repository
        self.asistencia_repository = asistencia_repository
        self.horario_repository = horario_repository
        self.escaneo_repository = escaneo_repository
        self.email_service = EmailService()
        self.db = MySQLConnection()  # Conexión MySQL lista para usar
    
    def execute(self, codigo_qr: str, ip_address: str = "") -> dict:
        try:
            # Evitar duplicados
            if self.escaneo_repository.existe_registro_reciente(codigo_qr, 10):
                return {"status": "duplicado", "message": "Código QR escaneado recientemente", "data": None}

            self.escaneo_repository.create(codigo_qr, ip_address)
            
            empleado = self.empleado_repository.get_by_codigo_qr(codigo_qr)
            if not empleado and codigo_qr.startswith("EMP_"):
                try:
                    parts = codigo_qr.split("_")
                    if len(parts) >= 3:
                        empleado_id = int(parts[2])
                        empleado = self.empleado_repository.get_by_id(empleado_id)
                except (ValueError, IndexError):
                    pass
            if not empleado:
                return {"status": "error", "message": "Empleado no encontrado", "data": None}

            fecha_actual = datetime.now().date().strftime('%Y-%m-%d')
            hora_actual = datetime.now().time()
            
            asistencia = self.asistencia_repository.get_by_empleado_and_fecha(empleado.id, fecha_actual)
            if not asistencia:
                asistencia = Asistencia(empleado_id=empleado.id, fecha=fecha_actual)
            
            resultado = self._procesar_registro_horario(asistencia, hora_actual)
            if resultado["actualizado"]:
                if asistencia.id:
                    self.asistencia_repository.update(asistencia)
                else:
                    self.asistencia_repository.create(asistencia)
                self._calcular_horas_trabajadas(asistencia)
                self.asistencia_repository.update(asistencia)
            
            self.verificar_y_enviar_alertas_faltas(empleado.id)

            return {
                "status": "success",
                "message": resultado["mensaje"],
                "data": {
                    "empleado": {"id": empleado.id, "nombre": empleado.nombre},
                    "asistencia": {
                        "fecha": asistencia.fecha,
                        "entrada_manana": str(asistencia.entrada_manana_real) if asistencia.entrada_manana_real else None,
                        "salida_manana": str(asistencia.salida_manana_real) if asistencia.salida_manana_real else None,
                        "entrada_tarde": str(asistencia.entrada_tarde_real) if asistencia.entrada_tarde_real else None,
                        "salida_tarde": str(asistencia.salida_tarde_real) if asistencia.salida_tarde_real else None
                    }
                }
            }

        except Exception as e:
            print(f"❌ Error ejecutando marca de asistencia: {e}")
            return {"status": "error", "message": "Error inesperado registrando asistencia", "data": None}

    # ------------------ MÉTODOS DE HORARIO Y HORAS ------------------
    def _procesar_registro_horario(self, asistencia: Asistencia, hora_actual: time) -> dict:
        try:
            if not asistencia.entrada_manana_real:
                asistencia.entrada_manana_real = hora_actual
                return {"actualizado": True, "mensaje": f"Entrada mañana registrada: {hora_actual}"}
            elif not asistencia.salida_manana_real:
                asistencia.salida_manana_real = hora_actual
                return {"actualizado": True, "mensaje": f"Salida mañana registrada: {hora_actual}"}
            elif not asistencia.entrada_tarde_real:
                asistencia.entrada_tarde_real = hora_actual
                return {"actualizado": True, "mensaje": f"Entrada tarde registrada: {hora_actual}"}
            elif not asistencia.salida_tarde_real:
                asistencia.salida_tarde_real = hora_actual
                return {"actualizado": True, "mensaje": f"Salida tarde registrada: {hora_actual}"}
            else:
                return {"actualizado": False, "mensaje": "Todos los registros del día completos"}
        except Exception as e:
            print(f"❌ Error procesando horario: {e}")
            return {"actualizado": False, "mensaje": "Error procesando horario"}

    def _calcular_horas_trabajadas(self, asistencia: Asistencia):
        try:
            total_minutos = 0
            if asistencia.entrada_manana_real and asistencia.salida_manana_real:
                total_minutos += self._calcular_minutos_entre_horas(asistencia.entrada_manana_real, asistencia.salida_manana_real)
            if asistencia.entrada_tarde_real and asistencia.salida_tarde_real:
                total_minutos += self._calcular_minutos_entre_horas(asistencia.entrada_tarde_real, asistencia.salida_tarde_real)
            
            total_horas = total_minutos / 60.0
            asistencia.total_horas_trabajadas = round(total_horas, 2)
            horas_normales = 8.0
            if total_horas > horas_normales:
                asistencia.horas_normales = horas_normales
                asistencia.horas_extras = round(total_horas - horas_normales, 2)
            else:
                asistencia.horas_normales = round(total_horas, 2)
                asistencia.horas_extras = 0.0
            asistencia.estado_dia = "COMPLETO" if total_minutos > 0 and total_horas >= 8 else ("INCOMPLETO" if total_minutos > 0 else "FALTA")
        except Exception as e:
            print(f"❌ Error calculando horas trabajadas: {e}")

    def _calcular_minutos_entre_horas(self, hora_inicio: time, hora_fin: time) -> int:
        try:
            return max(0, (hora_fin.hour*60 + hora_fin.minute) - (hora_inicio.hour*60 + hora_inicio.minute))
        except Exception as e:
            print(f"❌ Error calculando minutos entre horas: {e}")
            return 0

    # ------------------ ALERTAS ------------------
    def verificar_y_enviar_alertas_faltas(self, empleado_id: int):
        try:
            empleado = self.empleado_repository.get_by_id(empleado_id)
            if not empleado or not empleado.correo:
                return False
            faltas = self._contar_faltas_recientes(empleado_id)
            if faltas >= 4 and not self._alerta_ya_enviada(empleado_id, faltas):
                from src.infrastructure.repositories_mysql import EmpresaRepositoryMySQL
                empresa_repo = EmpresaRepositoryMySQL(self.db)
                empresa = empresa_repo.get_by_id(empleado.empresa_id) if hasattr(empresa_repo, 'get_by_id') else None
                nombre_empresa = empresa.nombre if empresa else "Empresa"
                
                exito = self.email_service.enviar_alerta_faltas(
                    nombre_empleado=empleado.nombre,
                    email_empleado=empleado.correo,
                    numero_faltas=faltas,
                    empresa_nombre=nombre_empresa
                )
                if exito:
                    self._registrar_alerta_enviada(empleado_id, faltas)
                    return True
            return False
        except Exception as e:
            print(f"❌ Error verificando alertas: {e}")
            return False

    def _contar_faltas_recientes(self, empleado_id: int, dias: int = 30) -> int:
        try:
            query = """
                SELECT COUNT(*) as total
                FROM asistencia
                WHERE empleado_id = %s 
                  AND fecha >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                  AND estado_dia = 'FALTA'
            """
            result = self.db.execute_query(query, (empleado_id, dias))
            return result[0]['total'] if result else 0
        except Exception as e:
            print(f"❌ Error contando faltas: {e}")
            return 0

    def _alerta_ya_enviada(self, empleado_id: int, numero_faltas: int) -> bool:
        try:
            query = "SELECT 1 FROM alertas_enviadas WHERE empleado_id=%s AND numero_faltas=%s LIMIT 1"
            result = self.db.execute_query(query, (empleado_id, numero_faltas))
            return bool(result)
        except Exception as e:
            print(f"❌ Error verificando alerta: {e}")
            return False

    def _registrar_alerta_enviada(self, empleado_id: int, numero_faltas: int):
        try:
            query = "INSERT INTO alertas_enviadas (empleado_id, numero_faltas) VALUES (%s, %s)"
            last_id = self.db.execute_insert(query, (empleado_id, numero_faltas))
            if last_id:
                print(f"✅ Alerta registrada para empleado {empleado_id} con {numero_faltas} faltas")
            else:
                print(f"❌ No se pudo registrar la alerta para empleado {empleado_id}")
        except Exception as e:
            print(f"❌ Error registrando alerta: {e}")
