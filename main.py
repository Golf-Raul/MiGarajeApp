import sqlite3
import os
import urllib.parse
from datetime import datetime, timedelta
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.utils import platform
import webbrowser

# --- CONFIGURACIÓN DE BASE DE DATOS SEGURA ---
def conectar_bd():
    try:
        if platform == 'android':
            from android.storage import app_storage_path
            ruta_dir = app_storage_path()
        else:
            ruta_dir = os.path.dirname(os.path.abspath(__file__))
        
        ruta_db = os.path.join(ruta_dir, 'garaje_pipo_v2026.db')
        conn = sqlite3.connect(ruta_db)
        cursor = conn.cursor()
        # Aseguramos que la tabla existe con todos los campos
        cursor.execute('''CREATE TABLE IF NOT EXISTS fichas 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           modelo TEXT, matricula TEXT, km_act TEXT,
                           aceite_det TEXT, aceite_km TEXT,
                           caja_det TEXT, caja_km TEXT,
                           f_aire TEXT, f_aceite TEXT, f_polen TEXT, f_comb TEXT, 
                           anti_det TEXT, r_del_km TEXT, r_tra_km TEXT, 
                           correa TEXT, frenos TEXT, pastillas TEXT, luces TEXT, 
                           averia TEXT, coste TEXT, fecha TEXT, 
                           mecanico TEXT, itv_mes TEXT, itv_ano TEXT)''')
        conn.commit()
        return conn
    except Exception as e:
        print(f"ERROR CRÍTICO BD: {e}")
        return None

class FilaCheck(BoxLayout):
    def __init__(self, texto_hint, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height='50dp', **kwargs)
        self.input = TextInput(hint_text=texto_hint, size_hint_x=0.8, multiline=False)
        self.check = CheckBox(size_hint_x=0.2, color=(0,0,0,1))
        self.add_widget(self.input)
        self.add_widget(self.check)
    
    def get_val(self):
        marca = "[OK] " if self.check.active else "[ ] "
        return marca + self.input.text

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
        self.mec = TextInput(hint_text="Mecánico", size_hint_y=None, height='50dp')
        self.mod = TextInput(hint_text="Modelo", size_hint_y=None, height='50dp')
        self.mat = TextInput(hint_text="Matrícula", size_hint_y=None, height='50dp')
        self.km = TextInput(hint_text="KM Actuales", size_hint_y=None, height='50dp')
        for w in [self.mec, self.mod, self.mat, self.km]: self.content.add_widget(w)
        btn_h = Button(text="VER HISTORIAL", background_color=(0.5,0.5,0.5,1)); btn_h.bind(on_press=lambda x: setattr(self.manager, 'current', 'historial'))
        btn_s = Button(text="SIGUIENTE", background_color=(0.1, 0.5, 0.8, 1)); btn_s.bind(on_press=self.sig)
        self.nav_bar.add_widget(btn_h); self.nav_bar.add_widget(btn_s)
        self.add_widget(l)

    def sig(self, x):
        App.get_running_app().datos.update({'mec':self.mec.text,'mod':self.mod.text,'mat':self.mat.text,'km':self.km.text})
        self.manager.current = 'pag2'

