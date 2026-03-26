from dominio.metaclase import MetaclaseEntidad


class Usuario(metaclass=MetaclaseEntidad):
    """
    Representa un usuario registrado en la biblioteca
    """
    
    # Los ID van a ser auto incrementable
    _contador_id = 1

    def __init__(self, nombre: str):
        # Se crea una variable distinta para cada objeto
        self.id_usuario = Usuario._contador_id
        Usuario._contador_id += 1

        self.nombre = nombre

    def __str__(self):
        return f"[{self.id_usuario}] {self.nombre}"

    def __repr__(self):
        return f"Usuario(id={self.id_usuario}, nombre='{self.nombre}')"