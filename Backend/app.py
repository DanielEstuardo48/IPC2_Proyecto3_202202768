import re
from flask import Flask, request, jsonify, Response
import xml.etree.ElementTree as ET

app = Flask(__name__)

class Cliente:
    def __init__(self, nit, nombre):
        self.nit = nit
        self.nombre = nombre

    def to_xml(self):
        cliente_xml = ET.Element("cliente")
        ET.SubElement(cliente_xml, "NIT").text = self.nit
        ET.SubElement(cliente_xml, "nombre").text = self.nombre
        return cliente_xml

class Banco:
    def __init__(self, codigo, nombre):
        self.codigo = codigo
        self.nombre = nombre

    def to_xml(self):
        banco_xml = ET.Element("banco")
        ET.SubElement(banco_xml, "codigo").text = self.codigo
        ET.SubElement(banco_xml, "nombre").text = self.nombre
        return banco_xml

class Pago:
    def __init__(self, codigo_banco, fecha, nit_cliente, valor):
        self.codigo_banco = codigo_banco
        self.fecha = fecha
        self.nit_cliente = nit_cliente
        self.valor = valor

    def to_xml(self):
        pago_xml = ET.Element("pago")
        ET.SubElement(pago_xml, "codigo_banco").text = self.codigo_banco
        ET.SubElement(pago_xml, "fecha").text = self.fecha
        ET.SubElement(pago_xml, "nit_cliente").text = self.nit_cliente
        ET.SubElement(pago_xml, "valor").text = str(self.valor)
        return pago_xml

class Factura:
    def __init__(self, numero_factura, nit_cliente, fecha, valor):
        self.numero_factura = numero_factura
        self.nit_cliente = nit_cliente
        self.fecha = fecha
        self.valor = valor

    def to_xml(self):
        factura_xml = ET.Element("factura")
        ET.SubElement(factura_xml, "numero_factura").text = self.numero_factura
        ET.SubElement(factura_xml, "nit_cliente").text = self.nit_cliente
        ET.SubElement(factura_xml, "fecha").text = self.fecha
        ET.SubElement(factura_xml, "valor").text = str(self.valor)
        return factura_xml


# Mantenemos los datos en memoria en lugar de escribir en disco
clientes_acumulativos = []
bancos_acumulativos = []
pagos_acumulativos = []
facturas_acumulativas = []

@app.route('/cargar_xml', methods=['POST'])
def subir_xml():
    if 'archivo' not in request.files:
        return jsonify({'error': 'No se ha enviado ningún archivo'})

    archivo = request.files['archivo']
    if archivo.filename == '':
        return jsonify({'error': 'No se ha seleccionado ningún archivo'})

    if archivo and archivo.filename.endswith('.xml'):
        parsear_xml(archivo)
        return jsonify({'mensaje': 'Archivo XML subido exitosamente'})
    else:
        return jsonify({'error': 'El archivo subido no es un archivo XML válido'})

def parsear_xml(archivo):
    global clientes_acumulativos, bancos_acumulativos

    tree = ET.parse(archivo)
    root = tree.getroot()

    nuevos_clientes = []
    nuevos_bancos = []

    for cliente_xml in root.findall('./clientes/cliente'):
        nit = cliente_xml.find('NIT').text
        nombre = cliente_xml.find('nombre').text
        cliente_existente = next((c for c in clientes_acumulativos if c.nit == nit), None)
        if cliente_existente:
            cliente_existente.nombre = nombre
        else:
            cliente = Cliente(nit, nombre)
            nuevos_clientes.append(cliente)

    for banco_xml in root.findall('./bancos/banco'):
        codigo = banco_xml.find('codigo').text
        nombre = banco_xml.find('nombre').text
        banco_existente = next((b for b in bancos_acumulativos if b.codigo == codigo), None)
        if banco_existente:
            banco_existente.nombre = nombre
        else:
            banco = Banco(codigo, nombre)
            nuevos_bancos.append(banco)

    clientes_acumulativos.extend(nuevos_clientes)
    bancos_acumulativos.extend(nuevos_bancos)

