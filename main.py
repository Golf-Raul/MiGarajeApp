from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.core.window import Window
from kivy.metrics import dp
import os

# Color de fondo gris claro
Window.clearcolor = (0.94, 0.94, 0.94, 1)

class MiGarajeApp(App):
    def build(self):
        self.title = "Mi Garaje"
        root = ScrollView()
        self.layout = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(20), spacing=dp(10))
        self.layout.bind(minimum_height=self.layout.setter('height'))

        # --- SECCIONES ---
        self.agregar_seccion("DATOS DEL VEHICULO", (0.2, 0.2, 0.2, 1))
        self.txt_modelo = self.agregar_input("Modelo / Marca")
        self.txt_matri = self.agregar_input("Matrícula")
        self.txt_km_act = self.agregar_input("Km actuales")

        self.agregar_seccion("MANTENIMIENTO", (0.1, 0.4, 0.7, 1))
        self.chk_distri = self.agregar_check("Kit Distribución Cambiado")
        self.txt_distri_km = self.agregar_input("Km del cambio")
        self.chk_aceite = self.agregar_check("Aceite Motor Cambiado")
        self.txt_aceite_det = self.agregar_input("Marca y Densidad Aceite")

        self.agregar_seccion("FILTROS", (0.1, 0.6, 0.3, 1))
        self.chk_f_aire = self.agregar_check("Filtro Aire")
        self.chk_f_aceite = self.agregar_check("Filtro Aceite")
        self.chk_f_polen = self.agregar_check("Filtro Polen")

        self.agregar_seccion("GASTOS Y AVERIAS", (0.7, 0.1, 0.1, 1))
        self.txt_averia = self.agregar_input("Descripción (Avería/Nota)")
        self.txt_coste = self.agregar_input("Importe (€)")
        self.txt_fecha = self.agregar_input("Fecha (DD/MM/AAAA)")

        # BOTÓN GUARDAR
        btn = Button(text="GUARDAR REGISTRO", size_hint_y=None, height=dp(60),
                     background_color=(0.1, 0.45, 0.9, 1), bold=True)
        btn.bind(on_press=self.guardar)
        self.layout.add_widget(btn)

        root.add_widget(self.layout)
        return root

    def agregar_seccion(self, texto, color):
        lbl = Label(text=texto, bold=True, color=(1,1,1,1), size_hint_y=None, 
                    height=dp(40), outline_width=1)
        # Fondo simulado para la sección
        self.layout.add_widget(lbl)

    def agregar_input(self, etiqueta):
        self.layout.add_widget(Label(text=etiqueta, color=(0,0,0,1), size_hint_y=None, height=dp(20), halign="left"))
        i = TextInput(multiline=False, size_hint_y=None, height=dp(40))
        self.layout.add_widget(i)
        return i

    def agregar_check(self, texto):
        box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        box.add_widget(Label(text=texto, color=(0,0,0,1)))
        c = CheckBox(color=(0,0,0,1))
        box.add_widget(c)
        self.layout.add_widget(box)
        return c

    def guardar(self, instance):
        # Guardar en la carpeta de datos de la app en el móvil
        path = os.path.join(self.user_data_dir, "mantenimiento_coches.txt")
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"Fecha: {self.txt_fecha.text} | Coche: {self.txt_modelo.text} | Coste: {self.txt_coste.text}€\\n")
        self.txt_modelo.text = "¡GUARDADO!"

if __name__ == '__main__':
    MiGarajeApp().run()
