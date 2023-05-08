from flask import Flask, render_template, request, jsonify
import psycopg2
import folium

app = Flask(__name__)

# Configuración de la conexión a la base de datos
conn = psycopg2.connect(
    host="localhost",
    database="parking",
    user="postgres",
    password="postgres"
)

# Ruta para registrar la información de un nuevo bus
@app.route('/registrar_bus', methods=['POST'])
def registrar_bus():
    cursor = conn.cursor()

    # Recuperar los datos del formulario
    origen = request.form['origen']
    destino = request.form['destino']
    hora_salida = request.form['hora_salida']
    hora_llegada = request.form['hora_llegada']
    tiempo_estadia = request.form['tiempo_estadia']
    latitud = float(request.form['latitud'])
    longitud = float(request.form['longitud'])

    # Insertar los datos en la tabla buses
    cursor.execute("INSERT INTO buses (origen, destino, hora_salida, hora_llegada, tiempo_estadia, ubicacion) VALUES (%s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))",
                   (origen, destino, hora_salida, hora_llegada, tiempo_estadia, longitud, latitud))
    conn.commit()

    return jsonify({'mensaje': 'Bus registrado correctamente.'})

# Ruta para visualizar el mapa interactivo
@app.route('/')
def mapa_interactivo():
    cursor = conn.cursor()

    # Obtener la información de los aparcaderos y buses
    cursor.execute("SELECT ST_Y(ubicacion), ST_X(ubicacion), origen, destino, hora_salida, hora_llegada, tiempo_estadia FROM buses")
    datos = cursor.fetchall()

        # Crear el mapa interactivo con folium
    mapa = folium.Map(location=[4.60971, -74.08175], zoom_start=13)

    # Agregar un marcador para cada aparcadero y bus
    for dato in datos:
        latitud, longitud, origen, destino, hora_salida, hora_llegada, tiempo_estadia = dato

        # Crear el marcador del aparcadero o bus
        popup = folium.Popup(f"<b>Origen:</b> {origen}<br><b>Destino:</b> {destino}<br><b>Hora de salida:</b> {hora_salida}<br><b>Hora de llegada:</b> {hora_llegada}<br><b>Tiempo de estadía:</b> {tiempo_estadia}", max_width=400)
        if origen == "Aparcadero":
            icono = folium.Icon(color='blue', icon='car')
        else:
            icono = folium.Icon(color='red', icon='bus')

        # Agregar el marcador al mapa
        folium.Marker(location=[latitud, longitud], popup=popup, icon=icono).add_to(mapa)

    # Renderizar la plantilla HTML con el mapa interactivo
    return render_template('mapa.html', mapa=mapa._repr_html_())

if __name__ == "__main__":
    app.run(debug=True)