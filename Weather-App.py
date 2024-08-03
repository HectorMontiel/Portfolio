import sys
import requests
import PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QStackedWidget, QWidget, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect

class ClimaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_key = "27928c70d4eda4a2a42836e9ad6d84b7"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Aplicación del Clima")
        self.setGeometry(100, 100, 400, 300)

        # Crear el widget principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Crear el QStackedWidget para cambiar entre escenas
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)

        # Crear las escenas
        self.main_scene = QWidget()
        self.setup_main_scene()
        self.stack.addWidget(self.main_scene)

        self.loading_scene = QLabel("Cargando...", self)
        self.loading_scene.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(self.loading_scene)

        self.result_scene = QWidget()
        self.setup_result_scene()
        self.stack.addWidget(self.result_scene)

        # Mostrar la escena principal por defecto
        self.stack.setCurrentWidget(self.main_scene)

    def setup_main_scene(self):
        layout = QVBoxLayout(self.main_scene)

        self.ciudad_input = QLineEdit(self)
        self.ciudad_input.setPlaceholderText("Introduce el nombre de la ciudad")
        layout.addWidget(self.ciudad_input)

        self.boton_obtener = QPushButton("Obtener Clima", self)
        self.boton_obtener.clicked.connect(self.mostrar_clima)
        layout.addWidget(self.boton_obtener)

    def setup_result_scene(self):
        self.result_layout = QVBoxLayout(self.result_scene)
        self.result_label = QLabel("", self)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_layout.addWidget(self.result_label)

    def obtener_datos_clima(self, ciudad):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={self.api_key}&units=metric"
        respuesta = requests.get(url)
        datos = respuesta.json()
        return datos

    def mostrar_clima(self):
        ciudad = self.ciudad_input.text()
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

        # Cambiar la imagen de fondo según el clima
        imagen = QPixmap(f"http://openweathermap.org/img/wn/{icono}@2x.png")
        self.result_label.setPixmap(imagen)

        self.result_label.setText((
            f"Ciudad: {ciudad}\n"
            f"Temperatura: {temperatura}°C\n"
            f"Descripción: {descripcion.capitalize()}\n"
            f"Humedad: {humedad}%"
        ))

        self.transition_to_scene(self.result_scene)

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