@app.route('/obtenercb', methods=['GET'])
def obtener_clientes():
    resultado_xml = construir_xml(clientes_acumulativos, bancos_acumulativos)
    return Response(resultado_xml, mimetype='text/xml')

@app.route('/obtener-estadisticas', methods=['GET'])
def obtener_estadisticas():
    global clientes_acumulativos, bancos_acumulativos

    try:
        nuevos_clientes, nuevos_bancos = parsear_xml('nuevo_xml_subido.xml')
    except FileNotFoundError:
        nuevos_clientes = []
        nuevos_bancos = []

    resultado_xml = construir_estadisticas(clientes_acumulativos, bancos_acumulativos, nuevos_clientes, nuevos_bancos)

    # Actualizar datos acumulativos con los nuevos clientes y bancos
    clientes_acumulativos.extend(nuevos_clientes)
    bancos_acumulativos.extend(nuevos_bancos)

    return Response(resultado_xml, mimetype='text/xml')

def construir_xml(clientes, bancos):
    resultado_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    resultado_xml += '<datos>\n'
    resultado_xml += '  <clientes>\n'
    for cliente in clientes:
        resultado_xml += f'    <cliente>\n'
        resultado_xml += f'      <NIT>{cliente.nit}</NIT>\n'
        resultado_xml += f'      <nombre>{cliente.nombre}</nombre>\n'
        resultado_xml += f'    </cliente>\n'
    resultado_xml += '  </clientes>\n'
    
    resultado_xml += '  <bancos>\n'
    for banco in bancos:
        resultado_xml += f'    <banco>\n'
        resultado_xml += f'      <codigo>{banco.codigo}</codigo>\n'
        resultado_xml += f'      <nombre>{banco.nombre}</nombre>\n'
        resultado_xml += f'    </banco>\n'
    resultado_xml += '  </bancos>\n'
    resultado_xml += '</datos>'
    return resultado_xml

def construir_estadisticas(clientes, bancos, nuevos_clientes, nuevos_bancos):
    num_clientes_totales = len(clientes)
    num_bancos_totales = len(bancos)

    # Encontrar clientes y bancos actualizados
    clientes_actualizados = [cliente for cliente in nuevos_clientes if cliente in clientes]
    bancos_actualizados = [banco for banco in nuevos_bancos if banco in bancos]

    resultado_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    resultado_xml += '<estadisticas>\n'
    resultado_xml += f'  <num_clientes_totales>{num_clientes_totales}</num_clientes_totales>\n'
    resultado_xml += f'  <num_bancos_totales>{num_bancos_totales}</num_bancos_totales>\n'
    resultado_xml += f'  <num_clientes_actualizados>{len(clientes_actualizados)}</num_clientes_actualizados>\n'
    resultado_xml += f'  <num_bancos_actualizados>{len(bancos_actualizados)}</num_bancos_actualizados>\n'
    resultado_xml += '</estadisticas>'

    return resultado_xml

def parsear_pagos_y_facturas(archivo):
    nuevos_pagos = []
    nuevas_facturas = []

    tree = ET.parse(archivo)
    root = tree.getroot()

    for pago_xml in root.findall('./pagos/pago'):
        codigo_banco = pago_xml.find('codigoBanco').text
        fecha_texto = pago_xml.find('fecha').text
        fecha_numero = extraer_numeros_fecha(fecha_texto)
        nit_cliente = pago_xml.find('NITcliente').text
        valor = float(pago_xml.find('valor').text)
        pago = Pago(codigo_banco, fecha_numero, nit_cliente, valor)
        nuevos_pagos.append(pago)

    for factura_xml in root.findall('./facturas/factura'):
        numero_factura = factura_xml.find('numeroFactura').text  # Cambiar 'numero_factura' a 'numeroFactura'
        nit_cliente = factura_xml.find('NITcliente').text
        fecha_texto = factura_xml.find('fecha').text
        fecha_numero = extraer_numeros_fecha(fecha_texto)
        valor = float(factura_xml.find('valor').text)
        factura = Factura(numero_factura, nit_cliente, fecha_numero, valor)
        nuevas_facturas.append(factura)


    # Extender las listas acumulativas con los nuevos pagos y facturas
    pagos_acumulativos.extend(nuevos_pagos)
    facturas_acumulativas.extend(nuevas_facturas)

    return nuevos_pagos, nuevas_facturas

