from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from nucleo.models import Tarea, Categoria, Etiqueta, RegistroActividad
from django.utils import timezone
import requests
import csv
import json

# Dashboard con Indicadores
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'nucleo/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener indicadores de la API externa
        try:
            response = requests.get('https://mindicador.cl/api')
            data = response.json()
            context['indicadores'] = {
                'UF': data.get('uf', {}).get('valor', 'N/A'),
                'Dólar': data.get('dolar', {}).get('valor', 'N/A'),
                'UTM': data.get('utm', {}).get('valor', 'N/A'),
                'IPC': data.get('ipc', {}).get('valor', 'N/A'),
                'Euro': data.get('euro', {}).get('valor', 'N/A'),
            }
        except Exception as e:
            context['indicadores'] = {'error': f'No se pudieron cargar los indicadores: {str(e)}'}
            # Datos de ejemplo cuando falla la API
            context['ejemplo_indicadores'] = {
                'UF': '36.500,25',
                'Dólar': '950,50',
                'UTM': '65.000',
                'IPC': '0,5%',
                'Euro': '1.020,30'
            }
        
        # Estadísticas de Tareas
        total = Tarea.objects.count()
        completadas = Tarea.objects.filter(completada=True).count()
        pendientes = Tarea.objects.filter(completada=False).count()
        
        context['total_tareas'] = total
        context['tareas_completadas'] = completadas
        context['tareas_pendientes'] = pendientes
        context['porcentaje_completadas'] = int((completadas / total * 100)) if total > 0 else 0
        
        # Contar categorías
        context['categorias_count'] = Categoria.objects.count()
        
        # Obtener últimas tareas (las 5 más recientes)
        context['ultimas_tareas'] = Tarea.objects.order_by('-fecha_creacion')[:5]
        
        # Fecha actual para comparaciones
        from django.utils import timezone
        context['hoy'] = timezone.now().date()
        
        return context
    
# CRUD Tarea
class TareaListView(LoginRequiredMixin, ListView):
    model = Tarea
    template_name = 'nucleo/tarea_list.html'
    context_object_name = 'tareas'

    def get_queryset(self):
        queryset = Tarea.objects.filter(usuario=self.request.user)
        estado = self.request.GET.get('estado')
        vencimiento = self.request.GET.get('vencimiento')
        
        if estado == 'completadas':
            queryset = queryset.filter(completada=True)
        elif estado == 'pendientes':
            queryset = queryset.filter(completada=False)
            
        if vencimiento == 'hoy':
            queryset = queryset.filter(fecha_vencimiento=timezone.now().date())
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_tareas = Tarea.objects.filter(usuario=self.request.user)
        
        completadas = user_tareas.filter(completada=True)
        pendientes = user_tareas.filter(completada=False)
        total = user_tareas.count()
        
        context['tareas_completadas'] = completadas
        context['tareas_pendientes'] = pendientes
        context['tareas_hoy'] = user_tareas.filter(fecha_vencimiento=timezone.now().date())
        context['hoy'] = timezone.now().date()
        
        # Calcular porcentajes
        context['porcentaje_completadas'] = int((completadas.count() / total * 100)) if total > 0 else 0
        context['porcentaje_pendientes'] = int((pendientes.count() / total * 100)) if total > 0 else 0
        
        return context

class TareaCreateView(LoginRequiredMixin, CreateView):
    model = Tarea
    fields = ['titulo', 'descripcion', 'fecha_vencimiento', 'categoria', 'etiqueta']
    template_name = 'nucleo/tarea_form.html'
    success_url = reverse_lazy('tarea_list')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

class TareaUpdateView(LoginRequiredMixin, UpdateView):
    model = Tarea
    fields = ['titulo', 'descripcion', 'fecha_vencimiento', 'categoria', 'etiqueta', 'completada']
    template_name = 'nucleo/tarea_form.html'
    success_url = reverse_lazy('tarea_list')

    def get_queryset(self):
        return Tarea.objects.filter(usuario=self.request.user)

class TareaDeleteView(LoginRequiredMixin, DeleteView):
    model = Tarea
    template_name = 'nucleo/tarea_confirm_delete.html'
    success_url = reverse_lazy('tarea_list')

    def get_queryset(self):
        return Tarea.objects.filter(usuario=self.request.user)


class TareaCompleteView(LoginRequiredMixin, View):
    """Marca una tarea como completada (o la alterna) y redirige a la lista."""
    def post(self, request, pk):
        tarea = get_object_or_404(Tarea, pk=pk, usuario=request.user)
        tarea.completada = not tarea.completada
        tarea.save()
        return redirect('tarea_list')

# JSON Dump
class JsonDumpView(LoginRequiredMixin, View):
    def get(self, request):
        data = {
            'categorias': list(Categoria.objects.values()),
            'etiquetas': list(Etiqueta.objects.values()),
            'tareas': list(Tarea.objects.values()),
            'registros': list(RegistroActividad.objects.values())
        }
        return JsonResponse(data)

# CSV Export
class CsvExportView(LoginRequiredMixin, View):
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tareas.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Título', 'Descripción', 'Categoría', 'Etiqueta', 'Usuario', 'Fecha Creación'])

        tareas = Tarea.objects.all()
        for tarea in tareas:
            writer.writerow([
                tarea.id, 
                tarea.titulo, 
                tarea.descripcion, 
                tarea.categoria.nombre, 
                tarea.etiqueta.nombre if tarea.etiqueta else '', 
                tarea.usuario.username, 
                tarea.fecha_creacion
            ])

        return response

# CRUD Categoria
class CategoriaListView(LoginRequiredMixin, ListView):
    model = Categoria
    template_name = 'nucleo/categoria_list.html'
    context_object_name = 'categorias'

class CategoriaCreateView(LoginRequiredMixin, CreateView):
    model = Categoria
    fields = ['nombre', 'descripcion']
    template_name = 'nucleo/categoria_form.html'
    success_url = reverse_lazy('categoria_list')

class CategoriaUpdateView(LoginRequiredMixin, UpdateView):
    model = Categoria
    fields = ['nombre', 'descripcion']
    template_name = 'nucleo/categoria_form.html'
    success_url = reverse_lazy('categoria_list')

class CategoriaDeleteView(LoginRequiredMixin, DeleteView):
    model = Categoria
    template_name = 'nucleo/categoria_confirm_delete.html'
    success_url = reverse_lazy('categoria_list')

