import csv
import json
import os
from datetime import date

from dominio.libro import Libro
from dominio.usuario import Usuario
from dominio.prestamo import Prestamo


class ExportadorMixin:
    """
    Mixin que añade funcionalidad de exportacion e importacion
    a clases que tengan libros, usuarios y prestamos historicos.
    """


# ============================================================ HELPERS INTERNOS
    def _convertir_fecha(self, texto):
        # Convierte strings ISO a date
        if texto in (None, "", "None"):
            return None
        return date.fromisoformat(texto)

    def _reiniciar_estado(self):
        # Limpia el sistema para que la importacion no de errores
        self._libros = {}
        self._usuarios = {}
        self._prestamos_activos = {}
        self._prestamos_historico = []

        Libro._contador_id = 1
        Usuario._contador_id = 1

    def _recalcular_contadores(self):
        # Ajusta los contadores para que al importar no empiecen en 1
        max_libro = max(self._libros.keys(), default=0)
        max_usuario = max(self._usuarios.keys(), default=0)

        Libro._contador_id = max_libro + 1
        Usuario._contador_id = max_usuario + 1

    def _ruta_exportacion(self, nombre_archivo):
        # Asegura que el directorio exportacion exista y devuelve su ruta
        carpeta = "exportacion"
        os.makedirs(carpeta, exist_ok=True)
        return os.path.join(carpeta, nombre_archivo)

    def _ruta_importacion(self, nombre_archivo):
        # Asegura que el directorio importacion exista y devuelve su ruta
        carpeta = "importacion"
        os.makedirs(carpeta, exist_ok=True)
        return os.path.join(carpeta, nombre_archivo)


# ============================================================ EXPORTACION CSV
    def exportar_libros_csv(self, ruta_archivo: str):
        # Exportacion de libros mediante CSV
        ruta = self._ruta_exportacion(ruta_archivo)

        with open(ruta, mode="w", newline="", encoding="utf-8") as archivo:
            writer = csv.writer(archivo)
            writer.writerow(["id_libro", "titulo", "autor"])

            for libro in self._libros.values():
                writer.writerow([
                    libro.id_libro,
                    libro.titulo,
                    libro.autor
                ])

        return ruta

    def exportar_usuarios_csv(self, ruta_archivo: str):
        # Exportacion de usuarioas mediante CSV
        ruta = self._ruta_exportacion(ruta_archivo)

        with open(ruta, mode="w", newline="", encoding="utf-8") as archivo:
            writer = csv.writer(archivo)
            writer.writerow(["id_usuario", "nombre"])

            for usuario in self._usuarios.values():
                writer.writerow([
                    usuario.id_usuario,
                    usuario.nombre
                ])

        return ruta

    def exportar_prestamos_csv(self, ruta_archivo: str):
        # Exportacion de prestamos mediante CSV
        ruta = self._ruta_exportacion(ruta_archivo)

        with open(ruta, mode="w", newline="", encoding="utf-8") as archivo:
            writer = csv.writer(archivo)
            writer.writerow([
                "id_usuario",
                "id_libro",
                "fecha_inicio",
                "plazo_dias",
                "fecha_limite",
                "fecha_devolucion"
            ])

            for prestamo in self._prestamos_historico:
                writer.writerow([
                    prestamo.id_usuario,
                    prestamo.id_libro,
                    prestamo.fecha_inicio.isoformat(),
                    prestamo.plazo_dias,
                    prestamo.fecha_limite().isoformat(),
                    prestamo.fecha_devolucion.isoformat() if prestamo.fecha_devolucion else ""
                ])

        return ruta