# Ruta para cargar XML de pagos y facturas
@app.route('/cargar_pagos_y_facturas', methods=['POST'])
def subir_pagos_y_facturas():
    if 'archivo' not in request.files:
        return jsonify({'error': 'No se ha enviado ningún archivo'})

    archivo = request.files['archivo']
    if archivo.filename == '':
        return jsonify({'error': 'No se ha seleccionado ningún archivo'})

    if archivo and archivo.filename.endswith('.xml'):
        nuevos_pagos, nuevas_facturas = parsear_pagos_y_facturas(archivo)
        # Aquí podrías realizar acciones adicionales, como almacenar los nuevos pagos y facturas en una base de datos
        return jsonify({'mensaje': 'Archivo de pagos y facturas XML subido exitosamente'})
    else:
        return jsonify({'error': 'El archivo subido no es un archivo XML válido'})

@app.route('/obtener_datos_facturas_pagos', methods=['GET'])
def obtener_datos_facturas_pagos():
    # Construir el XML con los datos acumulados de facturas y pagos
    xml_data = construir_xml_facturas_pagos()

    # Devolver el XML como una respuesta
    return Response(xml_data, mimetype='text/xml')

def extraer_numeros_fecha(texto_fecha):
    # Expresión regular para extraer solo los números de la fecha
    patron_fecha = r'\b(\d{2}/\d{2}/\d{4})\b'
    # Buscar coincidencias en el texto de la fecha
    match = re.search(patron_fecha, texto_fecha)
    if match:
        return match.group(1)
    else:
        return None

def construir_xml_facturas_pagos():
    resultado_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    resultado_xml += '<datos>\n'
    
    resultado_xml += '  <pagos>\n'
    for pago in pagos_acumulativos:
        resultado_xml += '    <pago>\n'
        resultado_xml += f'      <codigoBanco>{pago.codigo_banco}</codigoBanco>\n'
        resultado_xml += f'      <fecha>{pago.fecha}</fecha>\n'
        resultado_xml += f'      <NITcliente>{pago.nit_cliente}</NITcliente>\n'
        resultado_xml += f'      <valor>{pago.valor}</valor>\n'
        resultado_xml += '    </pago>\n'
    resultado_xml += '  </pagos>\n'
    
    resultado_xml += '  <facturas>\n'
    for factura in facturas_acumulativas:
        resultado_xml += '    <factura>\n'
        resultado_xml += f'      <numeroFactura>{factura.numero_factura}</numeroFactura>\n'
        resultado_xml += f'      <NITcliente>{factura.nit_cliente}</NITcliente>\n'
        resultado_xml += f'      <fecha>{factura.fecha}</fecha>\n'
        resultado_xml += f'      <valor>{factura.valor}</valor>\n'
        resultado_xml += '    </factura>\n'
    resultado_xml += '  </facturas>\n'

    resultado_xml += '</datos>'
    return resultado_xml

# Función para analizar facturas y pagos
def analizar_facturas_pagos(facturas, pagos):
    # Contadores
    total_facturas = len(facturas)
    total_pagos = len(pagos)
    facturas_duplicadas = len(facturas) - len(set(factura.numero_factura for factura in facturas))
    pagos_duplicados = len(pagos) - len(set(pago.codigo_banco for pago in pagos))
    facturas_con_error = sum(1 for factura in facturas if factura.valor <= 0)
    pagos_con_error = sum(1 for pago in pagos if pago.valor <= 0)

    # Crear XML con resultados
    xml_data = f'<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_data += '<analisis>\n'
    xml_data += f'  <total_facturas>{total_facturas}</total_facturas>\n'
    xml_data += f'  <facturas_duplicadas>{facturas_duplicadas}</facturas_duplicadas>\n'
    xml_data += f'  <facturas_con_error>{facturas_con_error}</facturas_con_error>\n'
    xml_data += f'  <total_pagos>{total_pagos}</total_pagos>\n'
    xml_data += f'  <pagos_duplicados>{pagos_duplicados}</pagos_duplicados>\n'
    xml_data += f'  <pagos_con_error>{pagos_con_error}</pagos_con_error>\n'
    xml_data += '</analisis>'

    return xml_data

