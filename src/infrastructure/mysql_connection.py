import mysql.connector
from mysql.connector import Error
import os
from typing import Optional

class MySQLConnection:
    def __init__(self):
        # Configuración específica para MySQL Workbench local
        self.host = os.getenv('DB_HOST', '127.0.0.1')  # Usar 127.0.0.1 en lugar de localhost
        self.port = os.getenv('DB_PORT', '3306')       # Puerto por defecto de MySQL
        self.database = os.getenv('DB_NAME', 'sistema_asistencia_qr')
        self.user = os.getenv('DB_USER', 'root')       # Usuario por defecto de Workbench
        self.password = os.getenv('DB_PASSWORD', 'joseph')   # Coloca aquí tu contraseña de MySQL
        self.connection = None
    
    def connect(self) -> Optional[mysql.connector.MySQLConnection]:
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,           # Agregado el puerto
                database=self.database,
                user=self.user,
                password=self.password,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                autocommit=True,
                # Configuraciones adicionales para mejor compatibilidad con Workbench
                use_unicode=True,
                auth_plugin='mysql_native_password'  # Plugin de autenticación común
            )
            if self.connection.is_connected():
                print(f"Conexión exitosa a MySQL Workbench - Base de datos: {self.database}")
                return self.connection
        except Error as e:
            print(f"Error al conectar a MySQL Workbench: {e}")
            print(f"Verifica que MySQL Server esté corriendo y las credenciales sean correctas")
            print(f"Credenciales usadas - Host: {self.host}:{self.port}, User: {self.user}, DB: {self.database}")
            return None
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexión a MySQL cerrada")
    
    def get_connection(self) -> Optional[mysql.connector.MySQLConnection]:
        if not self.connection or not self.connection.is_connected():
            return self.connect()
        return self.connection
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[list]:
        connection = self.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"Error ejecutando query: {e}")
            return None
    
    def execute_update(self, query: str, params: tuple = None) -> bool:
        connection = self.get_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error ejecutando update: {e}")
            connection.rollback()
            return False
    
    def execute_insert(self, query: str, params: tuple = None) -> Optional[int]:
        connection = self.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            connection.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
        except Error as e:
            print(f"Error ejecutando insert: {e}")
            connection.rollback()
            return None


# --- NUEVO: instancia global y función helper ---
_db_instance = MySQLConnection()

def get_connection() -> Optional[mysql.connector.MySQLConnection]:
    """Devuelve una conexión activa a la BD"""
    return _db_instance.get_connection()
