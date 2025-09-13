from datetime import datetime, time, timedelta
from src.infrastructure.email_service import EmailService
from src.domain.entities import Empleado, Asistencia
from src.domain.repositories import (
    EmpleadoRepository, 
    AsistenciaRepository, 
    HorarioEstandarRepository,
    EscaneoTrackingRepository
)
from src.infrastructure.mysql_connection import get_connection
from typing import Optional, Tuple


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
    
    def execute(self, codigo_qr: str, ip_address: str = "") -> dict:
        # Verificar si hay escaneo reciente
        if self.escaneo_repository.existe_registro_reciente(codigo_qr, 10):
            return {
                "status": "duplicado",
                "message": "Código QR escaneado recientemente",
                "data": None
            }
        
        self.escaneo_repository.create(codigo_qr, ip_address)
        empleado = None
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
            return {
                "status": "error",
                "message": "Empleado no encontrado",
                "data": None
            }
        
        fecha_actual = datetime.now().date().strftime('%Y-%m-%d')
        hora_actual = datetime.now().time()
        
        asistencia = self.asistencia_repository.get_by_empleado_and_fecha(
            empleado.id, fecha_actual
        )
        
        if not asistencia:
            asistencia = Asistencia(
                empleado_id=empleado.id,
                fecha=fecha_actual
            )
        
        resultado = self._procesar_registro_horario(asistencia, hora_actual)

        if resultado["actualizado"]:
            # ⚡ Primero calculo las horas trabajadas y estado por turnos
            self._calcular_horas_trabajadas(asistencia)

            # ⚡ Luego guardo en BD ya con horas y estados calculados
            if asistencia.id:
                self.asistencia_repository.update(asistencia)
            else:
                self.asistencia_repository.create(asistencia)
        
        self.verificar_y_enviar_alertas_faltas(empleado.id)
        
        return {
            "status": "success",
            "message": resultado["mensaje"],
            "data": {
                "empleado": {
                    "id": empleado.id,
                    "nombre": empleado.nombre
                },
                "asistencia": {
                    "fecha": asistencia.fecha,
                    "entrada_manana_real": str(asistencia.entrada_manana_real) if asistencia.entrada_manana_real else None,
                    "salida_manana_real": str(asistencia.salida_manana_real) if asistencia.salida_manana_real else None,
                    "entrada_tarde_real": str(asistencia.entrada_tarde_real) if asistencia.entrada_tarde_real else None,
                    "salida_tarde_real": str(asistencia.salida_tarde_real) if asistencia.salida_tarde_real else None,
                    "total_horas_trabajadas": asistencia.total_horas_trabajadas,
                    "horas_normales": asistencia.horas_normales,
                    "horas_extras": asistencia.horas_extras,
                    "estado_dia": asistencia.estado_dia,
                    "asistio_manana": asistencia.asistio_manana,
                    "asistio_tarde": asistencia.asistio_tarde,
                    "tardanza_manana": asistencia.tardanza_manana,
                    "tardanza_tarde": asistencia.tardanza_tarde
                }
            }
        }
    
    def _procesar_registro_horario(self, asistencia: Asistencia, hora_actual: time) -> dict:
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
    
    def _calcular_horas_trabajadas(self, asistencia: Asistencia):
        # ✅ Determinar si asistió a cada turno (marcó entrada Y salida)
        asistencia.asistio_manana = (
            bool(asistencia.entrada_manana_real) and 
            bool(asistencia.salida_manana_real)
        )
        asistencia.asistio_tarde = (
            bool(asistencia.entrada_tarde_real) and 
            bool(asistencia.salida_tarde_real)
        )

        # ✅ Calcular horas solo si ambos registros están
        total_minutos = 0
        if asistencia.entrada_manana_real and asistencia.salida_manana_real:
            minutos_manana = self._calcular_minutos_entre_horas(
                asistencia.entrada_manana_real, asistencia.salida_manana_real
            )
            total_minutos += minutos_manana
        if asistencia.entrada_tarde_real and asistencia.salida_tarde_real:
            minutos_tarde = self._calcular_minutos_entre_horas(
                asistencia.entrada_tarde_real, asistencia.salida_tarde_real
            )
            total_minutos += minutos_tarde

        total_horas = total_minutos / 60.0
        asistencia.total_horas_trabajadas = round(total_horas, 2)

        # ✅ Horas normales y extras
        horas_normales = 8.0
        if total_horas > horas_normales:
            asistencia.horas_extras = round(total_horas - horas_normales, 2)
            asistencia.horas_normales = horas_normales
        else:
            asistencia.horas_normales = round(total_horas, 2)
            asistencia.horas_extras = 0.0

        # ✅ Estado del día
        if asistencia.asistio_manana and asistencia.asistio_tarde:
            asistencia.estado_dia = "COMPLETO"
        elif asistencia.asistio_manana or asistencia.asistio_tarde:
            asistencia.estado_dia = "INCOMPLETO"
        else:
            asistencia.estado_dia = "FALTA"

        # ✅ Evaluar tardanzas (opcional, puedes ajustar horarios)
        self._evaluar_tardanzas(asistencia)
    
    def _evaluar_tardanzas(self, asistencia: Asistencia):
    # ⚙️ AJUSTA ESTOS HORARIOS SEGÚN TU EMPRESA
        hora_entrada_manana_esperada = time(6, 50)  # 6:50 AM
        tolerancia = timedelta(minutes=15)

    # Calcular hora límite mañana
        hoy = datetime.today().date()
        dt_entrada_esperada = datetime.combine(hoy, hora_entrada_manana_esperada)
        dt_limite_manana = dt_entrada_esperada + tolerancia
        hora_limite_manana = dt_limite_manana.time()

    # Verificar entrada mañana
        if asistencia.entrada_manana_real:
            asistencia.tardanza_manana = asistencia.entrada_manana_real > hora_limite_manana
        else:
            asistencia.tardanza_manana = False

    # Lo mismo para la tarde
        hora_entrada_tarde_esperada = time(13, 0)  # 1:00 PM
        dt_entrada_tarde_esperada = datetime.combine(hoy, hora_entrada_tarde_esperada)
        dt_limite_tarde = dt_entrada_tarde_esperada + tolerancia
        hora_limite_tarde = dt_limite_tarde.time()

        if asistencia.entrada_tarde_real:
            asistencia.tardanza_tarde = asistencia.entrada_tarde_real > hora_limite_tarde
        else:
            asistencia.tardanza_tarde = False

    def _calcular_minutos_entre_horas(self, hora_inicio, hora_fin) -> int:
        try:
            hoy = datetime.today().date()

            # Blindaje: convertir si llega como datetime
            if isinstance(hora_inicio, datetime):
                hora_inicio = hora_inicio.time()
            if isinstance(hora_fin, datetime):
                hora_fin = hora_fin.time()

            # Blindaje: si llega timedelta, ignoro
            if isinstance(hora_inicio, timedelta) or isinstance(hora_fin, timedelta):
                print("⚠️ Aviso: hora_inicio o hora_fin llegaron como timedelta, se ignora este cálculo.")
                return 0

            # Después:
