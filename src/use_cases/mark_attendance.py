from datetime import datetime, time, timedelta
import math
from src.domain.entities import Empleado, Asistencia
from src.domain.repositories import (
    EmpleadoRepository, 
    AsistenciaRepository, 
    HorarioEstandarRepository,
    EscaneoTrackingRepository,
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
            # Calcular las horas trabajadas y estado por turnos
            self._calcular_horas_trabajadas(asistencia)

            # Guardar en BD con horas y estados calculados
            if asistencia.id:
                self.asistencia_repository.update(asistencia)
            else:
                self.asistencia_repository.create(asistencia)
        
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
        """
        Procesa el registro horario con lógica de turnos basada en la hora actual.
        - Solo permite registros de mañana antes de las 12:00 PM.
        - A partir de las 12:00 PM, solo permite registros de tarde.
        """
        # Definir límites de turnos
        hora_limite_mañana = time(12, 0)  # Hasta las 12:00 PM es "mañana"

        # Verificar si ya pasó el turno de mañana
        ya_es_tarde = hora_actual >= hora_limite_mañana

        # Lógica mejorada por orden y hora
        if not asistencia.entrada_manana_real and not ya_es_tarde:
            # Solo permite entrada mañana si aún no ha pasado el límite
            asistencia.entrada_manana_real = hora_actual
            return {"actualizado": True, "mensaje": f"✅ Entrada mañana registrada: {hora_actual.strftime('%H:%M')}"}

        elif not asistencia.salida_manana_real and asistencia.entrada_manana_real and not ya_es_tarde:
            # Permite salida mañana solo si hay entrada y aún no es tarde
            asistencia.salida_manana_real = hora_actual
            return {"actualizado": True, "mensaje": f"✅ Salida mañana registrada: {hora_actual.strftime('%H:%M')}"}

        elif not asistencia.entrada_tarde_real:
            # A partir de las 12:00, fuerza el registro en la tarde
            asistencia.entrada_tarde_real = hora_actual
            return {"actualizado": True, "mensaje": f"✅ Entrada tarde registrada: {hora_actual.strftime('%H:%M')}"}

        elif not asistencia.salida_tarde_real:
            asistencia.salida_tarde_real = hora_actual
            return {"actualizado": True, "mensaje": f"✅ Salida tarde registrada: {hora_actual.strftime('%H:%M')}"}

        else:
            return {
                "actualizado": False, 
                "mensaje": "❌ Todos los registros del día ya están completos"
            }
    
    def _calcular_horas_trabajadas(self, asistencia: Asistencia):
        # Determinar si asistió a cada turno (marcó entrada Y salida)
        asistencia.asistio_manana = (
            bool(asistencia.entrada_manana_real) and 
            bool(asistencia.salida_manana_real)
        )
        asistencia.asistio_tarde = (
            bool(asistencia.entrada_tarde_real) and 
            bool(asistencia.salida_tarde_real)
        )

        # Calcular horas solo si ambos registros están
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

        # Convertir a horas (solo para mostrar)
        total_horas = total_minutos / 60.0
        asistencia.total_horas_trabajadas = round(total_horas, 2)

        # Horas normales y extras — CALCULA CON MINUTOS, NO CON HORAS REDONDEADAS
        minutos_normales = 8 * 60  # 480 minutos
        if total_minutos > minutos_normales:
            minutos_extras = total_minutos - minutos_normales
            asistencia.horas_extras = round(minutos_extras / 60.0, 2)
            asistencia.horas_normales = 8.0
        else:
            asistencia.horas_normales = round(total_horas, 2)
            asistencia.horas_extras = 0.0

        # Estado del día
        if asistencia.asistio_manana and asistencia.asistio_tarde:
            asistencia.estado_dia = "COMPLETO"
        elif asistencia.asistio_manana or asistencia.asistio_tarde:
            asistencia.estado_dia = "INCOMPLETO"
        else:
            asistencia.estado_dia = "FALTA"

        # Evaluar tardanzas (SIN TOLERANCIA)
        self._evaluar_tardanzas(asistencia)
    
    def _evaluar_tardanzas(self, asistencia: Asistencia):
        # HORARIOS ESPERADOS SIN TOLERANCIA
        hora_entrada_manana_esperada = time(6, 50)  # 6:50 AM
        hora_entrada_tarde_esperada = time(13, 0)   # 1:00 PM

        # Comparar directamente sin tolerancia
        if asistencia.entrada_manana_real:
            asistencia.tardanza_manana = asistencia.entrada_manana_real > hora_entrada_manana_esperada
        else:
            asistencia.tardanza_manana = False

        if asistencia.entrada_tarde_real:
            asistencia.tardanza_tarde = asistencia.entrada_tarde_real > hora_entrada_tarde_esperada
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

            # Convertir a datetime con fecha actual
            inicio_dt = datetime.combine(hoy, hora_inicio)
            fin_dt = datetime.combine(hoy, hora_fin)

            diferencia = fin_dt - inicio_dt
            total_segundos = diferencia.total_seconds()

            # Redondear hacia arriba: 1 segundo = 1 minuto
            minutos_redondeados = int(total_segundos / 60)

            return max(0, int(minutos_redondeados))
        except Exception as e:
            print(f"❌ Error calculando minutos entre horas: {e}")
            return 0