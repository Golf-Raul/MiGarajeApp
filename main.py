import sqlite3
import os
import urllib.parse
from datetime import datetime
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.utils import platform

if platform == 'android':
    from jnius import autoclass
else:
    import webbrowser

Window.clearcolor = (0.95, 0.95, 0.95, 1)

def conectar_bd():
    try:
        directorio = os.path.dirname(os.path.abspath(__file__)) if platform != 'android' else None
        if platform == 'android':
            from android.storage import app_storage_path
            directorio = app_storage_path()
        
        ruta_db = os.path.join(directorio, 'garaje_pipo_v2026.db')
        conn = sqlite3.connect(ruta_db)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS fichas 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           modelo TEXT, matricula TEXT, km_act TEXT,
                           aceite_det TEXT, aceite_km TEXT,
                           caja_det TEXT, caja_km TEXT,
                           f_aire TEXT, f_aceite TEXT, f_polen TEXT, f_comb TEXT, 
                           anti_det TEXT,
                           r_del_km TEXT, r_tra_km TEXT, 
                           correa TEXT, frenos TEXT, pastillas TEXT, luces TEXT, 
                           averia TEXT, coste TEXT, fecha TEXT, 
                           mecanico TEXT, itv_mes TEXT, itv_ano TEXT)''')
        conn.commit()
        return conn
    except Exception as e:
        print(f"Error BD: {e}")
        return None

class PantallaBase(Screen):
    def crear_contenedor(self, titulo):
        layout_total = BoxLayout(orientation='vertical')
        self.cabecera = Label(text=f"{titulo}\n[size=12sp]BY RAUL PLAZA[/size]", 
                              markup=True, size_hint_y=None, height='80dp', 
                              bold=True, font_size='20sp', color=(1,1,1,1), halign='center')
        with self.cabecera.canvas.before:
            Color(0.05, 0.3, 0.6, 1)
            self.rect = Rectangle(size=self.cabecera.size, pos=self.cabecera.pos)
        self.cabecera.bind(size=self._update_rect, pos=self._update_rect)
        
        layout_total.add_widget(self.cabecera)
        self.scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing='10dp', padding='15dp')
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        layout_total.add_widget(self.scroll)
        self.nav_bar = BoxLayout(size_hint_y=None, height='70dp', spacing='10dp', padding='5dp')
        layout_total.add_widget(self.nav_bar)
        return layout_total

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class PaginaUno(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("1. DATOS GENERALES")
        self.mec = TextInput(hint_text="Nombre del Mecánico", size_hint_y=None, height='50dp')
        self.mod = TextInput(hint_text="Modelo del Vehículo", size_hint_y=None, height='50dp')
        self.mat = TextInput(hint_text="Matrícula", size_hint_y=None, height='50dp')
        self.km = TextInput(hint_text="Kilómetros Actuales", size_hint_y=None, height='50dp')
        
        for w in [self.mec, self.mod, self.mat, self.km]: self.content.add_widget(w)
        
        btn_h = Button(text="HISTORIAL"); btn_h.bind(on_press=lambda x: setattr(self.manager, 'current', 'historial'))
        btn_s = Button(text="SIGUIENTE", background_color=(0.1, 0.5, 0.8, 1)); btn_s.bind(on_press=self.sig)
        self.nav_bar.add_widget(btn_h); self.nav_bar.add_widget(btn_s)
        self.add_widget(l)

    def sig(self, x):
        App.get_running_app().datos.update({'mec':self.mec.text, 'mod':self.mod.text, 'mat':self.mat.text, 'km':self.km.text})
        self.manager.current = 'pag2'

class PaginaDos(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("2. ACEITES Y LÍQUIDOS")
        self.aceite = TextInput(hint_text="Aceite Motor (Tipo)", size_hint_y=None, height='50dp')
        self.aceite_km = TextInput(hint_text="KM Próximo Cambio Aceite", size_hint_y=None, height='50dp')
        self.caja = TextInput(hint_text="Aceite Caja de Cambios", size_hint_y=None, height='50dp')
        self.caja_km = TextInput(hint_text="KM Cambio Aceite Caja", size_hint_y=None, height='50dp')
        self.anti = TextInput(hint_text="Anticongelante (Tipo/Nivel)", size_hint_y=None, height='50dp')
        
        for w in [self.aceite, self.aceite_km, self.caja, self.caja_km, self.anti]: self.content.add_widget(w)
        
        btn_v = Button(text="VOLVER"); btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag1'))
        btn_s = Button(text="SIGUIENTE", background_color=(0.1, 0.5, 0.8, 1)); btn_s.bind(on_press=self.sig)
        self.nav_bar.add_widget(btn_v); self.nav_bar.add_widget(btn_s)
        self.add_widget(l)

    def sig(self, x):
        App.get_running_app().datos.update({'aceite':self.aceite.text, 'aceite_km':self.aceite_km.text, 'caja':self.caja.text, 'caja_km':self.caja_km.text, 'anti':self.anti.text})
        self.manager.current = 'pag3'

class PaginaTres(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("3. FILTROS Y CORREAS")
        self.f_aire = TextInput(hint_text="Filtro Aire (Ref)", size_hint_y=None, height='50dp')
        self.f_aceite = TextInput(hint_text="Filtro Aceite (Ref)", size_hint_y=None, height='50dp')
        self.f_polen = TextInput(hint_text="Filtro Polen (Ref)", size_hint_y=None, height='50dp')
        self.f_comb = TextInput(hint_text="Filtro Combustible (Ref)", size_hint_y=None, height='50dp')
        self.correa = TextInput(hint_text="Correa Distribución (Estado/KM)", size_hint_y=None, height='50dp')
        
        for w in [self.f_aire, self.f_aceite, self.f_polen, self.f_comb, self.correa]: self.content.add_widget(w)
        
        btn_v = Button(text="VOLVER"); btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag2'))
        btn_s = Button(text="SIGUIENTE", background_color=(0.1, 0.5, 0.8, 1)); btn_s.bind(on_press=self.sig)
        self.nav_bar.add_widget(btn_v); self.nav_bar.add_widget(btn_s)
        self.add_widget(l)

    def sig(self, x):
        App.get_running_app().datos.update({'f_aire':self.f_aire.text, 'f_aceite':self.f_aceite.text, 'f_polen':self.f_polen.text, 'f_comb':self.f_comb.text, 'correa':self.correa.text})
        self.manager.current = 'pag4'

class PaginaCuatro(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("4. RUEDAS Y SEGURIDAD")
        self.r_del = TextInput(hint_text="KM Cambio Ruedas Del.", size_hint_y=None, height='50dp')
        self.r_tra = TextInput(hint_text="KM Cambio Ruedas Tras.", size_hint_y=None, height='50dp')
        self.frenos = TextInput(hint_text="Estado Discos", size_hint_y=None, height='50dp')
        self.pastillas = TextInput(hint_text="Estado Pastillas", size_hint_y=None, height='50dp')
        self.luces = TextInput(hint_text="Estado Luces", size_hint_y=None, height='50dp')
        
        for w in [self.r_del, self.r_tra, self.frenos, self.pastillas, self.luces]: self.content.add_widget(w)
        
        btn_v = Button(text="VOLVER"); btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag3'))
        btn_s = Button(text="SIGUIENTE", background_color=(0.1, 0.5, 0.8, 1)); btn_s.bind(on_press=self.sig)
        self.nav_bar.add_widget(btn_v); self.nav_bar.add_widget(btn_s)
        self.add_widget(l)

    def sig(self, x):
        App.get_running_app().datos.update({'r_del':self.r_del.text, 'r_tra':self.r_tra.text, 'frenos':self.frenos.text, 'pastillas':self.pastillas.text, 'luces':self.luces.text})
        self.manager.current = 'pag5'

class PaginaCinco(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("5. FINALIZAR TRABAJO")
        self.itv_m = TextInput(hint_text="Mes ITV (MM)", size_hint_y=None, height='50dp')
        self.itv_a = TextInput(hint_text="Año ITV (AAAA)", size_hint_y=None, height='50dp')
        self.obs = TextInput(hint_text="Observaciones / Reparaciones", multiline=True, size_hint_y=None, height='120dp')
        self.cos = TextInput(hint_text="Coste TOTAL (€)", size_hint_y=None, height='50dp')
        
        for w in [self.itv_m, self.itv_a, self.obs, self.cos]: self.content.add_widget(w)
        
        btn_v = Button(text="VOLVER"); btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag4'))
        btn_g = Button(text="GUARDAR Y ENVIAR", background_color=(0.1, 0.6, 0.3, 1), bold=True)
        btn_g.bind(on_press=self.finalizar)
        self.nav_bar.add_widget(btn_v); self.nav_bar.add_widget(btn_g)
        self.add_widget(l)

    def finalizar(self, x):
        d = App.get_running_app().datos
        f_hoy = datetime.now().strftime("%d/%m/%Y")
        conn = conectar_bd()
        if conn:
            c = conn.cursor()
            valores = (d.get('mod'), d.get('mat'), d.get('km'), d.get('aceite'), d.get('aceite_km'), 
                       d.get('caja'), d.get('caja_km'), d.get('f_aire'), d.get('f_aceite'), 
                       d.get('f_polen'), d.get('f_comb'), d.get('anti'), d.get('r_del'), 
                       d.get('r_tra'), d.get('correa'), d.get('frenos'), d.get('pastillas'), 
                       d.get('luces'), self.obs.text, self.cos.text, f_hoy, d.get('mec'), 
                       self.itv_m.text, self.itv_a.text)
            c.execute('''INSERT INTO fichas (modelo, matricula, km_act, aceite_det, aceite_km, 
                         caja_det, caja_km, f_aire, f_aceite, f_polen, f_comb, anti_det, 
                         r_del_km, r_tra_km, correa, frenos, pastillas, luces, averia, 
                         coste, fecha, mecanico, itv_mes, itv_ano) 
                         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', valores)
            conn.commit(); conn.close()
            self.manager.current = 'pag1'

