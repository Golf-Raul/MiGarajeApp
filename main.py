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

# --- BASE DE DATOS REPARADA ---
def conectar_bd():
    # Usamos la ruta que te funcionaba antes
    if platform == 'android':
        from android.storage import app_storage_path
        path = app_storage_path()
    else:
        path = os.path.dirname(os.path.abspath(__file__))
    
    db_path = os.path.join(path, 'garaje_pipo_v2026.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Mantenemos la tabla con TODOS los campos nuevos pero con la estructura antigua
    cursor.execute('''CREATE TABLE IF NOT EXISTS fichas 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       mecanico TEXT, modelo TEXT, matricula TEXT, km_act TEXT,
                       aceite TEXT, f_aire TEXT, f_aceite TEXT, f_polen TEXT, f_comb TEXT,
                       c_dist TEXT, c_aux TEXT, bomba TEXT,
                       r_del TEXT, r_tra TEXT, discos TEXT, pastillas TEXT, luces TEXT,
                       averia TEXT, coste TEXT, fecha TEXT, itv TEXT)''')
    conn.commit()
    return conn

# --- FILA CON CHECK Y REF (COMO PEDISTE) ---
class FilaPieza(BoxLayout):
    def __init__(self, nombre, hint="Ref/KM:", **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height='50dp', spacing=5)
        self.check = CheckBox(size_hint_x=0.15, color=(0, 1, 0, 2))
        self.label = Label(text=nombre, size_hint_x=0.35, halign='left')
        self.extra = TextInput(hint_text=hint, size_hint_x=0.5, multiline=False)
        self.add_widget(self.check); self.add_widget(self.label); self.add_widget(self.extra)

    def get_data(self):
        estado = "✅" if self.check.active else "❌"
        return f"{estado} {self.extra.text}"

# --- PANTALLAS (ESTRUCTURA DE SIEMPRE) ---
class PaginaBase(Screen):
    def crear_cabecera(self, titulo):
        layout = BoxLayout(orientation='vertical')
        header = Label(text=f"{titulo}\nBY Los Pipos RP y AJ", size_hint_y=None, height='80dp', bold=True)
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

class Pantalla1(PaginaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_cabecera("1. DATOS GENERALES")
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
        l = self.crear_cabecera("2. FILTROS Y ACEITE")
        self.aceite = FilaPieza("Aceite"); self.f_aire = FilaPieza("F. Aire")
        self.f_aceite = FilaPieza("F. Aceite"); self.f_polen = FilaPieza("F. Polen"); self.f_comb = FilaPieza("F. Comb")
        for w in [self.aceite, self.f_aire, self.f_aceite, self.f_polen, self.f_comb]: self.content.add_widget(w)
        btn_s = Button(text="SIGUIENTE"); btn_s.bind(on_press=self.sig)
        self.footer.add_widget(btn_s); self.add_widget(l)

    def sig(self, x):
        App.get_running_app().temp.update({
            'aceite':self.aceite.get_data(), 'f_aire':self.f_aire.get_data(), 
            'f_aceite':self.f_aceite.get_data(), 'f_polen':self.f_polen.get_data(), 'f_comb':self.f_comb.get_data()
        })
        self.manager.current = 'pag3'

class Pantalla3(PaginaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_cabecera("3. MECÁNICA")
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
        l = self.crear_cabecera("4. RUEDAS Y FRENOS")
        self.rd = FilaPieza("Ruedas Del."); self.rt = FilaPieza("Ruedas Tra.")
        self.dis = FilaPieza("Discos"); self.pas = FilaPieza("Pastillas"); self.luc = FilaPieza("Luces")
        for w in [self.rd, self.rt, self.dis, self.pas, self.luc]: self.content.add_widget(w)
        btn_s = Button(text="SIGUIENTE"); btn_s.bind(on_press=self.sig)
        self.footer.add_widget(btn_s); self.add_widget(l)

    def sig(self, x):
        App.get_running_app().temp.update({
            'rd':self.rd.get_data(), 'rt':self.rt.get_data(), 
            'dis':self.dis.get_data(), 'pas':self.pas.get_data(), 'luc':self.luc.get_data()
        })
        self.manager.current = 'pag5'

class Pantalla5(PaginaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_cabecera("5. FINALIZAR")
        self.obs = TextInput(hint_text="Notas/Averías", multiline=True, height='100dp', size_hint_y=None)
        self.itv = TextInput(hint_text="Próxima ITV", height='50dp', size_hint_y=None)
        self.cos = TextInput(hint_text="Precio Final €", height='50dp', size_hint_y=None)
        self.content.add_widget(self.obs); self.content.add_widget(self.itv); self.content.add_widget(self.cos)
        btn_g = Button(text="GUARDAR TODO", background_color=(0,0.6,0.2,1)); btn_g.bind(on_press=self.guardar)
        self.footer.add_widget(btn_g); self.add_widget(l)

    def guardar(self, x):
        t = App.get_running_app().temp
        fecha = datetime.now().strftime("%d/%m/%Y")
        conn = conectar_bd()
        c = conn.cursor()
        c.execute('''INSERT INTO fichas (mecanico, modelo, matricula, km_act, aceite, f_aire, f_aceite, f_polen, f_comb, c_dist, c_aux, bomba, r_del, r_tra, discos, pastillas, luces, averia, coste, fecha, itv) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (t.get('mec'), t.get('mod'), t.get('mat'), t.get('km'), t.get('aceite'), t.get('f_aire'), t.get('f_aceite'), t.get('f_polen'), t.get('f_comb'), t.get('dist'), t.get('aux'), t.get('bomba'), t.get('rd'), t.get('rt'), t.get('dis'), t.get('pas'), t.get('luc'), self.obs.text, self.cos.text, fecha, self.itv.text))
        conn.commit(); conn.close()
        self.manager.current = 'historial'

class PantallaHistorial(PaginaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_cabecera("HISTORIAL")
        self.busc = TextInput(hint_text="Buscar Matrícula...", size_hint_y=None, height='50dp')
        self.busc.bind(text=self.actualizar)
        l.add_widget(self.busc, index=2)
        btn_v = Button(text="VOLVER"); btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag1'))
        self.footer.add_widget(btn_v); self.add_widget(l)

    def on_enter(self): self.actualizar()

    def actualizar(self, *args):
        self.content.clear_widgets()
        conn = conectar_bd()
        c = conn.cursor()
        c.execute("SELECT id, matricula, fecha, modelo FROM fichas WHERE matricula LIKE ? ORDER BY id DESC", (f'%{self.busc.text}%',))
        for f in c.fetchall():
            fila = BoxLayout(size_hint_y=None, height='50dp', spacing=5)
            btn = Button(text=f"{f[2]} | {f[1]} | {f[3]}", size_hint_x=0.8)
            btn.bind(on_press=lambda x, id_f=f[0]: self.whatsapp(id_f))
            btn_x = Button(text="X", size_hint_x=0.2, background_color=(1,0,0,1))
            btn_x.bind(on_press=lambda x, id_f=f[0]: self.borrar(id_f))
            fila.add_widget(btn); fila.add_widget(btn_x); self.content.add_widget(fila)
        conn.close()

    def borrar(self, id_f):
        conn = conectar_bd(); conn.execute("DELETE FROM fichas WHERE id=?", (id_f,)); conn.commit(); conn.close()
        self.actualizar()

    def whatsapp(self, id_f):
        conn = conectar_bd(); f = conn.cursor().execute("SELECT * FROM fichas WHERE id=?", (id_f,)).fetchone(); conn.close()
        msg = f"🚗 *GARAJE PIPO*\nMatrícula: {f[3]}\nKilómetros: {f[4]}\n⚙️ Aceite: {f[5]}\n⚙️ Aire: {f[6]}\n⚙️ Distribución: {f[10]}\n💰 Total: {f[19]}€\nBY RAUL PLAZA"
        webbrowser.open(f"https://wa.me/?text={urllib.parse.quote(msg)}")

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
