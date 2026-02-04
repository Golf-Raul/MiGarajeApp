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
from kivy.uix.checkbox import CheckBox
from kivy.graphics import Color, Rectangle
from kivy.utils import platform
import webbrowser

# --- CONEXIÓN BASE DE DATOS ---
def conectar_bd():
    if platform == 'android':
        from android.storage import app_storage_path
        path = app_storage_path()
    else:
        path = os.path.dirname(os.path.abspath(__file__))
    
    db_path = os.path.join(path, 'garaje_pipo_v2026.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS fichas 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       mecanico TEXT, modelo TEXT, matricula TEXT, km_act TEXT,
                       aceite TEXT, f_aire TEXT, f_aceite TEXT, f_polen TEXT, f_comb TEXT,
                       c_dist TEXT, c_aux TEXT, bomba TEXT,
                       r_del TEXT, r_tra TEXT, discos TEXT, pastillas TEXT, luces TEXT,
                       averia TEXT, coste TEXT, fecha TEXT, itv TEXT)''')
    conn.commit()
    return conn

# --- FILA DE TRABAJO ---
class FilaPieza(BoxLayout):
    def __init__(self, nombre, hint="Ref/KM:", **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height='50dp', spacing=5)
        self.check = CheckBox(size_hint_x=0.15, color=(0, 1, 0, 2))
        self.label = Label(text=nombre, size_hint_x=0.35, halign='left')
        self.extra = TextInput(hint_text=hint, size_hint_x=0.5, multiline=False)
        self.add_widget(self.check); self.add_widget(self.label); self.add_widget(self.extra)

    def get_data(self):
        estado = "✅ OK" if self.check.active else "❌ PENDIENTE"
        return f"{estado} ({self.extra.text})" if self.extra.text else estado

# --- PANTALLAS (P1 A P5 SE MANTIENEN IGUAL) ---
class PaginaBase(Screen):
    def crear_cabecera(self, titulo):
        layout = BoxLayout(orientation='vertical')
        header = Label(text=f"{titulo}\nGARAJE PIPO - RAUL PLAZA", size_hint_y=None, height='80dp', bold=True)
        with header.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            self.rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=self._actualizar_rect, pos=self._actualizar_rect)
        layout.add_widget(header)
        self.scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8, padding=10)
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        layout.add_widget(self.scroll)
        self.footer = BoxLayout(size_hint_y=None, height='60dp', spacing=10, padding=5)
        layout.add_widget(self.footer)
        return layout

    def _actualizar_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

# [Las clases Pantalla1, 2, 3, 4 y 5 se mantienen con la misma lógica de guardado que ya te funciona]
# (Omitidas aquí por brevedad para centrarme en el Historial solicitado)

class Pantalla1(PaginaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_cabecera("1. DATOS VEHÍCULO")
        self.mec = TextInput(hint_text="Mecánico"); self.mod = TextInput(hint_text="Modelo")
        self.mat = TextInput(hint_text="Matrícula"); self.km = TextInput(hint_text="KM Actuales")
        for w in [self.mec, self.mod, self.mat, self.km]: 
            w.size_hint_y = None; w.height = '50dp'; self.content.add_widget(w)
        btn_h = Button(text="HISTORIAL"); btn_h.bind(on_press=lambda x: setattr(self.manager, 'current', 'historial'))
        btn_s = Button(text="SIGUIENTE", background_color=(0,0.7,0.3,1)); btn_s.bind(on_press=self.sig)
        self.footer.add_widget(btn_h); self.footer.add_widget(btn_s); self.add_widget(l)
    def sig(self, x):
        App.get_running_app().temp = {'mec':self.mec.text,'mod':self.mod.text,'mat':self.mat.text,'km':self.km.text}
        self.manager.current = 'pag2'

class Pantalla2(PaginaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_cabecera("2. FILTROS")
        self.aceite = FilaPieza("Aceite"); self.f_aire = FilaPieza("F. Aire"); self.f_aceite = FilaPieza("F. Aceite")
        for w in [self.aceite, self.f_aire, self.f_aceite]: self.content.add_widget(w)
        btn_s = Button(text="SIGUIENTE"); btn_s.bind(on_press=self.sig)
        self.footer.add_widget(btn_s); self.add_widget(l)
    def sig(self, x):
        App.get_running_app().temp.update({'aceite':self.aceite.get_data(), 'f_aire':self.f_aire.get_data(), 'f_aceite':self.f_aceite.get_data()})
        self.manager.current = 'pag3'

class Pantalla3(PaginaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_cabecera("3. CORREAS")
        self.dist = FilaPieza("Distribución"); self.aux = FilaPieza("Auxiliar"); self.bomba = FilaPieza("Bomba Agua")
        for w in [self.dist, self.aux, self.bomba]: self.content.add_widget(w)
        btn_s = Button(text="SIGUIENTE"); btn_s.bind(on_press=self.sig)
        self.footer.add_widget(btn_s); self.add_widget(l)
    def sig(self, x):
        App.get_running_app().temp.update({'dist':self.dist.get_data(), 'aux':self.aux.get_data(), 'bomba':self.bomba.get_data()})
        self.manager.current = 'pag4'

class Pantalla4(PaginaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_cabecera("4. FRENOS Y LUCES")
        self.dis = FilaPieza("Discos"); self.pas = FilaPieza("Pastillas"); self.luc = FilaPieza("Luces")
        for w in [self.dis, self.pas, self.luc]: self.content.add_widget(w)
        btn_s = Button(text="SIGUIENTE"); btn_s.bind(on_press=self.sig)
        self.footer.add_widget(btn_s); self.add_widget(l)
    def sig(self, x):
        App.get_running_app().temp.update({'dis':self.dis.get_data(), 'pas':self.pas.get_data(), 'luc':self.luc.get_data()})
        self.manager.current = 'pag5'

class Pantalla5(PaginaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_cabecera("5. FINALIZAR")
        self.obs = TextInput(hint_text="Observaciones", multiline=True, height='100dp', size_hint_y=None)
        self.cos = TextInput(hint_text="Precio Final €", height='50dp', size_hint_y=None)
        self.content.add_widget(self.obs); self.content.add_widget(self.cos)
        btn_g = Button(text="GUARDAR TRABAJO", background_color=(0,0.6,0.2,1)); btn_g.bind(on_press=self.guardar)
        self.footer.add_widget(btn_g); self.add_widget(l)
    def guardar(self, x):
        t = App.get_running_app().temp
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        conn = conectar_bd(); c = conn.cursor()
        c.execute('''INSERT INTO fichas (mecanico, modelo, matricula, km_act, aceite, f_aire, f_aceite, f_polen, f_comb, c_dist, c_aux, bomba, r_del, r_tra, discos, pastillas, luces, averia, coste, fecha, itv) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (t.get('mec'), t.get('mod'), t.get('mat'), t.get('km'), t.get('aceite'), t.get('f_aire'), t.get('f_aceite'), '', '', t.get('dist'), t.get('aux'), t.get('bomba'), '', '', t.get('dis'), t.get('pas'), t.get('luc'), self.obs.text, self.cos.text, fecha, ''))
        conn.commit(); conn.close()
        self.manager.current = 'historial'

