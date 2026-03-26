from datetime import date

from dominio.libro import Libro
from dominio.usuario import Usuario
from dominio.prestamo import Prestamo
from servicio.validadores import (
    validar_textos_no_vacios,
    validar_enteros_positivos,
    validar_fechas,
)
from servicio.multas import MultaStrategy, MultaPorDia
from servicio.exportador import ExportadorMixin


class Biblioteca(ExportadorMixin):
    """
    Agregado raiz del sistema
    Gestiona libros, usuarios, prestamos y la fecha actual del sistema
    """

    @validar_fechas("fecha_actual")
    def __init__(self, fecha_actual: date):

        self.fecha_actual = fecha_actual

        self._libros = {}
        self._usuarios = {}
        self._prestamos_activos = {}
        self._prestamos_historico = []

        self._estrategia_multa = MultaPorDia(1.0) # Por defecto la multa diaria sera de 1€
# ============================================================================ LIBRO
    @validar_textos_no_vacios("titulo", "autor")
    def agregar_libro(self, titulo: str, autor: str):
        # Crea un libro y lo añade al catalogo
        libro = Libro(titulo, autor)
        self._libros[libro.id_libro] = libro
        return libro

    def eliminar_libro(self, id_libro: int):
        # Elimina un libro del catalogo si no esta prestado
        if id_libro not in self._libros:
            raise ValueError("El libro no existe")

        if id_libro in self._prestamos_activos:
            raise ValueError("No se puede eliminar un libro que esta actualmente prestado")

        return self._libros.pop(id_libro)

    def listar_libros(self):
        # Devuelve una lista de todos los libros registrados
        return list(self._libros.values())

    def buscar_libro_por_id(self, id_libro: int):
        # Devuelve un libro a partir de su ID, o None si no existe
        return self._libros.get(id_libro)

    def buscar_libros_por_titulo(self, texto: str):
        # Devuelve una lista de libros cuyo titulo contiene el texto indicado
        texto = texto.lower()
        return [libro for libro in self._libros.values() if texto in libro.titulo.lower()]

    def buscar_libros_por_autor(self, texto: str):
        # Devuelve una lista de libros por autor
        texto = texto.lower()
        return [
            libro for libro in self._libros.values()
            if texto in libro.autor.lower()
        ]

# ============================================================================ USUARIO
    @validar_textos_no_vacios("nombre")
    def registrar_usuario(self, nombre: str):
        # Crea un usuario y lo registra en la biblioteca
        usuario = Usuario(nombre)
        self._usuarios[usuario.id_usuario] = usuario
        return usuario

    def eliminar_usuario(self, id_usuario: int):
        # Elimina un usuario si no tiene prestamos activos
        if id_usuario not in self._usuarios:
            raise ValueError("El usuario no existe.")

        for prestamo in self._prestamos_activos.values():
            if prestamo.id_usuario == id_usuario:
                raise ValueError("No se puede eliminar un usuario con prestamos activos.")

        return self._usuarios.pop(id_usuario)

    def listar_usuarios(self):
        # Devuelve una lista de todos los usuarios registrados
        return list(self._usuarios.values())

    def buscar_usuario_por_id(self, id_usuario: int):
        # Devuelve un usuario a partir de su ID, o None si no existe
        return self._usuarios.get(id_usuario)

    def buscar_usuario_por_nombre(self, texto: str):
        texto = texto.lower()
        return [
            usuario for usuario in self._usuarios.values()
            if texto in usuario.nombre.lower()
        ]

    def historial_usuario(self, id_usuario: int):
        # Devuelve el historial completo de prestamos de un usuario
        if id_usuario not in self._usuarios:
            raise ValueError("El usuario no existe.")
        return [prestamo for prestamo in self._prestamos_historico if prestamo.id_usuario == id_usuario]

