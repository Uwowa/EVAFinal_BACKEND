from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views
from rest_framework.authtoken import views as token_views

router = DefaultRouter()
router.register(r'categorias', views.CategoriaViewSet)
router.register(r'etiquetas', views.EtiquetaViewSet)
router.register(r'tareas', views.TareaViewSet)
router.register(r'registros', views.RegistroActividadViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token-auth/', token_views.obtain_auth_token),
]
