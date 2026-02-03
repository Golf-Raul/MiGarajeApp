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

# Configuración de ventana
Window.clearcolor = (0.95, 0.95, 0.95, 1)

# --- BASE DE DATOS COMPLETA ---
def conectar_bd():
    conn = sqlite3.connect('mantenimiento_raul.db')
    cursor = conn.cursor()
    # Creamos la tabla con TODOS los campos que necesitas
    cursor.execute('''CREATE TABLE IF NOT EXISTS fichas 
                      (id INTEGER PRIMARY KEY, modelo TEXT, matricula TEXT, km_act TEXT,
                       distri_chk TEXT, distri_km TEXT, aceite_chk TEXT, aceite_det TEXT, aceite_km TEXT,
                       caja_chk TEXT, caja_det TEXT, caja_km TEXT,
                       f_aire TEXT, f_aceite TEXT, f_polen TEXT, f_comb TEXT, 
                       luces TEXT, agua TEXT, frenos TEXT,
                       ruedas_del_chk TEXT, ruedas_del_km TEXT, ruedas_tra_chk TEXT, ruedas_tra_km TEXT,
                       averia TEXT, coste TEXT, fecha TEXT)''')
    conn.commit()
    return conn

# --- CLASE BASE ---
class PantallaBase(Screen):
    def crear_layout(self, titulo):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(Label(text=titulo, font_size=22, bold=True, color=(0.1, 0.2, 0.4, 1), size_hint_y=None, height=60))
        self.scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=[10, 20])
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        layout.add_widget(self.scroll)
        return layout

    def seccion(self, titulo):
        self.content.add_widget(Label(text=titulo, color=(0.1, 0.4, 0.8, 1), bold=True, size_hint_y=None, height=40))

    def input(self, placeholder, alto=70, multi=False):
        ti = TextInput(hint_text=placeholder, multiline=multi, size_hint_y=None, height=alto, padding=[10, 15])
        self.content.add_widget(ti)
        return ti

    def check(self, texto):
        box = BoxLayout(orientation='horizontal', size_hint_y=None, height=45)
        box.add_widget(Label(text=texto, color=(0,0,0,1)))
        cb = CheckBox(color=(0,0,0,1), size_hint_x=None, width=50)
        box.add_widget(cb)
        self.content.add_widget(box)
        return cb

