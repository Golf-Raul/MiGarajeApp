import sqlite3
import os
from datetime import datetime
from kivy.config import Config

Config.set('graphics', 'resizable', '1')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

try:
    from fpdf import FPDF
    PDF_DISPONIBLE = True
except ImportError:
    PDF_DISPONIBLE = False

Window.clearcolor = (0.9, 0.9, 0.9, 1)

def conectar_bd():
    directorio = App.get_running_app().user_data_dir
    ruta_db = os.path.join(directorio, 'mantenimiento_raul.db')
    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS fichas 
                      (id INTEGER PRIMARY KEY, modelo TEXT, matricula TEXT, km_act TEXT,
                       aceite_chk TEXT, aceite_det TEXT, aceite_km TEXT,
                       caja_chk TEXT, caja_det TEXT, caja_km TEXT,
                       f_aire TEXT, f_aceite TEXT, f_polen TEXT, f_comb TEXT, f_anti TEXT,
                       r_del_chk TEXT, r_del_km TEXT, r_tra_chk TEXT, r_tra_km TEXT, 
                       frenos TEXT, luces TEXT, agua TEXT, limpias TEXT,
                       averia TEXT, coste TEXT, fecha TEXT, mecanico TEXT, 
                       itv_mes TEXT, itv_ano TEXT)''')
    conn.commit()
    return conn

class PantallaBase(Screen):
    def crear_contenedor(self, titulo):
        layout_total = BoxLayout(orientation='vertical')
        
        # Cabecera
        cabecera = Label(text=titulo, size_hint_y=None, height=130, bold=True, font_size=32, color=(1,1,1,1))
        with cabecera.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            self.rect = Rectangle(size=cabecera.size, pos=cabecera.pos)
        cabecera.bind(size=self._update_rect, pos=self._update_rect)
        layout_total.add_widget(cabecera)

        # Contenido con Scroll
        self.scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=25, padding=25)
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        layout_total.add_widget(self.scroll)

        # Botonera de navegación
        self.nav_bar = BoxLayout(size_hint_y=None, height=120, spacing=15, padding=10)
        layout_total.add_widget(self.nav_bar)

        # --- PIE DE PÁGINA CON TU NOMBRE ---
        pie_firma = Label(text="APP CREADA POR RAUL PLAZA", size_hint_y=None, height=40, 
                          font_size=20, color=(0.5, 0.5, 0.5, 1), italic=True)
        layout_total.add_widget(pie_firma)
        
        return layout_total

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def input_g(self, hint, multi=False, alto=110, ancho=1):
        return TextInput(hint_text=hint, multiline=multi, size_hint_y=None, height=alto, 
                         size_hint_x=ancho, font_size=30, padding=[20, 25])

    def check_g(self, texto):
        box = BoxLayout(orientation='horizontal', size_hint_y=None, height=90)
        box.add_widget(Label(text=texto, color=(0,0,0,1), font_size=28))
        cb = CheckBox(color=(0.1, 0.4, 0.7, 1), size_hint_x=None, width=100)
        box.add_widget(cb)
        return box, cb

class PaginaUno(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("DATOS GENERALES")
        self.mec = self.input_g("Mecánico")
        self.mod = self.input_g("Modelo")
        self.mat = self.input_g("Matrícula")
        self.km = self.input_g("Kilómetros")
        for w in [self.mec, self.mod, self.mat, self.km]: self.content.add_widget(w)
        btn_sig = Button(text="SIGUIENTE >", background_color=(0.1, 0.6, 0.3, 1), font_size=28, bold=True)
        btn_sig.bind(on_press=self.ir_sig)
        self.nav_bar.add_widget(btn_sig)
        self.add_widget(l)

    def ir_sig(self, x):
        App.get_running_app().datos.update({'mec':self.mec.text, 'mod':self.mod.text, 'mat':self.mat.text, 'km':self.km.text})
        self.manager.current = 'pag2'

class PaginaDos(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("MOTOR Y CAJA CAMBIOS")
        b1, self.ac_chk = self.check_g("Aceite Motor"); self.ac_det = self.input_g("Detalle Aceite"); self.ac_km = self.input_g("Km Aceite")
        b2, self.cj_chk = self.check_g("Caja Cambios"); self.cj_det = self.input_g("Detalle Caja"); self.cj_km = self.input_g("Km Caja")
        for w in [b1, self.ac_det, self.ac_km, b2, self.cj_det, self.cj_km]: self.content.add_widget(w)
        btn_atras = Button(text="< ATRÁS", background_color=(0.7, 0.2, 0.2, 1), font_size=28, bold=True)
        btn_atras.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag1'))
        btn_sig = Button(text="SIGUIENTE >", background_color=(0.1, 0.6, 0.3, 1), font_size=28, bold=True)
        btn_sig.bind(on_press=self.ir_sig)
        self.nav_bar.add_widget(btn_atras); self.nav_bar.add_widget(btn_sig)
        self.add_widget(l)

    def ir_sig(self, x):
        App.get_running_app().datos.update({'ac':str(self.ac_chk.active), 'ad':self.ac_det.text, 'ak':self.ac_km.text, 'cc':str(self.cj_chk.active), 'cd':self.cj_det.text, 'ck':self.cj_km.text})
        self.manager.current = 'pag3'

class PaginaTres(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("FILTROS Y RUEDAS")
        f1_b, self.f1 = self.check_g("F. Aire"); self.content.add_widget(f1_b)
        f2_b, self.f2 = self.check_g("F. Aceite"); self.content.add_widget(f2_b)
        f3_b, self.f3 = self.check_g("F. Polen"); self.content.add_widget(f3_b)
        f4_b, self.f4 = self.check_g("F. Combustible"); self.content.add_widget(f4_b)
        fa_b, self.fa = self.check_g("Anticongelante"); self.content.add_widget(fa_b)
        r1_b, self.rdc = self.check_g("Ruedas Del."); self.content.add_widget(r1_b)
        self.rdk = self.input_g("Km Del."); self.content.add_widget(self.rdk)
        r2_b, self.rtc = self.check_g("Ruedas Tras."); self.content.add_widget(r2_b)
        self.rtk = self.input_g("Km Tras."); self.content.add_widget(self.rtk)

        btn_atras = Button(text="< ATRÁS", background_color=(0.7, 0.2, 0.2, 1), font_size=28, bold=True)
        btn_atras.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag2'))
        btn_sig = Button(text="SIGUIENTE >", background_color=(0.1, 0.6, 0.3, 1), font_size=28, bold=True)
        btn_sig.bind(on_press=self.ir_sig)
        self.nav_bar.add_widget(btn_atras); self.nav_bar.add_widget(btn_sig)
        self.add_widget(l)

    def ir_sig(self, x):
        App.get_running_app().datos.update({'f1':str(self.f1.active), 'f2':str(self.f2.active), 'f3':str(self.f3.active), 'f4':str(self.f4.active), 'fa':str(self.fa.active), 'rdc':str(self.rdc.active), 'rdk':self.rdk.text, 'rtc':str(self.rtc.active), 'rtk':self.rtk.text})
        self.manager.current = 'pag4'

class PaginaCuatro(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("FINALIZAR Y ITV")
        fr_b, self.fre = self.check_g("Frenos OK"); self.content.add_widget(fr_b)
        lu_b, self.luc = self.check_g("Luces OK"); self.content.add_widget(lu_b)
        ag_b, self.agu = self.check_g("Niveles OK"); self.content.add_widget(ag_b)
        
        self.content.add_widget(Label(text="PRÓXIMA ITV (MES / AÑO)", font_size=26, bold=True, color=(0,0,0,1)))
        box_itv = BoxLayout(orientation='horizontal', size_hint_y=None, height=110, spacing=20)
        self.itv_m = self.input_g("Mes", ancho=0.5); self.itv_a = self.input_g("Año", ancho=0.5)
        box_itv.add_widget(self.itv_m); box_itv.add_widget(self.itv_a); self.content.add_widget(box_itv)
        
        self.obs = self.input_g("Observaciones", multi=True, alto=200); self.cos = self.input_g("COSTE TOTAL (€)")
        self.content.add_widget(self.obs); self.content.add_widget(self.cos)

        btn_atras = Button(text="< ATRÁS", background_color=(0.7, 0.2, 0.2, 1), font_size=28, bold=True)
        btn_atras.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag3'))
        btn_fin = Button(text="GUARDAR Y PDF", background_color=(0, 0.5, 0.8, 1), font_size=30, bold=True)
        btn_fin.bind(on_press=self.finalizar_todo)
        self.nav_bar.add_widget(btn_atras); self.nav_bar.add_widget(btn_fin)
        self.add_widget(l)

    def finalizar_todo(self, x):
        d = App.get_running_app().datos
        f_hoy = datetime.now().strftime("%d/%m/%Y")
        conn = conectar_bd(); c = conn.cursor()
        c.execute('''INSERT INTO fichas (modelo, matricula, km_act, aceite_chk, aceite_det, aceite_km, 
                     caja_chk, caja_det, caja_km, f_aire, f_aceite, f_polen, f_comb, f_anti, 
                     r_del_chk, r_del_km, r_tra_chk, r_tra_km, frenos, luces, agua, limpias, 
                     averia, coste, fecha, mecanico, itv_mes, itv_ano) 
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                  (d['mod'], d['mat'], d['km'], d['ac'], d['ad'], d['ak'], d['cc'], d['cd'], d['ck'],
                   d['f1'], d['f2'], d['f3'], d['f4'], d['fa'], d['rdc'], d['rdk'], d['rtc'], d['rtk'],
                   str(self.fre.active), str(self.luc.active), str(self.agu.active), "True",
                   self.obs.text, self.cos.text, f_hoy, d['mec'], self.itv_m.text, self.itv_a.text))
        conn.commit(); conn.close()

        if PDF_DISPONIBLE:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="INFORME DE MANTENIMIENTO", ln=True, align='C')
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(200, 10, txt="CREADO POR RAUL PLAZA", ln=True, align='C')
            pdf.ln(10)
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, txt=f"Vehiculo: {d['mod']} | Matrícula: {d['mat']}", ln=True)
            pdf.cell(0, 10, txt=f"Fecha: {f_hoy} | Coste: {self.cos.text} Euros", ln=True)
            pdf.output(f"Ficha_{d['mat']}.pdf")
            msg = "PDF Creado con éxito"
        else: msg = "Guardado en BD"
        Popup(title='Hecho', content=Label(text=msg), size_hint=(0.8, 0.4)).open()
        self.manager.current = 'pag1'

class MiApp(App):
    datos = {}
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(PaginaUno(name='pag1'))
        sm.add_widget(PaginaDos(name='pag2'))
        sm.add_widget(PaginaTres(name='pag3'))
        sm.add_widget(PaginaCuatro(name='pag4'))
        return sm

if __name__ == '__main__':
    MiApp().run()