# --- HISTORIAL MEJORADO CON OPCIÓN WHATSAPP COMPLETO ---
class PantallaHistorial(PaginaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_cabecera("HISTORIAL DE TRABAJOS")
        self.busc = TextInput(hint_text="🔍 Buscar Matrícula...", size_hint_y=None, height='50dp')
        self.busc.bind(text=self.actualizar)
        l.add_widget(self.busc, index=2)
        btn_v = Button(text="VOLVER", background_color=(0.5,0.5,0.5,1)); btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag1'))
        self.footer.add_widget(btn_v); self.add_widget(l)

    def on_enter(self): self.actualizar()

    def actualizar(self, *args):
        self.content.clear_widgets()
        conn = conectar_bd(); c = conn.cursor()
        c.execute("SELECT id, matricula, fecha, modelo FROM fichas WHERE matricula LIKE ? ORDER BY id DESC", (f'%{self.busc.text}%',))
        for f in c.fetchall():
            fila = BoxLayout(size_hint_y=None, height='60dp', spacing=5)
            # Botón de informe
            btn = Button(text=f"📄 {f[1]} - {f[2]}", size_hint_x=0.8, background_color=(0.1, 0.5, 0.8, 1))
            btn.bind(on_press=lambda x, id_f=f[0]: self.enviar_todo_wa(id_f))
            # Botón eliminar
            btn_x = Button(text="❌", size_hint_x=0.2, background_color=(1,0,0,1))
            btn_x.bind(on_press=lambda x, id_f=f[0]: self.borrar(id_f))
            fila.add_widget(btn); fila.add_widget(btn_x); self.content.add_widget(fila)
        conn.close()

    def enviar_todo_wa(self, id_f):
        conn = conectar_bd()
        f = conn.cursor().execute("SELECT * FROM fichas WHERE id=?", (id_f,)).fetchone()
        conn.close()
        # DOCUMENTO DETALLADO PARA WHATSAPP
        msg = f"🛠️ *INFORME MECÁNICO - RA y AJ los PIPOS*\n"
        msg += f"━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"🚗 *VEHÍCULO:* {f[2]} ({f[3]})\n"
        msg += f"📅 *FECHA:* {f[20]} | 📍 *KM:* {f[4]}\n"
        msg += f"👨‍🔧 *MECÁNICO:* {f[1]}\n"
        msg += f"━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"🛢️ *ACEITE:* {f[5]}\n"
        msg += f"💨 *FILTRO AIRE:* {f[6]}\n"
        msg += f"⚙️ *FILTRO ACEITE:* {f[7]}\n"
        msg += f"⛓️ *DISTRIBUCIÓN:* {f[10]}\n"
        msg += f"📉 *CORREA AUX:* {f[11]}\n"
        msg += f"💧 *BOMBA AGUA:* {f[12]}\n"
        msg += f"🛑 *DISCOS:* {f[15]}\n"
        msg += f"🥢 *PASTILLAS:* {f[16]}\n"
        msg += f"💡 *LUCES:* {f[17]}\n"
        msg += f"📝 *NOTAS:* {f[18]}\n"
        msg += f"━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"💰 *COSTE TOTAL:* {f[19]} €\n"
        msg += f"\n_Gracias por su confianza_"
        
        webbrowser.open(f"https://wa.me/?text={urllib.parse.quote(msg)}")

    def borrar(self, id_f):
        conn = conectar_bd(); conn.execute("DELETE FROM fichas WHERE id=?", (id_f,)); conn.commit(); conn.close()
        self.actualizar()

class MiApp(App):
    temp = {}
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(Pantalla1(name='pag1')); sm.add_widget(Pantalla2(name='pag2'))
        sm.add_widget(Pantalla3(name='pag3')); sm.add_widget(Pantalla4(name='pag4'))
        sm.add_widget(Pantalla5(name='pag5')); sm.add_widget(PantallaHistorial(name='historial'))
        return sm

if __name__ == '__main__':
    MiApp().run()