# --- PÁGINAS ---
class PaginaUno(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = self.crear_layout("1. DATOS VEHÍCULO")
        self.seccion("DATOS VEHÍCULO")
        self.txt_modelo = self.input("Modelo")
        self.txt_matri = self.input("Matrícula")
        self.txt_km_act = self.input("Km actuales")
        
        btn = Button(text="SIGUIENTE", size_hint_y=None, height=80, background_color=(0.1, 0.5, 0.1, 1), bold=True)
        btn.bind(on_press=self.siguiente)
        self.content.add_widget(btn)
        self.add_widget(layout)

    def siguiente(self, x):
        app = App.get_running_app()
        app.f_temp.update({'mod': self.txt_modelo.text, 'mat': self.txt_matri.text, 'km': self.txt_km_act.text})
        self.manager.current = 'pag2'

class PaginaDos(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = self.crear_layout("2. DISTRIBUCIÓN Y ACEITES")
        self.seccion("KIT DISTRIBUCIÓN")
        self.chk_distri = self.check("Cambiado")
        self.txt_distri_km = self.input("Km del cambio")
        self.seccion("ACEITE MOTOR")
        self.chk_aceite = self.check("Cambiado")
        self.txt_aceite_det = self.input("Marca y Densidad")
        self.txt_aceite_km = self.input("Km del cambio")
        self.seccion("ACEITE CAJA")
        self.chk_caja = self.check("Cambiado")
        self.txt_caja_det = self.input("Marca y Densidad")
        self.txt_caja_km = self.input("Km del cambio")

        btns = BoxLayout(size_hint_y=None, height=80, spacing=10)
        btn_back = Button(text="VOLVER", background_color=(0.7, 0.2, 0.2, 1))
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag1'))
        btn_next = Button(text="SIGUIENTE", background_color=(0.1, 0.5, 0.1, 1))
        btn_next.bind(on_press=self.siguiente)
        btns.add_widget(btn_back); btns.add_widget(btn_next)
        self.content.add_widget(btns)
        self.add_widget(layout)

    def siguiente(self, x):
        app = App.get_running_app()
        app.f_temp.update({
            'd_c': str(self.chk_distri.active), 'd_k': self.txt_distri_km.text,
            'a_c': str(self.chk_aceite.active), 'a_d': self.txt_aceite_det.text, 'a_k': self.txt_aceite_km.text,
            'c_c': str(self.chk_caja.active), 'c_d': self.txt_caja_det.text, 'c_k': self.txt_caja_km.text
        })
        self.manager.current = 'pag3'

class PaginaTres(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = self.crear_layout("3. REVISIÓN Y SEGURIDAD")
        self.seccion("FILTROS Y REVISIONES")
        self.chk_f_aire = self.check("Filtro Aire")
        self.chk_f_aceite = self.check("Filtro Aceite")
        self.chk_f_polen = self.check("Filtro Polen")
        self.chk_f_comb = self.check("Filtro Combustible")
        self.chk_luces = self.check("Luces")
        self.chk_agua = self.check("Agua Limpia")
        self.seccion("SEGURIDAD Y RUEDAS")
        self.chk_frenos = self.check("Revisión Frenos")
        self.chk_r_del = self.check("Ruedas Delanteras")
        self.txt_r_km_del = self.input("Km cambio ruedas delanteras")
        self.chk_r_tra = self.check("Ruedas Traseras")
        self.txt_r_km_tra = self.input("Km cambio ruedas traseras")

        btns = BoxLayout(size_hint_y=None, height=80, spacing=10)
        btn_back = Button(text="VOLVER", background_color=(0.7, 0.2, 0.2, 1))
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag2'))
        btn_next = Button(text="SIGUIENTE", background_color=(0.1, 0.5, 0.1, 1))
        btn_next.bind(on_press=self.siguiente)
        btns.add_widget(btn_back); btns.add_widget(btn_next)
        self.content.add_widget(btns)
        self.add_widget(layout)

    def siguiente(self, x):
        app = App.get_running_app()
        app.f_temp.update({
            'f_ai': str(self.chk_f_aire.active), 'f_ac': str(self.chk_f_aceite.active),
            'f_po': str(self.chk_f_polen.active), 'f_co': str(self.chk_f_comb.active),
            'luc': str(self.chk_luces.active), 'agu': str(self.chk_agua.active),
            'fre': str(self.chk_frenos.active), 'rd_c': str(self.chk_r_del.active),
            'rd_k': self.txt_r_km_del.text, 'rt_c': str(self.chk_r_tra.active), 'rt_k': self.txt_r_km_tra.text
        })
        self.manager.current = 'pag4'

class PaginaCuatro(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = self.crear_layout("4. AVERÍAS Y COSTES")
        self.seccion("AVERÍAS REPARADAS")
        self.txt_averia = self.input("Detalle de las averías...", alto=250, multi=True)
        self.seccion("CIERRE")
        self.txt_coste = self.input("Importe Total (€)")
        self.txt_fecha = self.input("Fecha (DD/MM/AAAA)")
        
        btns = BoxLayout(size_hint_y=None, height=90, spacing=10)
        btn_back = Button(text="VOLVER", background_color=(0.7, 0.2, 0.2, 1))
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag3'))
        btn_save = Button(text="GUARDAR TODO", background_color=(0, 0.6, 0, 1), bold=True)
        btn_save.bind(on_press=self.finalizar)
        btns.add_widget(btn_back); btns.add_widget(btn_save)
        self.content.add_widget(btns)
        self.add_widget(layout)

    def finalizar(self, x):
        app = App.get_running_app()
        conn = conectar_bd()
        cursor = conn.cursor()
        t = app.f_temp
        cursor.execute('''INSERT INTO fichas VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', 
                       (t['mod'], t['mat'], t['km'], t['d_c'], t['d_k'], t['a_c'], t['a_d'], t['a_k'],
                        t['c_c'], t['c_d'], t['c_k'], t['f_ai'], t['f_ac'], t['f_po'], t['f_co'],
                        t['luc'], t['agu'], t['fre'], t['rd_c'], t['rd_k'], t['rt_c'], t['rt_k'],
                        self.txt_averia.text, self.txt_coste.text, self.txt_fecha.text))
        conn.commit()
        conn.close()
        app.f_temp = {}
        self.manager.current = 'pag1'

class MiGarajeApp(App):
    f_temp = {}
    def build(self):
        conectar_bd()
        sm = ScreenManager()
        sm.add_widget(PaginaUno(name='pag1'))
        sm.add_widget(PaginaDos(name='pag2'))
        sm.add_widget(PaginaTres(name='pag3'))
        sm.add_widget(PaginaCuatro(name='pag4'))
        return sm

if __name__ == "__main__":
    MiGarajeApp().run()