# ============================================================================ MULTAS
    # Funcion para poder cambiar el tipo de multa (multa_por_dia o multa_fija)
    def cambiar_estrategia_multa(self, estrategia: MultaStrategy):
        if not isinstance(estrategia, MultaStrategy):
            raise TypeError("La estrategia debe ser una instancia de MultaStrategy.")
        self._estrategia_multa = estrategia

    def calcular_multa(self, prestamo):
        return self._estrategia_multa.calcular(prestamo)

# ============================================================================ PRESTAMO
    @validar_enteros_positivos("id_usuario", "id_libro", "plazo_dias")
    def prestar_libro(self, id_usuario: int, id_libro: int, plazo_dias: int):
        # Registra un prestamo usando la fecha actual del sistema como fecha de inicio
        if id_usuario not in self._usuarios:
            raise ValueError("El usuario no existe.")

        if id_libro not in self._libros:
            raise ValueError("El libro no existe.")

        if id_libro in self._prestamos_activos:
            raise ValueError("El libro ya esta prestado actualmente.")

        prestamo = Prestamo(
            id_usuario=id_usuario,
            id_libro=id_libro,
            fecha_inicio=self.fecha_actual,
            plazo_dias=plazo_dias
        )

        self._prestamos_activos[id_libro] = prestamo
        self._prestamos_historico.append(prestamo)

        return prestamo

    def listar_prestamos_activos(self):
        # Devuelve una lista de todos los prestamos activos
        return list(self._prestamos_activos.values())

    def prestamos_finalizados(self):
        # Devuelve  una lista de los prestamos que han finalizado(entregados)
        return [
            prestamo for prestamo in self._prestamos_historico
            if prestamo.fecha_devolucion is not None
        ]

    def prestamos_vencidos(self):
        # Devuelve una lista con los prestamos activos que estan vencidos(fuera de fecha y no entregados)
        return [
            prestamo
            for prestamo in self._prestamos_activos.values()
            if prestamo.esta_vencido(self.fecha_actual)
        ]

    def libro_esta_prestado(self, id_libro: int):
        # Indica si un libro esta actualmente prestado
        return id_libro in self._prestamos_activos

# ============================================================================ DEVOLUCION
    @validar_enteros_positivos("id_libro")
    @validar_fechas("fecha_devolucion")
    def devolver_libro(self, id_libro: int, fecha_devolucion: date):
        # Registra la devolucion de un libro prestado
        if id_libro not in self._prestamos_activos:
            raise ValueError("Ese libro no esta actualmente prestado.")

        prestamo = self._prestamos_activos[id_libro]
        prestamo.registrar_devolucion(fecha_devolucion)

        del self._prestamos_activos[id_libro]

        return prestamo

    def historial_devoluciones(self):
        return [
            prestamo for prestamo in self._prestamos_historico
            if prestamo.fecha_devolucion is not None
        ]

# ============================================================================ SISTEMA
    @validar_fechas("nueva_fecha")
    def cambiar_fecha_actual(self, nueva_fecha: date):
        # Cambia la fecha actual del sistema
        self.fecha_actual = nueva_fecha


# ============================================================================ PLUGINS
    # Funcion para "estadisticas_plugin.py"
    def resumen(self):
        return {
            "fecha": self.fecha_actual,
            "libros": len(self._libros),
            "usuarios": len(self._usuarios),
            "prestamos_activos": len(self._prestamos_activos)
        }

    def __iter__(self):
        # Permite iterar directamente sobre los libros de la biblioteca
        return iter(self._libros.values())

    def __getitem__(self, id_libro: int):
        # Permite acceder a un libro por su ID usando corchetes
        return self._libros[id_libro]

    def __len__(self):
        # Devuelve el numero de libros registrados en la biblioteca
        return len(self._libros)

    def __str__(self):
        return (
            f"Biblioteca(fecha_actual={self.fecha_actual}, "
            f"libros={len(self._libros)}, usuarios={len(self._usuarios)}, "
            f"prestamos_activos={len(self._prestamos_activos)})"
        )