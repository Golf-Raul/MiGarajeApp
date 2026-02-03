from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.core.window import Window

# Configuración visual
Window.clearcolor = (0.95, 0.95, 0.95, 1)

class PantallaBase(Screen):
    """Clase base con la firma de Raul Plaza incorporada"""
    def crear_layout(self, titulo):
        # Layout principal
        self.main_layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        
        # Título de la sección
        self.main_layout.add_widget(Label(text=titulo, font_size=24, color=(0,0,0,1), bold=True, size_hint_y=None, height=80))
        
        # Contenedor para el contenido (para que la firma quede abajo)
        self.content_layout = BoxLayout(orientation='vertical', spacing=15)
        self.main_layout.add_widget(self.content_layout)
        
        # FIRMA DE AUTOR (Raul Plaza)
        self.main_layout.add_widget(Label(
            text="Creado por Raul Plaza", 
            font_size=14, 
            color=(0.6, 0.6, 0.6, 1), 
            size_hint_y=None, 
            height=50,
            italic=True
        ))
        return self.main_layout

    def boton_sig(self, texto="SIGUIENTE"):
        return Button(text=texto, size_hint_y=None, height=100, background_color=(0.1, 0.6, 0.1, 1), bold=True)

    def boton_atras(self):
        return Button(text="ATRÁS", size_hint_y=None, height=100, background_color=(0.7, 0.2, 0.2, 1))

# --- PASO 1: DATOS ---
class PantallaDatos(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = self.crear_layout("PASO 1: VEHÍCULO")
        
        self.modelo = TextInput(hint_text="Modelo (Ej: Seat Leon)", multiline=False, size_hint_y=None, height=100)
        self.matricula = TextInput(hint_text="Matrícula", multiline=False, size_hint_y=None, height=100)
        
        self.content_layout.add_widget(self.modelo)
        self.content_layout.add_widget(self.matricula)
        
        btn = self.boton_sig()
        btn.bind(on_press=self.validar)
        self.content_layout.add_widget(btn)
        self.add_widget(layout)

    def validar(self, instance):
        if self.modelo.text and self.matricula.text:
            self.manager.current = 'motor'
        else:
            self.modelo.hint_text = "¡RELLENA ESTO!"

# --- PASO 2: MOTOR ---
class PantallaMotor(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = self.crear_layout("PASO 2: MOTOR")
        
        self.distri = CheckBox(color=(0,0,0,1))
        self.content_layout.add_widget(BoxLayout(orientation='horizontal', children=[Label(text="¿Distribución hecha?", color=(0,0,0,1)), self.distri]))
        
        self.aceite = CheckBox(color=(0,0,0,1))
        self.content_layout.add_widget(BoxLayout(orientation='horizontal', children=[Label(text="¿Aceite y filtros?", color=(0,0,0,1)), self.aceite]))
        
        btns = BoxLayout(spacing=10, size_hint_y=None, height=100)
        btn_a = self.boton_atras()
        btn_a.bind(on_press=lambda x: setattr(self.manager, 'current', 'datos'))
        btn_s = self.boton_sig()
        btn_s.bind(on_press=lambda x: setattr(self.manager, 'current', 'seguridad'))
        
        btns.add_widget(btn_a); btns.add_widget(btn_s)
        self.content_layout.add_widget(btns)
        self.add_widget(layout)

# --- PASO 3: SEGURIDAD ---
class PantallaSeguridad(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = self.crear_layout("PASO 3: SEGURIDAD")
        
        self.frenos = CheckBox(color=(0,0,0,1))
        self.content_layout.add_widget(BoxLayout(orientation='horizontal', children=[Label(text="Revisión de Frenos", color=(0,0,0,1)), self.frenos]))
        
        btns = BoxLayout(spacing=10, size_hint_y=None, height=100)
        btn_a = self.boton_atras()
        btn_a.bind(on_press=lambda x: setattr(self.manager, 'current', 'motor'))
        btn_s = self.boton_sig()
        btn_s.bind(on_press=lambda x: setattr(self.manager, 'current', 'gastos'))
        
        btns.add_widget(btn_a); btns.add_widget(btn_s)
        self.content_layout.add_widget(btns)
        self.add_widget(layout)

# --- PASO 4: GASTOS ---
class PantallaGastos(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = self.crear_layout("PASO 4: REPARACIONES")
        
        self.desc = TextInput(hint_text="Descripción avería", size_hint_y=None, height=150)
        self.coste = TextInput(hint_text="Coste en €", multiline=False, size_hint_y=None, height=100, input_filter='float')
        
        self.content_layout.add_widget(self.desc)
        self.content_layout.add_widget(self.coste)
        
        btns = BoxLayout(spacing=10, size_hint_y=None, height=100)
        btn_a = self.boton_atras()
        btn_a.bind(on_press=lambda x: setattr(self.manager, 'current', 'seguridad'))
        btn_f = self.boton_sig("FINALIZAR")
        btn_f.bind(on_press=self.finalizar)
        
        btns.add_widget(btn_a); btns.add_widget(btn_f)
        self.content_layout.add_widget(btns)
        self.add_widget(layout)

    def finalizar(self, instance):
        print("Guardando datos... Creado por Raul Plaza")
        App.get_running_app().stop()

class MiGarajeApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(PantallaDatos(name='datos'))
        sm.add_widget(PantallaMotor(name='motor'))
        sm.add_widget(PantallaSeguridad(name='seguridad'))
        sm.add_widget(PantallaGastos(name='gastos'))
        return sm

if __name__ == "__main__":
    MiGarajeApp().run()
