import sqlite3
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

# Configuración de color de fondo
Window.clearcolor = (0.95, 0.95, 0.95, 1)

# --- BASE DE DATOS ---
def conectar_bd():
    conn = sqlite3.connect('mantenimiento_raul.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS fichas 
                      (id INTEGER PRIMARY KEY, nombre TEXT, modelo TEXT, matricula TEXT, 
                       motor TEXT, seguridad TEXT, averia TEXT, coste TEXT)''')
    conn.commit()
    return conn

# --- CLASE BASE PARA DISEÑO ---
class PantallaBase(Screen):
    def crear_layout(self, titulo):
        main_layout = BoxLayout(orientation='vertical', padding=10)
        # Título
        main_layout.add_widget(Label(text=titulo, font_size=22, color=(0,0,0,1), bold=True, size_hint_y=None, height=60))
        
        # Scroll para que quepa todo en el móvil
        self.scroll = ScrollView(size_hint=(1, 1))
        self.content_layout = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None, padding=20)
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        
        self.scroll.add_widget(self.content_layout)
        main_layout.add_widget(self.scroll)
        
        # Firma de Raul Plaza
        main_layout.add_widget(Label(text="Creado por Raul Plaza", font_size=12, color=(0.6, 0.6, 0.6, 1), size_hint_y=None, height=40, italic=True))
        return main_layout

# --- PANTALLA 1: DATOS ---
class PantallaDatos(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = self.crear_layout("PASO 1: IDENTIFICACIÓN")
        
        self.nombre = TextInput(hint_text="Nombre del dueño", multiline=False, size_hint_y=None, height=90)
        self.modelo = TextInput(hint_text="Modelo de coche", multiline=False, size_hint_y=None, height=90)
        self.matricula = TextInput(hint_text="Matrícula", multiline=False, size_hint_y=None, height=90)
        
        self.content_layout.add_widget(self.nombre)
        self.content_layout.add_widget(self.modelo)
        self.content_layout.add_widget(self.matricula)
        
        btn_sig = Button(text="SIGUIENTE", size_hint_y=None, height=100, background_color=(0.1, 0.6, 0.1, 1), bold=True)
        btn_sig.bind(on_press=self.ir_a_motor)
        self.content_layout.add_widget(btn_sig)

        btn_hist = Button(text="VER HISTORIAL / BUSCAR", size_hint_y=None, height=100, background_color=(0.2, 0.4, 0.8, 1))
        btn_hist.bind(on_press=lambda x: setattr(self.manager, 'current', 'historial'))
        self.content_layout.add_widget(btn_hist)
        
        self.add_widget(layout)

    def ir_a_motor(self, instance):
        if self.nombre.text and self.matricula.text:
            app = App.get_running_app()
            app.datos_temp = {'nombre': self.nombre.text, 'modelo': self.modelo.text, 'matricula': self.matricula.text}
            self.manager.current = 'motor'

# --- PANTALLA 2: MOTOR ---
class PantallaMotor(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = self.crear_layout("PASO 2: REVISIÓN MOTOR")
        
        self.check_aceite = CheckBox(color=(0,0,0,1), size_hint_y=None, height=50)
        self.content_layout.add_widget(Label(text="Aceite y Filtros OK?", color=(0,0,0,1)))
        self.content_layout.add_widget(self.check_aceite)
        
        btn_sig = Button(text="SIGUIENTE", size_hint_y=None, height=100, background_color=(0.1, 0.6, 0.1, 1))
        btn_sig.bind(on_press=lambda x: setattr(self.manager, 'current', 'gastos'))
        self.content_layout.add_widget(btn_sig)
        self.add_widget(layout)

# --- PANTALLA 4: GASTOS ---
class PantallaGastos(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = self.crear_layout("PASO 3: GASTOS")
        
        self.reparacion = TextInput(hint_text="¿Qué se le ha hecho?", size_hint_y=None, height=150)
        self.coste = TextInput(hint_text="Coste en €", multiline=False, size_hint_y=None, height=90, input_filter='float')
        
        self.content_layout.add_widget(self.reparacion)
        self.content_layout.add_widget(self.coste)
        
        btn_guardar = Button(text="GUARDAR FICHA", size_hint_y=None, height=110, background_color=(0, 0.7, 0, 1), bold=True)
        btn_guardar.bind(on_press=self.guardar_final)
        self.content_layout.add_widget(btn_guardar)
        self.add_widget(layout)

    def guardar_final(self, instance):
        app = App.get_running_app()
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO fichas (nombre, modelo, matricula, averia, coste) VALUES (?,?,?,?,?)",
                       (app.datos_temp['nombre'], app.datos_temp['modelo'], app.datos_temp['matricula'], 
                        self.reparacion.text, self.coste.text))
        conn.commit()
        conn.close()
        self.manager.current = 'historial'

# --- PANTALLA HISTORIAL CON BUSCADOR ---
class PantallaHistorial(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = self.crear_layout("HISTORIAL Y BÚSQUEDA")
        
        self.buscador = TextInput(hint_text="🔍 Busca por Matrícula o Nombre...", size_hint_y=None, height=80, multiline=False)
        self.buscador.bind(text=self.filtrar)
        
        # El buscador va arriba del contenido
        self.content_layout.add_widget(self.buscador)
        self.lista_fichas = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.lista_fichas.bind(minimum_height=self.lista_fichas.setter('height'))
        self.content_layout.add_widget(self.lista_fichas)
        
        btn_volver = Button(text="VOLVER AL INICIO", size_hint_y=None, height=90)
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'datos'))
        self.content_layout.add_widget(btn_volver)
        
        self.add_widget(layout)

    def on_enter(self):
        self.cargar_datos()

    def filtrar(self, instance, value):
        self.cargar_datos(value)

    def cargar_datos(self, filtro=""):
        self.lista_fichas.clear_widgets()
        conn = conectar_bd()
        cursor = conn.cursor()
        if filtro:
            cursor.execute("SELECT * FROM fichas WHERE nombre LIKE ? OR matricula LIKE ?", (f'%{filtro}%', f'%{filtro}%'))
        else:
            cursor.execute("SELECT * FROM fichas ORDER BY id DESC")
        
        for f in cursor.fetchall():
            resumen = f"Dueño: {f[1]} | Mat: {f[3]}\nRep: {f[6]} | Coste: {f[7]}€"
            self.lista_fichas.add_widget(Label(text=resumen, color=(0,0,0,1), size_hint_y=None, height=100))
        conn.close()

# --- APP PRINCIPAL ---
class MiGarajeApp(App):
    datos_temp = {}
    def build(self):
        conectar_bd()
        sm = ScreenManager()
        sm.add_widget(PantallaDatos(name='datos'))
        sm.add_widget(PantallaMotor(name='motor'))
        sm.add_widget(PantallaGastos(name='gastos'))
        sm.add_widget(PantallaHistorial(name='historial'))
        return sm

if __name__ == "__main__":
    MiGarajeApp().run()
