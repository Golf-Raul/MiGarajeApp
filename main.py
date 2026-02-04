import sqlite3
import os
from datetime import datetime
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
from kivy.utils import platform

# Configuración de pantalla
Window.clearcolor = (0.9, 0.9, 0.9, 1)

def conectar_bd():
    try:
        if platform == 'android':
            from android.storage import app_storage_path
            directorio = app_storage_path()
        else:
            directorio = os.path.dirname(os.path.abspath(__file__))
        
        ruta_db = os.path.join(directorio, 'garaje_pipo_v3.db')
        conn = sqlite3.connect(ruta_db)
        cursor = conn.cursor()
        # TABLA COMPLETA CON TODOS LOS CAMPOS
        cursor.execute('''CREATE TABLE IF NOT EXISTS fichas 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           modelo TEXT, matricula TEXT, km_act TEXT,
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
    except Exception as e:
        print(f"Error BD: {e}")
        return None

# --- CLASES BASE ---
class PantallaBase(Screen):
    def crear_contenedor(self, titulo):
        layout_total = BoxLayout(orientation='vertical')
        self.cabecera = Label(text=titulo, size_hint_y=None, height='70dp', bold=True, font_size='22sp', color=(1,1,1,1))
        with self.cabecera.canvas.before:
            Color(0.1, 0.4, 0.7, 1) # Azul Pipo
            self.rect = Rectangle(size=self.cabecera.size, pos=self.cabecera.pos)
        self.cabecera.bind(size=self._update_rect, pos=self._update_rect)
        layout_total.add_widget(self.cabecera)
        
        self.scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing='10dp', padding='15dp')
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        layout_total.add_widget(self.scroll)
        
        self.nav_bar = BoxLayout(size_hint_y=None, height='65dp', spacing='10dp', padding='5dp')
        layout_total.add_widget(self.nav_bar)
        return layout_total

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def input_g(self, hint, multi=False, alto='50dp'):
        return TextInput(hint_text=hint, multiline=multi, size_hint_y=None, height=alto, font_size='16sp')

    def check_g(self, texto):
        box = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        box.add_widget(Label(text=texto, color=(0,0,0,1), halign='left'))
        cb = CheckBox(color=(0.1, 0.4, 0.7, 1), size_hint_x=None, width='50dp')
        box.add_widget(cb)
        return box, cb

# --- PANTALLAS ---
class PaginaUno(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("1. DATOS GENERALES")
        self.mec = self.input_g("Nombre del Mecánico")
        self.mod = self.input_g("Modelo del Vehículo")
        self.mat = self.input_g("Matrícula")
        self.km = self.input_g("Kilómetros Actuales")
        for w in [self.mec, self.mod, self.mat, self.km]: self.content.add_widget(w)
        
        btn_h = Button(text="HISTORIAL", background_color=(0.5, 0.5, 0.5, 1))
        btn_h.bind(on_press=lambda x: setattr(self.manager, 'current', 'historial'))
        btn_s = Button(text="SIGUIENTE", background_color=(0.1, 0.6, 0.3, 1))
        btn_s.bind(on_press=self.guardar_y_sig)
        self.nav_bar.add_widget(btn_h); self.nav_bar.add_widget(btn_s); self.add_widget(l)

    def guardar_y_sig(self, x):
        App.get_running_app().datos.update({'mec':self.mec.text, 'mod':self.mod.text, 'mat':self.mat.text, 'km':self.km.text})
        self.manager.current = 'pag2'

class PaginaDos(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("2. LÍQUIDOS Y CAJA")
        # Aceite Motor
        b1, self.ac_chk = self.check_g("Cambio Aceite Motor")
        self.ac_det = self.input_g("Tipo (ej: 5W30)")
        self.ac_km = self.input_g("Próximo Cambio (KM)")
        # Caja Cambios
        b2, self.cj_chk = self.check_g("Cambio Aceite Caja")
        self.cj_det = self.input_g("Tipo Valvulina")
        self.cj_km = self.input_g("Próximo Cambio Caja (KM)")
        
        for w in [b1, self.ac_det, self.ac_km, Label(text="---", height='20dp'), b2, self.cj_det, self.cj_km]: 
            self.content.add_widget(w)
            
        btn_a = Button(text="ATRÁS"); btn_a.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag1'))
        btn_s = Button(text="SIGUIENTE"); btn_s.bind(on_press=self.guardar_y_sig)
        self.nav_bar.add_widget(btn_a); self.nav_bar.add_widget(btn_s); self.add_widget(l)

    def guardar_y_sig(self, x):
        App.get_running_app().datos.update({
            'ac_chk': str(self.ac_chk.active), 'ac_det': self.ac_det.text, 'ac_km': self.ac_km.text,
            'cj_chk': str(self.cj_chk.active), 'cj_det': self.cj_det.text, 'cj_km': self.cj_km.text
        })
        self.manager.current = 'pag3'

class PaginaTres(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("3. FILTROS Y REVISIÓN")
        b1, self.f1 = self.check_g("Filtro Aire"); self.r1 = self.input_g("Ref. Aire")
        b2, self.f2 = self.check_g("Filtro Aceite"); self.r2 = self.input_g("Ref. Aceite")
        b3, self.f3 = self.check_g("Filtro Polen"); self.r3 = self.input_g("Ref. Polen")
        b4, self.f4 = self.check_g("Filtro Combustible"); self.r4 = self.input_g("Ref. Combustible")
        b5, self.anti = self.check_g("Anticongelante")
        
        for w in [b1, self.r1, b2, self.r2, b3, self.r3, b4, self.r4, b5]: self.content.add_widget(w)
        
        btn_a = Button(text="ATRÁS"); btn_a.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag2'))
        btn_s = Button(text="SIGUIENTE"); btn_s.bind(on_press=self.guardar_y_sig)
        self.nav_bar.add_widget(btn_a); self.nav_bar.add_widget(btn_s); self.add_widget(l)

    def guardar_y_sig(self, x):
        App.get_running_app().datos.update({
            'f1': str(self.f1.active), 'r1': self.r1.text, 'f2': str(self.f2.active), 'r2': self.r2.text,
            'f3': str(self.f3.active), 'r3': self.r3.text, 'f4': str(self.f4.active), 'r4': self.r4.text,
            'anti': str(self.anti.active)
        })
        self.manager.current = 'pag4'

class PaginaCuatro(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("4. SEGURIDAD E ITV")
        b1, self.rd_c = self.check_g("Ruedas Del."); self.rd_k = self.input_g("KM Ruedas Del.")
        b2, self.rt_c = self.check_g("Ruedas Tra."); self.rt_k = self.input_g("KM Ruedas Tra.")
        b3, self.fre = self.check_g("Revisión Frenos")
        b4, self.luc = self.check_g("Revisión Luces")
        
        self.itv_m = self.input_g("Mes ITV (1-12)")
        self.itv_a = self.input_g("Año ITV (ej: 2026)")
        
        self.obs = self.input_g("Otras averías / Notas", multi=True, alto='80dp')
        self.cos = self.input_g("Coste Total Reparación €")

        for w in [b1, self.rd_k, b2, self.rt_k, b3, b4, self.itv_m, self.itv_a, self.obs, self.cos]: 
            self.content.add_widget(w)
            
        btn_a = Button(text="ATRÁS"); btn_a.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag3'))
        btn_g = Button(text="GUARDAR TODO", background_color=(0.1, 0.6, 0.3, 1))
        btn_g.bind(on_press=self.finalizar)
        self.nav_bar.add_widget(btn_a); self.nav_bar.add_widget(btn_g); self.add_widget(l)

    def finalizar(self, x):
        d = App.get_running_app().datos
        f_hoy = datetime.now().strftime("%d/%m/%Y")
        conn = conectar_bd()
        if conn:
            c = conn.cursor()
            c.execute('''INSERT INTO fichas (modelo, matricula, km_act, aceite_chk, aceite_det, aceite_km, 
                         caja_chk, caja_det, caja_km, f_aire, ref_f1, f_aceite, ref_f2, f_polen, ref_f3, 
                         f_comb, ref_f4, f_anti, r_del_chk, r_del_km, r_tra_chk, r_tra_km, frenos, luces, 
                         averia, coste, fecha, mecanico, itv_mes, itv_ano) 
                         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                      (d['mod'], d['mat'], d['km'], d['ac_chk'], d['ac_det'], d['ac_km'],
                       d['cj_chk'], d['cj_det'], d['cj_km'], d['f1'], d['r1'], d['f2'], d['r2'], 
                       d['f3'], d['r3'], d['f4'], d['r4'], d['anti'], str(self.rd_c.active), self.rd_k.text,
                       str(self.rt_c.active), self.rt_k.text, str(self.fre.active), str(self.luc.active),
                       self.obs.text, self.cos.text, f_hoy, d['mec'], self.itv_m.text, self.itv_a.text))
            conn.commit()
            conn.close()
        # Reset y volver al inicio
        App.get_running_app().datos = {}
        self.manager.current = 'pag1'