# Truncar segundos a 0
            hora_inicio_truncada = time(hora_inicio.hour, hora_inicio.minute)
            hora_fin_truncada = time(hora_fin.hour, hora_fin.minute)

            inicio_dt = datetime.combine(hoy, hora_inicio_truncada)
            fin_dt = datetime.combine(hoy, hora_fin_truncada)

            diferencia = fin_dt - inicio_dt
            return max(0, int(diferencia.total_seconds() // 60))
        except Exception as e:
            print(f"❌ Error calculando minutos entre horas: {e}")
            return 0
    
    # ---------------- ALERTAS REALES -----------------
    
    def verificar_y_enviar_alertas_faltas(self, empleado_id: int):
        try:
            empleado = self.empleado_repository.get_by_id(empleado_id)
            if not empleado or not empleado.correo:
                return False
            faltas = self._contar_faltas_recientes(empleado_id, dias=30)
            if faltas >= 4 and not self._alerta_ya_enviada(empleado_id, faltas):
                from src.infrastructure.repositories_mysql import EmpresaRepositoryMySQL
                from src.infrastructure.mysql_connection import MySQLConnection
                
                db_connection = MySQLConnection()
                empresa_repo = EmpresaRepositoryMySQL(db_connection)
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
            print(f"Error verificando alertas: {e}")
            return False

    def _contar_faltas_recientes(self, empleado_id: int, dias: int = 30) -> int:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = """
                SELECT COUNT(*) 
                FROM asistencia
                WHERE empleado_id = %s 
                  AND fecha >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                  AND estado_dia = 'FALTA'
            """
            cursor.execute(query, (empleado_id, dias))
            resultado = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return resultado
        except Exception as e:
            print(f"Error contando faltas: {e}")
            return 0

    def _alerta_ya_enviada(self, empleado_id: int, numero_faltas: int) -> bool:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = """
                SELECT 1
                FROM alertas_enviadas
                WHERE empleado_id = %s AND numero_faltas = %s
                LIMIT 1
            """
            cursor.execute(query, (empleado_id, numero_faltas))
            existe = cursor.fetchone() is not None
            cursor.close()
            conn.close()
            return existe
        except Exception as e:
            print(f"Error verificando alerta: {e}")
            return False

    def _registrar_alerta_enviada(self, empleado_id: int, numero_faltas: int):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = """
                INSERT INTO alertas_enviadas (empleado_id, numero_faltas)
                VALUES (%s, %s)
            """
            cursor.execute(query, (empleado_id, numero_faltas))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"✅ Alerta registrada para empleado {empleado_id} con {numero_faltas} faltas")
        except Exception as e:
            print(f"Error registrando alerta: {e}")