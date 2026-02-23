# Sesion del Operador
class Sesion:
    _operador = None

    @classmethod
    def iniciar(cls, operador):
        """Inicia sesion con datos del operador"""
        cls._operador = operador

    @classmethod
    def cerrar(cls):
        """Cierra la sesion"""
        cls._operador = None

    @classmethod
    def operador_activo(cls):
        """Retorna todos los datos del operador"""
        return cls._operador

    @classmethod
    def numero_operador(cls):
        """Retorna el numero de operador formateado"""
        if cls._operador:
            return f"{cls._operador.get('numero_operador', 0):04d}"
        return "0000"

    @classmethod
    def nombre_operador(cls):
        """Retorna el nombre del operador"""
        return cls._operador.get("nombre", "Operador") if cls._operador else "Operador"

    @classmethod
    def nivel(cls):
        """Retorna el nivel de acceso"""
        return cls._operador.get("nivel", "usuario") if cls._operador else "usuario"

    @classmethod
    def operador_id(cls):
        """Retorna el ID del operador"""
        return cls._operador.get("id") if cls._operador else None

    @classmethod
    def tiene_permiso(cls, modulo):
        """Verifica si el operador tiene permiso para un modulo"""
        if not cls._operador:
            return False
        if cls._operador.get("nivel") == "administrador":
            return True
        return bool(cls._operador.get(f"mod_{modulo}", 0))

    # Metodos de compatibilidad
    @classmethod
    def nombre_usuario(cls):
        """Alias para nombre_operador (compatibilidad)"""
        return cls.nombre_operador()

    @classmethod
    def rol(cls):
        """Alias para nivel (compatibilidad)"""
        return cls.nivel()

    @classmethod
    def usuario_activo(cls):
        """Alias para operador_activo (compatibilidad)"""
        return cls._operador
