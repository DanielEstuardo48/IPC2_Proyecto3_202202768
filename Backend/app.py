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

# Mantenemos los datos en memoria en lugar de escribir en disco
clientes_acumulativos = []
bancos_acumulativos = []

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



if __name__ == '__main__':
    app.run(debug=True, port=4000)