class PantallaHistorial(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("HISTORIAL DE TRABAJOS")
        self.busc = TextInput(hint_text="Escribe la matrícula...", size_hint_y=None, height='55dp')
        self.busc.bind(text=self.actualizar_lista)
        l.add_widget(self.busc, index=2)
        btn_v = Button(text="VOLVER"); btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag1'))
        self.nav_bar.add_widget(btn_v); self.add_widget(l)

    def actualizar_lista(self, *args):
        self.content.clear_widgets()
        conn = conectar_bd()
        if conn:
            c = conn.cursor()
            c.execute("SELECT id, matricula, fecha, modelo FROM fichas WHERE matricula LIKE ?", (f'%{self.busc.text}%',))
            for f in c.fetchall():
                btn = Button(text=f"{f[2]} | {f[1]} ({f[3]})", size_hint_y=None, height='50dp')
                btn.bind(on_press=lambda x, id_f=f[0]: self.ver_detalle(id_f))
                self.content.add_widget(btn)
            conn.close()

    def ver_detalle(self, id_f):
        conn = conectar_bd()
        f = conn.cursor().execute("SELECT * FROM fichas WHERE id=?", (id_f,)).fetchone()
        conn.close()
        
        informe = (
            f"🛠️ *EL GARAJE DE PIPO RP Y AJ*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📋 *FICHA TÉCNICA DE TRABAJO*\n"
            f"📅 *Fecha:* {f[21]}\n"
            f"🚗 *Vehículo:* {f[1]} ({f[2]})\n"
            f"📍 *KM:* {f[3]}\n"
            f"👤 *Mecánico:* {f[22]}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ *MANTENIMIENTO:*\n"
            f"• Aceite: {f[4]} (Próx: {f[5]})\n"
            f"• Caja: {f[6]} (Próx: {f[7]})\n"
            f"• Anticongelante: {f[12]}\n"
            f"• Ruedas Del: {f[13]} km | Tras: {f[14]} km\n"
            f"• Frenos: {f[16]} | Pastillas: {f[17]}\n"
            f"• Luces: {f[18]} | Correa: {f[15]}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ *REPARACIONES:*\n{f[19]}\n\n"
            f"💰 *TOTAL:* {f[20]}€\n"
            f"📅 *ITV:* {f[23]}/{f[24]}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"BY RAUL PLAZA"
        )
        webbrowser.open(f"https://wa.me/?text={urllib.parse.quote(informe)}")

class MiApp(App):
    datos = {}
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(PaginaUno(name='pag1'))
        sm.add_widget(PaginaDos(name='pag2'))
        sm.add_widget(PaginaTres(name='pag3'))
        sm.add_widget(PaginaCuatro(name='pag4'))
        sm.add_widget(PaginaCinco(name='pag5'))
        sm.add_widget(PantallaHistorial(name='historial'))
        return sm

if __name__ == '__main__':
    MiApp().run()
