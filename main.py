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

Window.clearcolor = (0.9, 0.9, 0.9, 1)

def conectar_bd():
    try:
        ruta_db = 'reparaciones_rp_aj_v2.db' 
        conn = sqlite3.connect(ruta_db)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS fichas 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, modelo TEXT, matricula TEXT, km_act TEXT,
                           aceite_chk TEXT, aceite_det TEXT, aceite_km TEXT,
                           caja_chk TEXT, caja_det TEXT, caja_km TEXT,
                           f_aire TEXT, ref_f1 TEXT, f_aceite TEXT, ref_f2 TEXT, 
                           f_polen TEXT, ref_f3 TEXT, f_comb TEXT, ref_f4 TEXT, f_anti TEXT,
                           r_del_chk TEXT, r_del_km TEXT, r_tra_chk TEXT, r_tra_km TEXT, 
                           frenos TEXT, liq_frenos TEXT, luces TEXT, agua TEXT,
                           averia TEXT, coste TEXT, fecha TEXT, mecanico TEXT, 
                           itv_mes TEXT, itv_ano TEXT)''')
        conn.commit()
        return conn
    except Exception:
        return None

class PantallaBase(Screen):
    def crear_contenedor(self, titulo):
        layout_total = BoxLayout(orientation='vertical')
        self.cabecera = Label(text=titulo, size_hint_y=None, height='80dp', bold=True, font_size='24sp', color=(1,1,1,1))
        with self.cabecera.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            self.rect = Rectangle(size=self.cabecera.size, pos=self.cabecera.pos)
        self.cabecera.bind(size=self._update_rect, pos=self._update_rect)
        layout_total.add_widget(self.cabecera)

        self.scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing='15dp', padding='20dp')
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        layout_total.add_widget(self.scroll)

        self.nav_bar = BoxLayout(size_hint_y=None, height='70dp', spacing='10dp', padding='5dp')
        layout_total.add_widget(self.nav_bar)
        
        pie = Label(text="APP CREADA POR RAUL PLAZA", size_hint_y=None, height='30dp', font_size='14sp', color=(0.4, 0.4, 0.4, 1), bold=True)
        layout_total.add_widget(pie)
        return layout_total

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def input_g(self, hint, multi=False, alto='60dp'):
        return TextInput(hint_text=hint, multiline=multi, size_hint_y=None, height=alto, font_size='18sp', padding=['10dp', '10dp'])

    def check_g(self, texto):
        box = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        box.add_widget(Label(text=texto, color=(0,0,0,1), font_size='16sp', bold=True))
        cb = CheckBox(color=(0.1, 0.4, 0.7, 1), size_hint_x=None, width='50dp')
        box.add_widget(cb)
        return box, cb

class PantallaHistorial(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout_p = self.crear_contenedor("HISTORIAL")
        self.buscador = TextInput(hint_text="BUSCAR MATRÍCULA...", size_hint_y=None, height='60dp', font_size='20sp', multiline=False)
        self.buscador.bind(text=self.actualizar_lista)
        self.layout_p.add_widget(self.buscador, index=2)
        btn_v = Button(text="VOLVER", background_color=(0.6, 0.6, 0.6, 1), bold=True)
        btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag1'))
        self.nav_bar.add_widget(btn_v)
        self.add_widget(self.layout_p)

    def on_pre_enter(self): self.actualizar_lista()

    def actualizar_lista(self, *args):
        self.content.clear_widgets()
        conn = conectar_bd()
        if not conn: return
        c = conn.cursor()
        c.execute("SELECT id, modelo, matricula, fecha FROM fichas WHERE matricula LIKE ? ORDER BY id DESC", (f'%{self.buscador.text}%',))
        for f in c.fetchall():
            item = BoxLayout(size_hint_y=None, height='60dp', spacing='5dp')
            btn = Button(text=f"{f[3]} | {f[2]}", font_size='16sp')
            btn.bind(on_press=lambda x, id_f=f[0]: self.ver_detalle(id_f))
            btn_del = Button(text="X", size_hint_x=0.2, background_color=(0.8, 0, 0, 1))
            btn_del.bind(on_press=lambda x, id_f=f[0]: self.borrar(id_f))
            item.add_widget(btn); item.add_widget(btn_del)
            self.content.add_widget(item)
        conn.close()

    def borrar(self, id_f):
        conn = conectar_bd()
        if conn:
            conn.cursor().execute("DELETE FROM fichas WHERE id=?", (id_f,))
            conn.commit(); conn.close(); self.actualizar_lista()

    def ver_detalle(self, id_f):
        conn = conectar_bd()
        f = conn.cursor().execute("SELECT * FROM fichas WHERE id=?", (id_f,)).fetchone()
        conn.close()
        cont = BoxLayout(orientation='vertical', padding=20)
        res = Label(text=f"Modelo: {f[1]}\nMatrícula: {f[2]}\nFecha: {f[30]}\nCoste: {f[29]}€\nRefs: {f[11]}, {f[13]}", font_size='16sp', color=(0,0,0,1))
        btn_c = Button(text="CERRAR", size_hint_y=0.2)
        cont.add_widget(res); cont.add_widget(btn_c)
        pop = Popup(title="RESUMEN", content=cont, size_hint=(0.9, 0.8))
        btn_c.bind(on_press=pop.dismiss); pop.open()

class PaginaUno(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("DATOS GENERALES")
        self.mec = self.input_g("Mecánico"); self.mod = self.input_g("Modelo")
        self.mat = self.input_g("Matrícula"); self.km = self.input_g("Kilómetros")
        for w in [self.mec, self.mod, self.mat, self.km]: self.content.add_widget(w)
        btn_h = Button(text="HISTORIAL", background_color=(0.2, 0.5, 0.7, 1))
        btn_h.bind(on_press=lambda x: setattr(self.manager, 'current', 'historial'))
        btn_s = Button(text="SIGUIENTE", background_color=(0.1, 0.6, 0.3, 1))
        btn_s.bind(on_press=self.ir_sig)
        self.nav_bar.add_widget(btn_h); self.nav_bar.add_widget(btn_s); self.add_widget(l)

    def ir_sig(self, x):
        App.get_running_app().datos.update({'mec':self.mec.text, 'mod':self.mod.text, 'mat':self.mat.text, 'km':self.km.text})
        self.manager.current = 'pag2'

class PaginaDos(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("MOTOR Y CAJA")
        b1, self.ac_chk = self.check_g("Aceite Motor"); self.ac_det = self.input_g("Detalle Aceite"); self.ac_km = self.input_g("Km Aceite")
        b2, self.cj_chk = self.check_g("Caja Cambios"); self.cj_det = self.input_g("Detalle Aceite Caja"); self.cj_km = self.input_g("Km Aceite Caja")
        for w in [b1, self.ac_det, self.ac_km, b2, self.cj_det, self.cj_km]: self.content.add_widget(w)
        btn_s = Button(text="SIGUIENTE", background_color=(0.1, 0.6, 0.3, 1))
        btn_s.bind(on_press=self.ir_sig)
        self.nav_bar.add_widget(btn_s); self.add_widget(l)

    def ir_sig(self, x):
        App.get_running_app().datos.update({'ac':str(self.ac_chk.active), 'ad':self.ac_det.text, 'ak':self.ac_km.text, 'cc':str(self.cj_chk.active), 'cd':self.cj_det.text, 'ck':self.cj_km.text})
        self.manager.current = 'pag3'

class PaginaTres(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("FILTROS Y RUEDAS")
        b1, self.f1 = self.check_g("F. Aire"); self.r1 = self.input_g("Ref. Aire")
        b2, self.f2 = self.check_g("F. Aceite"); self.r2 = self.input_g("Ref. Aceite")
        b3, self.f3 = self.check_g("F. Polen"); self.r3 = self.input_g("Ref. Polen")
        b4, self.f4 = self.check_g("F. Combustible"); self.r4 = self.input_g("Ref. Combustible")
        ba, self.fa = self.check_g("Anticongelante")
        rd, self.rdc = self.check_g("Ruedas Del."); self.rdk = self.input_g("Km Ruedas Del.")
        rt, self.rtc = self.check_g("Ruedas Tras."); self.rtk = self.input_g("Km Ruedas Tras.")
        for w in [b1, self.r1, b2, self.r2, b3, self.r3, b4, self.r4, ba, rd, self.rdk, rt, self.rtk]: self.content.add_widget(w)
        btn_s = Button(text="SIGUIENTE", background_color=(0.1, 0.6, 0.3, 1))
        btn_s.bind(on_press=self.ir_sig)
        self.nav_bar.add_widget(btn_s); self.add_widget(l)

    def ir_sig(self, x):
        App.get_running_app().datos.update({'f1':str(self.f1.active), 'rf1':self.r1.text, 'f2':str(self.f2.active), 'rf2':self.r2.text, 'f3':str(self.f3.active), 'rf3':self.r3.text, 'f4':str(self.f4.active), 'rf4':self.r4.text, 'fa':str(self.fa.active), 'rdc':str(self.rdc.active), 'rdk':self.rdk.text, 'rtc':str(self.rtc.active), 'rtk':self.rtk.text})
        self.manager.current = 'pag4'

class PaginaCuatro(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("FINALIZAR E ITV")
        b_fr, self.fre = self.check_g("Frenos OK")
        b_lf, self.lfr = self.check_g("Líquido Frenos")
        b_lu, self.luc = self.check_g("Luces OK")
        b_ag, self.agu = self.check_g("Niveles OK")
        self.itv_m = self.input_g("Mes ITV"); self.itv_a = self.input_g("Año ITV")
        self.obs = self.input_g("Averías/Detalles", multi=True, alto='150dp')
        self.cos = self.input_g("COSTE €")
        for w in [b_fr, b_lf, b_lu, b_ag, self.itv_m, self.itv_a, self.obs, self.cos]: self.content.add_widget(w)
        btn_g = Button(text="GUARDAR", background_color=(0.4, 0.4, 0.4, 1))
        btn_g.bind(on_press=lambda x: self.finalizar(enviar=False))
        btn_e = Button(text="ENVIAR", background_color=(0, 0.5, 0.8, 1))
        btn_e.bind(on_press=lambda x: self.finalizar(enviar=True))
        self.nav_bar.add_widget(btn_g); self.nav_bar.add_widget(btn_e); self.add_widget(l)

    def finalizar(self, enviar=False):
        d = App.get_running_app().datos
        f_hoy = datetime.now().strftime("%d/%m/%Y")
        conn = conectar_bd()
        if conn:
            c = conn.cursor()
            c.execute('''INSERT INTO fichas (modelo, matricula, km_act, aceite_chk, aceite_det, aceite_km, 
                         caja_chk, caja_det, caja_km, f_aire, ref_f1, f_aceite, ref_f2, f_polen, ref_f3, f_comb, ref_f4, f_anti, 
                         r_del_chk, r_del_km, r_tra_chk, r_tra_km, frenos, liq_frenos, luces, agua, 
                         averia, coste, fecha, mecanico, itv_mes, itv_ano) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                      (d['mod'], d['mat'], d['km'], d['ac'], d['ad'], d['ak'], d['cc'], d['cd'], d['ck'],
                       d['f1'], d['rf1'], d['f2'], d['rf2'], d['f3'], d['rf3'], d['f4'], d['rf4'], d['fa'],
                       d['rdc'], d['rdk'], d['rtc'], d['rtk'], str(self.fre.active), str(self.lfr.active), str(self.luc.active), str(self.agu.active),
                       self.obs.text, self.cos.text, f_hoy, d['mec'], self.itv_m.text, self.itv_a.text))
            conn.commit(); conn.close()
        if enviar:
            mensaje = f"*REPARACIONES RP y AJ*\n\n✅ *Vehículo:* {d['mod']}\n🆔 *Matrícula:* {d['mat']}\n💶 *Coste:* {self.cos.text}€"
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