class PaginaDos(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("2. ACEITES Y LÍQUIDOS")
        self.aceite = FilaCheck("Aceite Motor")
        self.aceite_km = TextInput(hint_text="KM Próx. Cambio", size_hint_y=None, height='50dp')
        self.caja = FilaCheck("Aceite Caja")
        self.caja_km = TextInput(hint_text="KM Cambio Caja", size_hint_y=None, height='50dp')
        self.anti = FilaCheck("Anticongelante")
        for w in [self.aceite, self.aceite_km, self.caja, self.caja_km, self.anti]: self.content.add_widget(w)
        btn_v = Button(text="VOLVER"); btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag1'))
        btn_s = Button(text="SIGUIENTE", background_color=(0.1, 0.5, 0.8, 1)); btn_s.bind(on_press=self.sig)
        self.nav_bar.add_widget(btn_v); self.nav_bar.add_widget(btn_s)
        self.add_widget(l)

    def sig(self, x):
        App.get_running_app().datos.update({'aceite':self.aceite.get_val(),'aceite_km':self.aceite_km.text,'caja':self.caja.get_val(),'caja_km':self.caja_km.text,'anti':self.anti.get_val()})
        self.manager.current = 'pag3'

class PaginaTres(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("3. FILTROS Y CORREAS")
        self.f_aire = FilaCheck("Filtro Aire")
        self.f_aceite = FilaCheck("Filtro Aceite")
        self.f_polen = FilaCheck("Filtro Polen")
        self.f_comb = FilaCheck("Filtro Combustible")
        self.correa = FilaCheck("Correa")
        for w in [self.f_aire, self.f_aceite, self.f_polen, self.f_comb, self.correa]: self.content.add_widget(w)
        btn_v = Button(text="VOLVER"); btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag2'))
        btn_s = Button(text="SIGUIENTE", background_color=(0.1, 0.5, 0.8, 1)); btn_s.bind(on_press=self.sig)
        self.nav_bar.add_widget(btn_v); self.nav_bar.add_widget(btn_s)
        self.add_widget(l)

    def sig(self, x):
        App.get_running_app().datos.update({'f_aire':self.f_aire.get_val(),'f_aceite':self.f_aceite.get_val(),'f_polen':self.f_polen.get_val(),'f_comb':self.f_comb.get_val(),'correa':self.correa.get_val()})
        self.manager.current = 'pag4'

class PaginaCuatro(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("4. RUEDAS Y FRENOS")
        self.r_del = FilaCheck("Ruedas Delanteras") # AHORA CON CHECK
        self.r_tra = FilaCheck("Ruedas Traseras")   # AHORA CON CHECK
        self.frenos = FilaCheck("Discos")
        self.pastillas = FilaCheck("Pastillas")
        self.luces = FilaCheck("Luces")
        for w in [self.r_del, self.r_tra, self.frenos, self.pastillas, self.luces]: self.content.add_widget(w)
        btn_v = Button(text="VOLVER"); btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag3'))
        btn_s = Button(text="SIGUIENTE", background_color=(0.1, 0.5, 0.8, 1)); btn_s.bind(on_press=self.sig)
        self.nav_bar.add_widget(btn_v); self.nav_bar.add_widget(btn_s)
        self.add_widget(l)

    def sig(self, x):
        App.get_running_app().datos.update({'r_del':self.r_del.get_val(),'r_tra':self.r_tra.get_val(),'frenos':self.frenos.get_val(),'pastillas':self.pastillas.get_val(),'luces':self.luces.get_val()})
        self.manager.current = 'pag5'

class PaginaCinco(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("5. FINALIZAR")
        self.itv_m = TextInput(hint_text="Mes ITV (MM)", size_hint_y=None, height='50dp')
        self.itv_a = TextInput(hint_text="Año ITV (AAAA)", size_hint_y=None, height='50dp')
        self.obs = TextInput(hint_text="Averías / Notas", multiline=True, size_hint_y=None, height='100dp')
        self.cos = TextInput(hint_text="Coste (€)", size_hint_y=None, height='50dp')
        for w in [self.itv_m, self.itv_a, self.obs, self.cos]: self.content.add_widget(w)
        btn_v = Button(text="VOLVER"); btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag4'))
        btn_g = Button(text="GUARDAR Y RESETEAR", background_color=(0.1, 0.6, 0.3, 1)); btn_g.bind(on_press=self.finalizar)
        self.nav_bar.add_widget(btn_v); self.nav_bar.add_widget(btn_g)
        self.add_widget(l)

    def finalizar(self, x):
        d = App.get_running_app().datos
        f_hoy = datetime.now().strftime("%d/%m/%Y")
        
        # 1. GUARDADO EN BASE DE DATOS
        conn = conectar_bd()
        if conn:
            c = conn.cursor()
            c.execute('''INSERT INTO fichas (modelo, matricula, km_act, aceite_det, aceite_km, caja_det, caja_km, f_aire, f_aceite, f_polen, f_comb, anti_det, r_del_km, r_tra_km, correa, frenos, pastillas, luces, averia, coste, fecha, mecanico, itv_mes, itv_ano) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', 
            (d.get('mod'), d.get('mat'), d.get('km'), d.get('aceite'), d.get('aceite_km'), d.get('caja'), d.get('caja_km'), d.get('f_aire'), d.get('f_aceite'), d.get('f_polen'), d.get('f_comb'), d.get('anti'), d.get('r_del'), d.get('r_tra'), d.get('correa'), d.get('frenos'), d.get('pastillas'), d.get('luces'), self.obs.text, self.cos.text, f_hoy, d.get('mec'), self.itv_m.text, self.itv_a.text))
            conn.commit(); conn.close()

        # 2. SISTEMA DE AVISO (SIMULADO EN LOG PARA EL SISTEMA)
        print(f"AVISO: Programada alerta ITV para {self.itv_m.text}/{self.itv_a.text} para el coche {d.get('mat')}")

        # 3. RESETEO TOTAL DE CAMPOS
        for screen in self.manager.screens:
            for widget in screen.walk():
                if isinstance(widget, TextInput): widget.text = ""
                if isinstance(widget, CheckBox): widget.active = False
        App.get_running_app().datos = {}
        self.manager.current = 'pag1'

class PantallaHistorial(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("HISTORIAL")
        self.busc = TextInput(hint_text="Matrícula...", size_hint_y=None, height='50dp')
        self.busc.bind(text=self.actualizar_lista)
        l.add_widget(self.busc, index=2)
        btn_v = Button(text="VOLVER"); btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag1'))
        self.nav_bar.add_widget(btn_v); self.add_widget(l)

    def actualizar_lista(self, *args):
        self.content.clear_widgets()
        conn = conectar_bd()
        if conn:
            c = conn.cursor()
            c.execute("SELECT id, matricula, fecha, modelo FROM fichas WHERE matricula LIKE ? ORDER BY id DESC", (f'%{self.busc.text}%',))
            for f in c.fetchall():
                btn = Button(text=f"{f[2]} - {f[1]} ({f[3]})", size_hint_y=None, height='55dp', background_color=(0.9,0.9,0.9,1), color=(0,0,0,1))
                btn.bind(on_press=lambda x, id_f=f[0]: self.enviar_wa(id_f))
                self.content.add_widget(btn)
            conn.close()

    def enviar_wa(self, id_f):
        conn = conectar_bd()
        f = conn.cursor().execute("SELECT * FROM fichas WHERE id=?", (id_f,)).fetchone()
        conn.close()
        texto = (f"🛠️ *GARAJE PIPO RP Y AJ - INFORME*\n🚗 *Coche:* {f[1]} ({f[2]})\n📍 *KM:* {f[3]}\n📅 *Fecha:* {f[21]}\n"
                 f"━━━━━━━━━━━━\n✅ *REVISIÓN:*\n• Aceite: {f[4]} (Prox: {f[5]})\n• Caja: {f[6]} (Prox: {f[7]})\n• Anticong: {f[12]}\n"
                 f"• Filtros: Aire:{f[8]} Aceite:{f[9]} Polen:{f[10]} Comb:{f[11]}\n"
                 f"• Ruedas Del: {f[13]}\n• Ruedas Tra: {f[14]}\n• Correa: {f[15]}\n• Frenos: {f[16]} | Pastillas: {f[17]}\n"
                 f"━━━━━━━━━━━━\n⚠️ *NOTAS:* {f[19]}\n💰 *TOTAL:* {f[20]}€\n📅 *PROX. ITV:* {f[23]}/{f[24]}\nBY RAUL PLAZA")
        webbrowser.open(f"https://wa.me/?text={urllib.parse.quote(texto)}")

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
