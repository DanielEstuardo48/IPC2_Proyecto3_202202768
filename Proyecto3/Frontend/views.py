from django.shortcuts import render ,HttpResponse
import requests

# Create your views here.
def index(request):
    return render (request, 'index.html')

def Carga_C(request):
    return render (request, 'Carga_C.html')

def Cargar_F(request):
    return render (request, 'Cargar_F.html')

def EstadoCuenta(request):
    return render (request, 'EstadoCuenta.html')

def Estudiante(request):
    return render (request,'Estudiante.html')

def Documentacion(request):
    return render (request,'Documentacion.html')

def Ingresos(request):
    return render (request,'Ingresos.html')


def borrar_datos_backend(request):
    url = 'http://127.0.0.1:4000/borrardatos'
    response = requests.delete(url)
    
    if response.status_code == 200:
        # Mensaje de éxito
        mensaje = '¡Los datos se borraron correctamente!'
        return HttpResponse('<script>alert("' + mensaje + '");window.location = document.referrer;</script>', status=200)
    else:
        # Mensaje de error
        mensaje = 'Hubo un error al borrar los datos. Por favor, intenta nuevamente.'
        return HttpResponse('<script>alert("' + mensaje + '");window.location = document.referrer;</script>', status=500)

def cargar_xml_cb(request):
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        if archivo:
            url = 'http://127.0.0.1:4000/cargar_xml'  # Ruta del backend Flask
            files = {'archivo': archivo}  # Cambia 'uploadfile' a 'archivo'
            response = requests.post(url, files=files)
            if response.status_code == 200:
                mensaje = 'Archivo cargado exitosamente'
                return HttpResponse('<script>alert("' + mensaje + '");window.location = document.referrer;</script>', status=200)
            else:
                mensaje = 'Error al cargar el archivo'
                return HttpResponse('<script>alert("' + mensaje + '");window.location = document.referrer;</script>', status=500)
        else:
            mensaje = 'No se ha seleccionado ningún archivo'
            return HttpResponse('<script>alert("' + mensaje + '");window.location = document.referrer;</script>', status=500)
    else:
        mensaje = 'La solicitud debe ser de tipo POST'
        return HttpResponse('<script>alert("' + mensaje + '");window.location = document.referrer;</script>', status=500)

def cargar_xml_fp(request):
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        if archivo:
            url = 'http://127.0.0.1:4000/cargar_pagos_y_facturas'  # Ruta del backend Flask
            files = {'archivo': archivo}  # Cambia 'uploadfile' a 'archivo'
            response = requests.post(url, files=files)
            if response.status_code == 200:
                mensaje = 'Archivo cargado exitosamente'
                return HttpResponse('<script>alert("' + mensaje + '");window.location = document.referrer;</script>', status=200)
            else:
                mensaje = 'Error al cargar el archivo'
                return HttpResponse('<script>alert("' + mensaje + '");window.location = document.referrer;</script>', status=500)
        else:
            mensaje = 'No se ha seleccionado ningún archivo'
            return HttpResponse('<script>alert("' + mensaje + '");window.location = document.referrer;</script>', status=500)
    else:
        mensaje = 'La solicitud debe ser de tipo POST'
        return HttpResponse('<script>alert("' + mensaje + '");window.location = document.referrer;</script>', status=500)
    
def mostrar_clientes(request):
    url = 'http://127.0.0.1:4000/mostrarclientes'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanzará una excepción si hay un error en la solicitud
        datos_clientes = response.json()
        return render(request, 'EstadoCuenta.html', {'clientes': datos_clientes})
    except requests.exceptions.RequestException as e:
        mensaje_error = 'Ocurrió un error al obtener los clientes: {}'.format(str(e))
        return render(request, 'EstadoCuenta.html', {'error': mensaje_error})
    
def mostrar_cuenta(request):
    if request.method == 'POST':
        nit = request.POST.get('nit', '')
        url = 'http://127.0.0.1:4000/consulta_cuenta'
        try:
            response = requests.get(url, params={'nit': nit})
            response.raise_for_status()
            datos_cuenta = response.json()
            return render(request, 'EstadoCuenta.html', {'datos_cuenta': datos_cuenta})
        except requests.exceptions.RequestException as e:
            mensaje_error = 'Ocurrió un error al obtener los datos de la cuenta: {}'.format(str(e))
            return render(request, 'EstadoCuenta.html', {'error': mensaje_error})

    return render(request, 'EstadoCuenta.html')