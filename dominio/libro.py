from dominio.metaclase import MetaclaseEntidad

# Libro hereda de Metaclase.py
class Libro(metaclass=MetaclaseEntidad):
    """
    Representa un libro dentro del catalogo de la biblioteca
    """

    # Los ID van a ser auto incrementables
    _contador_id = 1

    def __init__(self, titulo: str, autor: str):
        # Se crea una variable distinta para cada objeto
        self.id_libro = Libro._contador_id
        Libro._contador_id += 1

        self.titulo = titulo
        self.autor = autor

    def __str__(self):
        return f"[{self.id_libro}] {self.titulo} - {self.autor}"

    def __repr__(self):
        return f"Libro(id={self.id_libro}, titulo='{self.titulo}', autor='{self.autor}')"