import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QComboBox, QPushButton, QStackedWidget, 
                             QWidget, QVBoxLayout, QListWidget)
from PyQt5.QtCore import QPropertyAnimation, QRect, Qt
from PyQt5.QtGui import QFont
import requests

class ClimaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_key = "27928c70d4eda4a2a42836e9ad6d84b7"
        self.init_data()
        self.init_ui()

    def init_data(self):
        self.continentes_paises = self.obtener_continentes_paises()
        self.continentes = list(self.continentes_paises.keys())

        # Datos estáticos para ciudades importantes
        self.ciudades_importantes = {
            "United States": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
            "Canada": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"],
            "Germany": ["Berlin", "Munich", "Frankfurt", "Hamburg", "Cologne"],
            "France": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice"],
            "Japan": ["Tokyo", "Osaka", "Nagoya", "Yokohama", "Fukuoka"],
            "Mexico": ["Mexico City", "Guadalajara", "Monterrey", "Puebla", "Cancún"],
            # Agrega más países y ciudades según sea necesario
        }

    def init_ui(self):
        self.setWindowTitle("Weather App")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #2E2E2E; color: #FFFFFF;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)

        self.main_scene = QWidget()
        self.setup_main_scene()
        self.stack.addWidget(self.main_scene)

        self.loading_scene = QLabel("Loading...", self)
        self.loading_scene.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(self.loading_scene)

        self.result_scene = QWidget()
        self.setup_result_scene()
        self.stack.addWidget(self.result_scene)

        self.stack.setCurrentWidget(self.main_scene)

    def setup_main_scene(self):
        layout = QVBoxLayout(self.main_scene)
        layout.setContentsMargins(20, 20, 20, 20)

        self.continente_input = QComboBox(self)
        self.continente_input.addItems(self.continentes)
        self.continente_input.currentIndexChanged.connect(self.actualizar_paises)
        layout.addWidget(self.continente_input)

        self.pais_input = QComboBox(self)
        self.pais_input.currentIndexChanged.connect(self.actualizar_ciudades)
        layout.addWidget(self.pais_input)

        self.ciudad_list = QListWidget(self)
        layout.addWidget(self.ciudad_list)

        self.boton_obtener = QPushButton("Get Weather", self)
        self.boton_obtener.clicked.connect(self.mostrar_clima)
        layout.addWidget(self.boton_obtener)

        self.actualizar_paises()

    def setup_result_scene(self):
        self.result_layout = QVBoxLayout(self.result_scene)
        self.result_layout.setContentsMargins(20, 20, 20, 20)

        self.result_label = QLabel("", self)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.result_layout.addWidget(self.result_label)

        self.back_button = QPushButton("Back", self)
        self.back_button.clicked.connect(self.volver_a_inicio)
        self.result_layout.addWidget(self.back_button)

    def obtener_continentes_paises(self):
        url = "https://restcountries.com/v3.1/all"
        try:
            respuesta = requests.get(url, verify=False)
            datos = respuesta.json()
        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud: {e}")
            return {}

        continentes_paises = {}
        for pais in datos:
            continente = pais.get('region', 'Unknown')
            nombre_pais = pais['name']['common']
            if continente not in continentes_paises:
                continentes_paises[continente] = []
            continentes_paises[continente].append(nombre_pais)

        return continentes_paises

    def obtener_ciudades(self, pais):
        return self.ciudades_importantes.get(pais, ["No data available"])

    def actualizar_paises(self):
        continente_seleccionado = self.continente_input.currentText()
        paises = self.continentes_paises.get(continente_seleccionado, [])
        self.pais_input.clear()
        self.pais_input.addItems(paises)
        self.actualizar_ciudades()

    def actualizar_ciudades(self):
        pais_seleccionado = self.pais_input.currentText()
        ciudades = self.obtener_ciudades(pais_seleccionado)
        self.ciudad_list.clear()
        self.ciudad_list.addItems(ciudades)

    def obtener_datos_clima(self, ciudad):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={self.api_key}&units=metric"
        respuesta = requests.get(url)
        datos = respuesta.json()
        return datos

    def mostrar_clima(self):
        ciudad = self.ciudad_list.currentItem().text()
        self.stack.setCurrentWidget(self.loading_scene)
        datos_clima = self.obtener_datos_clima(ciudad)

        if datos_clima.get('cod') != 200:
            self.result_label.setText(f"Error: {datos_clima.get('message')}")
            self.stack.setCurrentWidget(self.result_scene)
            return

        ciudad = datos_clima['name']
        temperatura = datos_clima['main']['temp']
        descripcion = datos_clima['weather'][0]['description']
        humedad = datos_clima['main']['humidity']
        icono = datos_clima['weather'][0]['icon']

        fondo = self.obtener_fondo_por_icono(icono)
        self.result_scene.setStyleSheet(f"""
            background-image: url({fondo});
            background-repeat: no-repeat;
            background-position: center;
            background-size: cover;
        """)

        self.result_label.setText((
            f"City: {ciudad}\n"
            f"Temperature: {temperatura}°C\n"
            f"Description: {descripcion.capitalize()}\n"
            f"Humidity: {humedad}%"
        ))

        self.transition_to_scene(self.result_scene)

    def obtener_fondo_por_icono(self, icono):
        icono_a_fondo = {
            "01d": "backgrounds/clear_day.jpg",
            "01n": "backgrounds/clear_night.jpg",
            "02d": "backgrounds/partly_cloudy_day.jpg",
            "02n": "backgrounds/partly_cloudy_night.jpg",
            "03d": "backgrounds/cloudy.jpg",
            "03n": "backgrounds/cloudy.jpg",
            "04d": "backgrounds/overcast.jpg",
            "04n": "backgrounds/overcast.jpg",
            "09d": "backgrounds/rain.jpg",
            "09n": "backgrounds/rain.jpg",
            "10d": "backgrounds/rain_day.jpg",
            "10n": "backgrounds/rain_night.jpg",
            "11d": "backgrounds/storm.jpg",
            "11n": "backgrounds/storm.jpg",
            "13d": "backgrounds/snow.jpg",
            "13n": "backgrounds/snow.jpg",
            "50d": "backgrounds/fog.jpg",
            "50n": "backgrounds/fog.jpg",
        }
        return icono_a_fondo.get(icono, "backgrounds/default.jpg")

    def volver_a_inicio(self):
        self.stack.setCurrentWidget(self.main_scene)

    def transition_to_scene(self, scene):
        self.stack.setCurrentWidget(scene)
        self.animation = QPropertyAnimation(self.stack, b"geometry")
        self.animation.setDuration(500)
        self.animation.setStartValue(QRect(self.stack.geometry().width(), 0, self.stack.geometry().width(), self.stack.geometry().height()))
        self.animation.setEndValue(QRect(0, 0, self.stack.geometry().width(), self.stack.geometry().height()))
        self.animation.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClimaApp()
    window.show()
    sys.exit(app.exec_())
