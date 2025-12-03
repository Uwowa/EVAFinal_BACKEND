from django.urls import path
from django.contrib.auth import views as auth_views
from nucleo import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='nucleo/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('tareas/', views.TareaListView.as_view(), name='tarea_list'),
    path('tareas/nueva/', views.TareaCreateView.as_view(), name='tarea_create'),
    path('tareas/<int:pk>/editar/', views.TareaUpdateView.as_view(), name='tarea_update'),
    path('tareas/<int:pk>/eliminar/', views.TareaDeleteView.as_view(), name='tarea_delete'),
    
    path('categorias/', views.CategoriaListView.as_view(), name='categoria_list'),
    path('categorias/nueva/', views.CategoriaCreateView.as_view(), name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='categoria_update'),
    path('categorias/<int:pk>/eliminar/', views.CategoriaDeleteView.as_view(), name='categoria_delete'),
    
    path('datos/json/', views.JsonDumpView.as_view(), name='json_dump'),
    path('datos/csv/', views.CsvExportView.as_view(), name='csv_export'),
]