class PantallaHistorial(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout_p = self.crear_contenedor("HISTORIAL DE TRABAJOS")
        self.buscador = TextInput(hint_text="BUSCAR POR MATRÍCULA...", size_hint_y=None, height='55dp', font_size='18sp')
        self.buscador.bind(text=self.actualizar_lista)
        self.layout_p.add_widget(self.buscador, index=2)
        btn_v = Button(text="VOLVER AL MENÚ")
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
            btn = Button(text=f"{f[3]} | {f[2]} | {f[1]}", size_hint_y=None, height='60dp', background_color=(1,1,1,1), color=(0,0,0,1))
            btn.bind(on_press=lambda x, id_f=f[0]: self.ver_detalle(id_f))
            self.content.add_widget(btn)
        conn.close()

    def ver_detalle(self, id_f):
        conn = conectar_bd()
        f = conn.cursor().execute("SELECT * FROM fichas WHERE id=?", (id_f,)).fetchone()
        conn.close()
        
        info = f"FECHA: {f[29]}\nMATRÍCULA: {f[2]}\nMODELO: {f[1]}\nKM: {f[3]}\nMECÁNICO: {f[30]}\n\n"
        info += f"ACEITE: {f[5]} (Próx: {f[6]})\nCAJA: {f[8]} (Próx: {f[9]})\n"
        info += f"F.AIRE: {f[11]} | F.ACEITE: {f[13]}\n"
        info += f"NOTAS: {f[27]}\nCOSTE: {f[28]}€"
        
        c_pop = BoxLayout(orientation='vertical', padding=10)
        c_pop.add_widget(Label(text=info, color=(1,1,1,1), font_size='14sp', halign='center'))
        btn_c = Button(text="CERRAR", size_hint_y=None, height='50dp')
        pop = Popup(title="DETALLE DEL TRABAJO", content=c_pop, size_hint=(0.9, 0.8))
        btn_c.bind(on_press=pop.dismiss); c_pop.add_widget(btn_c); pop.open()

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
