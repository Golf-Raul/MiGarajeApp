import sqlite3
import os
import webbrowser
from datetime import datetime
from urllib.parse import quote
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

# Intentar importar FPDF para el PDF
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
                       frenos TEXT, liq_frenos TEXT, luces TEXT, agua TEXT, limpias TEXT,
                       averia TEXT, coste TEXT, fecha TEXT, mecanico TEXT, 
                       itv_mes TEXT, itv_ano TEXT)''')
    conn.commit()
    return conn

class PantallaBase(Screen):
    def crear_contenedor(self, titulo):
        layout_total = BoxLayout(orientation='vertical')
        cabecera = Label(text=titulo, size_hint_y=None, height=140, bold=True, font_size=38, color=(1,1,1,1))
        with cabecera.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            self.rect = Rectangle(size=cabecera.size, pos=cabecera.pos)
        cabecera.bind(size=self._update_rect, pos=self._update_rect)
        layout_total.add_widget(cabecera)

        self.scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=30, padding=30)
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        layout_total.add_widget(self.scroll)

        self.nav_bar = BoxLayout(size_hint_y=None, height=130, spacing=20, padding=10)
        layout_total.add_widget(self.nav_bar)
        
        pie = Label(text="APP CREADA POR RAUL PLAZA", size_hint_y=None, height=50, font_size=22, color=(0.4, 0.4, 0.4, 1), bold=True)
        layout_total.add_widget(pie)
        return layout_total

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def input_g(self, hint, multi=False, alto=120):
        return TextInput(hint_text=hint, multiline=multi, size_hint_y=None, height=alto, font_size=32, padding=[20, 25])

    def check_g(self, texto):
        box = BoxLayout(orientation='horizontal', size_hint_y=None, height=100)
        box.add_widget(Label(text=texto, color=(0,0,0,1), font_size=30))
        cb = CheckBox(color=(0.1, 0.4, 0.7, 1), size_hint_x=None, width=120)
        box.add_widget(cb)
        return box, cb

class PantallaHistorial(PantallaBase):
    def on_pre_enter(self):
        self.actualizar_lista()

    def actualizar_lista(self):
        self.content.clear_widgets()
        conn = conectar_bd(); c = conn.cursor()
        c.execute("SELECT id, modelo, matricula, fecha FROM fichas ORDER BY id DESC")
        for fila in c.fetchall():
            item = BoxLayout(size_hint_y=None, height=120, spacing=10)
            btn_ver = Button(text=f"{fila[3]} - {fila[1]} ({fila[2]})", font_size=28)
            btn_ver.bind(on_press=lambda x, id_f=fila[0]: self.ver_detalle(id_f))
            btn_del = Button(text="X", size_hint_x=0.2, background_color=(0.8, 0, 0, 1), bold=True)
            btn_del.bind(on_press=lambda x, id_f=fila[0]: self.borrar_registro(id_f))
            item.add_widget(btn_ver); item.add_widget(btn_del)
            self.content.add_widget(item)
        conn.close()

    def borrar_registro(self, id_f):
        conn = conectar_bd(); c = conn.cursor()
        c.execute("DELETE FROM fichas WHERE id=?", (id_f,))
        conn.commit(); conn.close()
        self.actualizar_lista()

    def ver_detalle(self, id_ficha):
        conn = conectar_bd(); c = conn.cursor()
        c.execute("SELECT * FROM fichas WHERE id=?", (id_ficha,))
        f = c.fetchone()
        conn.close()
        resumen = f"Modelo: {f[1]}\nMatrícula: {f[2]}\nFecha: {f[26]}\nCoste: {f[25]}€\nMecánico: {f[27]}"
        Popup(title="Ficha Guardada", content=Label(text=resumen, font_size=30), size_hint=(0.9, 0.6)).open()

class PaginaUno(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("DATOS GENERALES")
        self.mec = self.input_g("Mecánico"); self.mod = self.input_g("Modelo")
        self.mat = self.input_g("Matrícula"); self.km = self.input_g("Kilómetros")
        for w in [self.mec, self.mod, self.mat, self.km]: self.content.add_widget(w)
        
        btn_hist = Button(text="HISTORIAL", background_color=(0.2, 0.5, 0.7, 1), font_size=30, bold=True)
        btn_hist.bind(on_press=lambda x: setattr(self.manager, 'current', 'historial'))
        btn_sig = Button(text="SIGUIENTE >", background_color=(0.1, 0.6, 0.3, 1), font_size=30, bold=True)
        btn_sig.bind(on_press=self.ir_sig)
        self.nav_bar.add_widget(btn_hist); self.nav_bar.add_widget(btn_sig)
        self.add_widget(l)

    def ir_sig(self, x):
        App.get_running_app().datos.update({'mec':self.mec.text, 'mod':self.mod.text, 'mat':self.mat.text, 'km':self.km.text})
        self.manager.current = 'pag2'

class PaginaDos(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("MOTOR Y CAJA")
        b1, self.ac_chk = self.check_g("Aceite Motor"); self.ac_det = self.input_g("Detalle Aceite"); self.ac_km = self.input_g("Km Aceite")
        b2, self.cj_chk = self.check_g("Caja Cambios"); self.cj_det = self.input_g("Detalle Caja"); self.cj_km = self.input_g("Km Caja")
        for w in [b1, self.ac_det, self.ac_km, b2, self.cj_det, self.cj_km]: self.content.add_widget(w)
        btn_sig = Button(text="SIGUIENTE >", background_color=(0.1, 0.6, 0.3, 1), font_size=30, bold=True)
        btn_sig.bind(on_press=self.ir_sig)
        self.nav_bar.add_widget(btn_sig)
        self.add_widget(l)

    def ir_sig(self, x):
        App.get_running_app().datos.update({'ac':str(self.ac_chk.active), 'ad':self.ac_det.text, 'ak':self.ac_km.text, 'cc':str(self.cj_chk.active), 'cd':self.cj_det.text, 'ck':self.cj_km.text})
        self.manager.current = 'pag3'

class PaginaTres(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("FILTROS Y RUEDAS")
        # Filtros
        self.f1_b, self.f1 = self.check_g("F. Aire"); self.content.add_widget(self.f1_b)
        self.f2_b, self.f2 = self.check_g("F. Aceite"); self.content.add_widget(self.f2_b)
        self.f3_b, self.f3 = self.check_g("F. Polen"); self.content.add_widget(self.f3_b)
        self.f4_b, self.f4 = self.check_g("F. Combustible"); self.content.add_widget(self.f4_b)
        self.fa_b, self.fa = self.check_g("Anticongelante"); self.content.add_widget(self.fa_b)
        # Ruedas
        self.r1_b, self.rdc = self.check_g("Ruedas Del."); self.content.add_widget(self.r1_b)
        self.rdk = self.input_g("Km Ruedas Del."); self.content.add_widget(self.rdk)
        self.r2_b, self.rtc = self.check_g("Ruedas Tras."); self.content.add_widget(self.r2_b)
        self.rtk = self.input_g("Km Ruedas Tras."); self.content.add_widget(self.rtk)
        
        btn_sig = Button(text="SIGUIENTE >", background_color=(0.1, 0.6, 0.3, 1), font_size=30, bold=True)
        btn_sig.bind(on_press=self.ir_sig)
        self.nav_bar.add_widget(btn_sig)
        self.add_widget(l)

    def ir_sig(self, x):
        App.get_running_app().datos.update({'f1':str(self.f1.active), 'f2':str(self.f2.active), 'f3':str(self.f3.active), 'f4':str(self.f4.active), 'fa':str(self.fa.active), 'rdc':str(self.rdc.active), 'rdk':self.rdk.text, 'rtc':str(self.rtc.active), 'rtk':self.rtk.text})
        self.manager.current = 'pag4'

class PaginaCuatro(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("FINALIZAR E ITV")
        fr_b, self.fre = self.check_g("Frenos OK"); self.content.add_widget(fr_b)
        # AÑADIDO: Líquido de frenos justo debajo de frenos
        lf_b, self.lf = self.check_g("Líquido de Frenos"); self.content.add_widget(lf_b)
        
        lu_b, self.luc = self.check_g("Luces OK"); self.content.add_widget(lu_b)
        ag_b, self.agu = self.check_g("Niveles OK"); self.content.add_widget(ag_b)
        
        box_itv = BoxLayout(orientation='horizontal', size_hint_y=None, height=120, spacing=10)
        self.itv_m = self.input_g("Mes ITV"); self.itv_a = self.input_g("Año ITV")
        box_itv.add_widget(self.itv_m); box_itv.add_widget(self.itv_a); self.content.add_widget(box_itv)
        
        self.obs = self.input_g("Averías/Detalles", multi=True, alto=250)
        self.cos = self.input_g("COSTE (€)")
        self.content.add_widget(self.obs); self.content.add_widget(self.cos)

        btn_fin = Button(text="PDF Y WHATSAPP", background_color=(0, 0.5, 0.8, 1), font_size=34, bold=True)
        btn_fin.bind(on_press=self.finalizar)
        self.nav_bar.add_widget(btn_fin)
        self.add_widget(l)

    def finalizar(self, x):
        d = App.get_running_app().datos
        f_hoy = datetime.now().strftime("%d/%m/%Y")
        
        # 1. Guardar en BD
        conn = conectar_bd(); c = conn.cursor()
        c.execute('''INSERT INTO fichas (modelo, matricula, km_act, aceite_chk, aceite_det, aceite_km, 
                     caja_chk, caja_det, caja_km, f_aire, f_aceite, f_polen, f_comb, f_anti, 
                     r_del_chk, r_del_km, r_tra_chk, r_tra_km, frenos, liq_frenos, luces, agua, limpias, 
                     averia, coste, fecha, mecanico, itv_mes, itv_ano) 
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                  (d['mod'], d['mat'], d['km'], d['ac'], d['ad'], d['ak'], d['cc'], d['cd'], d['ck'],
                   d['f1'], d['f2'], d['f3'], d['f4'], d['fa'], d['rdc'], d['rdk'], d['rtc'], d['rtk'],
                   str(self.fre.active), str(self.lf.active), str(self.luc.active), str(self.agu.active), "True",
                   self.obs.text, self.cos.text, f_hoy, d['mec'], self.itv_m.text, self.itv_a.text))
        conn.commit(); conn.close()

        # 2. Generar PDF Real
        nombre_archivo = f"Mantenimiento_{d['mat']}_{datetime.now().strftime('%H%M')}.pdf"
        if PDF_DISPONIBLE:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="FICHA DE TALLER - RAUL PLAZA", ln=True, align='C')
            pdf.ln(10)
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Fecha: {f_hoy} | Mecánico: {d['mec']}", ln=True)
            pdf.cell(200, 10, txt=f"Vehículo: {d['mod']} | Matrícula: {d['mat']}", ln=True)
            pdf.cell(200, 10, txt=f"Kilómetros: {d['km']}", ln=True)
            pdf.ln(5)
            pdf.cell(200, 10, txt=f"Coste Total: {self.cos.text} Euros", ln=True)
            pdf.output(nombre_archivo)

        # 3. Mandar por WhatsApp (Texto formateado)
        mensaje = f"*TALLER RAUL PLAZA*\n\n✅ *Vehículo:* {d['mod']}\n🆔 *Matrícula:* {d['mat']}\n🛠 *Trabajo:* Mantenimiento General\n💶 *Coste:* {self.cos.text}€\n🗓 *Próxima ITV:* {self.itv_m.text}/{self.itv_a.text}"
        webbrowser.open(f"https://wa.me/?text={quote(mensaje)}")
        
        self.manager.current = 'pag1'

class MiApp(App):
    datos = {}
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(PaginaUno(name='pag1'))
        sm.add_widget(PaginaDos(name='pag2'))
        sm.add_widget(PaginaTres(name='pag3'))
        sm.add_widget(PaginaCuatro(name='pag4'))
        sm.add_widget(PantallaHistorial(name='historial'))
        return sm

if __name__ == '__main__':
    MiApp().run()
