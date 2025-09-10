from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import *

class EmpresaRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Empresa]:
        pass
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Empresa]:
        pass
    
    @abstractmethod
    def create(self, empresa: Empresa) -> Empresa:
        pass
    
    @abstractmethod
    def update(self, empresa: Empresa) -> Empresa:
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Elimina una empresa por su ID"""
        pass

class EmpleadoRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Empleado]:
        pass
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Empleado]:
        pass
    
    @abstractmethod
    def get_by_empresa_id(self, empresa_id: int) -> List[Empleado]:
        pass
    
    @abstractmethod
    def get_by_codigo_qr(self, codigo_qr: str) -> Optional[Empleado]:
        pass
    
    @abstractmethod
    def create(self, empleado: Empleado) -> Empleado:
        pass
    
    @abstractmethod
    def update(self, empleado: Empleado) -> Empleado:
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Elimina un empleado por su ID (eliminación completa de la base de datos)"""
        pass

class AsistenciaRepository(ABC):
    @abstractmethod
    def get_by_empleado_and_fecha(self, empleado_id: int, fecha: str) -> Optional[Asistencia]:
        pass
    
    @abstractmethod
    def get_by_fecha(self, fecha: str) -> List[Asistencia]:
        pass
    
    @abstractmethod
    def get_by_empleado_and_periodo(self, empleado_id: int, fecha_inicio: str, fecha_fin: str) -> List[Asistencia]:
        pass
    
    @abstractmethod
    def create(self, asistencia: Asistencia) -> Asistencia:
        pass
    
    @abstractmethod
    def update(self, asistencia: Asistencia) -> Asistencia:
        pass
    
    @abstractmethod
    def contar_faltas_empleado(self, empleado_id: int, dias: int = 30) -> int:
        """Cuenta las faltas de un empleado en los últimos X días"""
        pass
    
    @abstractmethod
    def alerta_ya_enviada(self, empleado_id: int, numero_faltas: int) -> bool:
        """Verifica si ya se envió alerta por este número de faltas"""
        pass
    
    @abstractmethod
    def registrar_alerta_enviada(self, empleado_id: int, numero_faltas: int) -> bool:
        """Registra que se envió una alerta"""
        pass

class HorarioEstandarRepository(ABC):
    @abstractmethod
    def get_by_empresa_id(self, empresa_id: int) -> Optional[HorarioEstandar]:
        pass
    
    @abstractmethod
    def create(self, horario: HorarioEstandar) -> HorarioEstandar:
        pass
    
    @abstractmethod
    def update(self, horario: HorarioEstandar) -> HorarioEstandar:
        pass

class EscaneoTrackingRepository(ABC):
    @abstractmethod
    def create(self, escaneo: EscaneoTracking) -> EscaneoTracking:
        pass
    
    @abstractmethod
    def existe_registro_reciente(self, codigo_qr: str, segundos: int) -> bool:
        pass

# from typing import List, Optional, Dict, Any
# from datetime import date

# class EmpresaRepository:
#     def list_all(self) -> List[Dict[str, Any]]:
#         raise NotImplementedError

# class EmpleadoRepository:
#     def create(self, empresa_id: int, nombre: str, dni: Optional[str]) -> int:
#         raise NotImplementedError
#     def update_qr(self, empleado_id: int, qr_filename: str) -> None:
#         raise NotImplementedError
#     def get_with_empresa(self, empleado_id: int) -> Optional[Dict[str, Any]]:
#         raise NotImplementedError
#     def list_by_empresa(self, empresa_id: Optional[int]) -> List[Dict[str, Any]]:
#         raise NotImplementedError

# class AsistenciaRepository:
#     def get_last_for_day(self, empleado_id: int, fecha: date) -> Optional[Dict]:
#         raise NotImplementedError
#     def create_entrada(self, empleado_id: int, fecha: date, hora: str) -> None:
#         raise NotImplementedError
#     def set_salida(self, asistencia_id: int, hora: str) -> None:
#         raise NotImplementedError
#     def report_by_empresa_and_range(self, empresa_id: int, desde: date, hasta: date) -> List[Dict]:
#         raise NotImplementedError
