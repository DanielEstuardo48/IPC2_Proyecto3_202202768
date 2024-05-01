from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('borrar_datos_backend', views.borrar_datos_backend, name='borrar_datos_backend'),
    path('Carga_C', views.Carga_C, name='Carga_C'),
    path('cargar_xml_cb', views.cargar_xml_cb, name='subirxmlcb'),
    path('Cargar_F', views.Cargar_F, name='Cargar_F'),
    path('cargar_xml_fp', views.cargar_xml_fp, name='subirxmlfp'),
    path('EstadoCuenta', views.EstadoCuenta, name='EstadoCuenta'),
    path('mostrar_clientes', views.mostrar_clientes, name='mostrar_clientes'),
    path('mostrar_cuenta',views.mostrar_cuenta, name='mostrar_cuenta'),
    path('Estudiante', views.Estudiante, name='estudiante'),
    path('Documentacion', views.Documentacion, name='documentacion'),
    path('Ingresos', views.Ingresos, name='ingresos'),
]