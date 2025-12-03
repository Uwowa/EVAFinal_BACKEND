from django.db import models
from django.contrib.auth.models import User

# Tabla 1: Categoría
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

# Tabla 2: Etiqueta (Gestionada por App Desktop)
class Etiqueta(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    color = models.CharField(max_length=7, default="#FFFFFF", verbose_name="Color Hex")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Etiqueta"
        verbose_name_plural = "Etiquetas"

# Tabla 3: Tarea (Gestionada por Web, FK a T1 y T2)
class Tarea(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descripcion = models.TextField(verbose_name="Descripción")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_vencimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Vencimiento")
    completada = models.BooleanField(default=False, verbose_name="Completada")
    
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="tareas", verbose_name="Categoría")
    etiqueta = models.ForeignKey(Etiqueta, on_delete=models.SET_NULL, null=True, blank=True, related_name="tareas", verbose_name="Etiqueta")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"

# Tabla 4: Registro de Actividad (Libre elección)
class RegistroActividad(models.Model):
    accion = models.CharField(max_length=255, verbose_name="Acción")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Usuario")
    detalles = models.TextField(blank=True, verbose_name="Detalles")

    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.fecha}"

    class Meta:
        verbose_name = "Registro de Actividad"
        verbose_name_plural = "Registros de Actividad"