# Ruta para analizar facturas y pagos en formato XML
@app.route('/analizar_facturas_pagos_xml', methods=['GET'])
def mostrar_analisis_facturas_pagos_xml():
    # Obtener resultados del análisis
    xml_data = analizar_facturas_pagos(facturas_acumulativas, pagos_acumulativos)

    # Devolver los resultados como XML
    return Response(xml_data, mimetype='text/xml')

@app.route('/borrardatos', methods=['DELETE'])
def borrar_datos():
    global clientes_acumulativos, bancos_acumulativos, pagos_acumulativos, facturas_acumulativas
    clientes_acumulativos = []
    bancos_acumulativos = []
    pagos_acumulativos = []
    facturas_acumulativas = []
    return 'Datos borrados correctamente', 200

@app.route('/mostrarclientes', methods=['GET'])
def mostrar_clientes():
    # Función para extraer solo los dígitos de un NIT
    def extraer_digitos(nit):
        numeros = re.findall(r'\d+', nit)
        if numeros:
            return int(numeros[0])
        else:
            return float('inf')  # Retorna infinito si no se encuentran números en el NIT

    # Ordenar los clientes por los dígitos del NIT de menor a mayor
    clientes_ordenados = sorted(clientes_acumulativos, key=lambda x: extraer_digitos(x.nit))

    # Crear la lista de resultados
    resultado = [{"nit": cliente.nit, "nombre": cliente.nombre} for cliente in clientes_ordenados]
    return jsonify(resultado)


def obtener_datos_cuenta(nit):
    resultados = []

    # Filtrar las facturas y pagos correspondientes al NIT proporcionado
    facturas_cliente = [factura for factura in facturas_acumulativas if factura.nit_cliente == nit]
    pagos_cliente = [pago for pago in pagos_acumulativos if pago.nit_cliente == nit]

    # Iterar sobre las facturas del cliente
    for factura in facturas_cliente:
        # Buscar el pago correspondiente a esta factura
        pago_correspondiente = next((pago for pago in pagos_cliente if pago.fecha >= factura.fecha), None)
        if pago_correspondiente:
            # Obtener detalles adicionales
            cliente = next((c for c in clientes_acumulativos if c.nit == nit), None)
            nombre_banco = next((b.nombre for b in bancos_acumulativos if b.codigo == pago_correspondiente.codigo_banco), None)
            saldo = pago_correspondiente.valor - factura.valor
            saldo_texto = f'{saldo} aún debe' if saldo < 0 else saldo
            # Crear un diccionario con los detalles y agregarlo a los resultados
            resultado = {
                'nit_cliente': factura.nit_cliente,
                'nombre_cliente': cliente.nombre if cliente else "",
                'fecha_factura': factura.fecha,
                'cantidad_factura': factura.valor,
                'fecha_pago': pago_correspondiente.fecha,
                'cantidad_pago': pago_correspondiente.valor,
                'nombre_banco': nombre_banco,
                'saldo': saldo_texto
            }
            resultados.append(resultado)

    # Ordenar los resultados por fecha de pago de forma descendente (de más reciente a más antigua)
    resultados = sorted(resultados, key=lambda x: x['fecha_pago'], reverse=True)

    return resultados

@app.route('/consulta_cuenta', methods=['GET'])
def consulta_cuenta():
    nit = request.args.get('nit', '')
    # Lógica para obtener los datos de la cuenta usando la función obtener_datos_cuenta(nit)
    datos_cuenta = obtener_datos_cuenta(nit)
    return jsonify(datos_cuenta)



if __name__ == '__main__':
    app.run(debug=True, port=4000)