# ============================================================ EXPORTACION JSON
    def exportar_todo_json(self, ruta_archivo: str):
        # Exporta todos los datos del sistema en un archivo JSON
        ruta = self._ruta_exportacion(ruta_archivo)

        datos = {
            "fecha_actual": self.fecha_actual.isoformat(),
            "libros": {
                libro.id_libro: {
                    "titulo": libro.titulo,
                    "autor": libro.autor
                }
                for libro in self._libros.values()
            },
            "usuarios": {
                usuario.id_usuario: {
                    "nombre": usuario.nombre
                }
                for usuario in self._usuarios.values()
            },
            "prestamos_historico": [
                {
                    "id_usuario": prestamo.id_usuario,
                    "id_libro": prestamo.id_libro,
                    "fecha_inicio": prestamo.fecha_inicio.isoformat(),
                    "plazo_dias": prestamo.plazo_dias,
                    "fecha_limite": prestamo.fecha_limite().isoformat(),
                    "fecha_devolucion": prestamo.fecha_devolucion.isoformat() if prestamo.fecha_devolucion else None
                }
                for prestamo in self._prestamos_historico
            ]
        }

        with open(ruta, mode="w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)

        return ruta


# ============================================================ IMPORTACION CSV
    def importar_libros_csv(self, ruta_archivo: str, reemplazar: bool = False):
        # Carga libros desde CSV, permite sobrescribir o añadir a los existentes
        ruta = self._ruta_importacion(ruta_archivo)

        if reemplazar:
            self._libros = {}
            Libro._contador_id = 1

        with open(ruta, mode="r", newline="", encoding="utf-8") as archivo:
            reader = csv.DictReader(archivo)

            for fila in reader:
                id_libro = int(fila["id_libro"])
                titulo = fila["titulo"].strip()
                autor = fila["autor"].strip()

                libro = Libro(titulo, autor)
                libro.id_libro = id_libro

                self._libros[id_libro] = libro

        self._recalcular_contadores()


    def importar_usuarios_csv(self, ruta_archivo: str, reemplazar: bool = False):
        # Carga usuarios desde CSV, permite sobrescribir o añadir a los existentes
        ruta = self._ruta_importacion(ruta_archivo)

        if reemplazar:
            self._usuarios = {}
            Usuario._contador_id = 1

        with open(ruta, mode="r", newline="", encoding="utf-8") as archivo:
            reader = csv.DictReader(archivo)

            for fila in reader:
                id_usuario = int(fila["id_usuario"])
                nombre = fila["nombre"].strip()

                usuario = Usuario(nombre)
                usuario.id_usuario = id_usuario

                self._usuarios[id_usuario] = usuario

        self._recalcular_contadores()


    def importar_prestamos_csv(self, ruta_archivo: str):

        ruta = self._ruta_importacion(ruta_archivo)

        with open(ruta, mode="r", encoding="utf-8") as archivo:

            lector = csv.DictReader(archivo)

            for fila in lector:

                id_usuario = int(fila["id_usuario"])
                id_libro = int(fila["id_libro"])

                fecha_inicio = self._convertir_fecha(fila["fecha_inicio"])
                plazo_dias = int(fila["plazo_dias"])

                prestamo = Prestamo(
                    id_usuario=id_usuario,
                    id_libro=id_libro,
                    fecha_inicio=fecha_inicio,
                    plazo_dias=plazo_dias
                )

                fecha_devolucion_txt = fila.get("fecha_devolucion")

                if fecha_devolucion_txt:
                    prestamo.fecha_devolucion = self._convertir_fecha(fecha_devolucion_txt)

                # añadir al historico
                self._prestamos_historico.append(prestamo)

                # si no está devuelto → activo
                if prestamo.fecha_devolucion is None:
                    self._prestamos_activos[prestamo.id_libro] = prestamo

        self._recalcular_contadores()

# ============================================================IMPORTACION JSON
    def importar_todo_json(self, ruta_archivo: str):
        ruta = self._ruta_importacion(ruta_archivo)

        with open(ruta, mode="r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        self._reiniciar_estado()

        self.fecha_actual = self._convertir_fecha(datos["fecha_actual"])

        # LIBROS
        for id_libro_txt, info in datos.get("libros", {}).items():
            id_libro = int(id_libro_txt)

            libro = Libro(info["titulo"], info["autor"])
            libro.id_libro = id_libro

            self._libros[id_libro] = libro

        # USUARIOS
        for id_usuario_txt, info in datos.get("usuarios", {}).items():
            id_usuario = int(id_usuario_txt)

            usuario = Usuario(info["nombre"])
            usuario.id_usuario = id_usuario

            self._usuarios[id_usuario] = usuario

        # PRESTAMOS
        prestamos_importados = []

        # Formato normal: prestamos_historico
        prestamos_importados.extend(datos.get("prestamos_historico", []))

        # Formato alternativo: activos + finalizados
        prestamos_importados.extend(datos.get("prestamos_activos", []))
        prestamos_importados.extend(datos.get("prestamos_finalizados", []))

        for info in prestamos_importados:
            prestamo = Prestamo(
                id_usuario=int(info["id_usuario"]),
                id_libro=int(info["id_libro"]),
                fecha_inicio=self._convertir_fecha(info["fecha_inicio"]),
                plazo_dias=int(info["plazo_dias"])
            )

            fecha_devolucion = self._convertir_fecha(info.get("fecha_devolucion"))
            if fecha_devolucion is not None:
                prestamo.fecha_devolucion = fecha_devolucion

            self._prestamos_historico.append(prestamo)

            if prestamo.fecha_devolucion is None:
                self._prestamos_activos[prestamo.id_libro] = prestamo

        self._recalcular_contadores()
