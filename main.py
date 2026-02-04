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

# --- BASE DE DATOS PROFESIONAL ---
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
                       c_distribucion TEXT, c_auxiliar TEXT, bomba_agua TEXT,
                       r_del TEXT, r_tra TEXT, discos TEXT, pastillas TEXT, luces TEXT,
                       averia TEXT, coste TEXT, fecha TEXT, itv TEXT)''')
    conn.commit()
    return conn

# --- COMPONENTE TIPO "FILTRO/PIEZA" ---
class FilaPieza(BoxLayout):
    def __init__(self, nombre, hint_extra="Ref/KM:", **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height='50dp', spacing=5)
        self.check = CheckBox(size_hint_x=0.15, color=(0, 1, 0, 2)) # Verde si OK
        self.label = Label(text=nombre, size_hint_x=0.35, halign='left', text_size=(200, None))
        self.extra = TextInput(hint_text=hint_extra, size_hint_x=0.5, multiline=False)
        
        self.add_widget(self.check)
        self.add_widget(self.label)
        self.add_widget(self.extra)

    def get_val(self):
        estado = "✅ OK" if self.check.active else "❌ PENDIENTE"
        return f"{estado} | {self.extra.text}"

# --- PANTALLAS ---
class PaginaGenerica(Screen):
    def preparar(self, titulo):
        layout = BoxLayout(orientation='vertical')
        # Cabecera Azul
        header = Label(text=f"{titulo}\nGARAJE PIPO - RAUL PLAZA", size_hint_y=None, height='80dp', bold=True, halign='center')
        with header.canvas.before:
            Color(0.1, 0.4, 0.8, 1)
            self.rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=self._update_rect, pos=self._update_rect)
        layout.add_widget(header)

        self.scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        layout.add_widget(self.scroll)

        self.nav = BoxLayout(size_hint_y=None, height='60dp', spacing=10, padding=5)
        layout.add_widget(self.nav)
        return layout

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class Pantalla1(PaginaGenerica):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.preparar("1. DATOS VEHÍCULO")
        self.mec = TextInput(hint_text="Mecánico", size_hint_y=None, height='50dp')
        self.mod = TextInput(hint_text="Modelo", size_hint_y=None, height='50dp')
        self.mat = TextInput(hint_text="Matrícula", size_hint_y=None, height='50dp')
        self.km = TextInput(hint_text="Kilómetros Actuales", size_hint_y=None, height='50dp')
        for w in [self.mec, self.mod, self.mat, self.km]: self.content.add_widget(w)
        
        btn_h = Button(text="HISTORIAL", background_color=(0.5,0.5,0.5,1))
        btn_h.bind(on_press=lambda x: setattr(self.manager, 'current', 'historial'))
        btn_s = Button(text="SIGUIENTE", background_color=(0,0.7,0,1))
        btn_s.bind(on_press=self.sig)
        self.nav.add_widget(btn_h); self.nav.add_widget(btn_s)
        self.add_widget(l)

    def sig(self, x):
        App.get_running_app().datos.update({'mec':self.mec.text,'mod':self.mod.text,'mat':self.mat.text,'km':self.km.text})
        self.manager.current = 'pag2'

class Pantalla2(PaginaGenerica):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.preparar("2. FILTROS Y ACEITE")
        self.aceite = FilaPieza("Aceite Motor", "Ref/Tipo:")
        self.f_aire = FilaPieza("Filtro Aire", "Ref:")
        self.f_aceite = FilaPieza("Filtro Aceite", "Ref:")
        self.f_polen = FilaPieza("Filtro Polen", "Ref:")
        self.f_comb = FilaPieza("Filtro Combust.", "Ref:")
        for w in [self.aceite, self.f_aire, self.f_aceite, self.f_polen, self.f_comb]: self.content.add_widget(w)
        
        btn_v = Button(text="ATRÁS"); btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag1'))
        btn_s = Button(text="SIGUIENTE"); btn_s.bind(on_press=self.sig)
        self.nav.add_widget(btn_v); self.nav.add_widget(btn_s)
        self.add_widget(l)

    def sig(self, x):
        App.get_running_app().datos.update({
            'aceite':self.aceite.get_val(), 'f_aire':self.f_aire.get_val(),
            'f_aceite':self.f_aceite.get_val(), 'f_polen':self.f_polen.get_val(), 'f_comb':self.f_comb.get_val()
        })
        self.manager.current = 'pag3'

class Pantalla3(PaginaGenerica):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.preparar("3. CORREAS Y BOMBA")
        self.c_dist = FilaPieza("Distribución", "KM cambio:")
        self.c_aux = FilaPieza("C. Auxiliar", "Ref:")
        self.bomba = FilaPieza("Bomba Agua")
        for w in [self.c_dist, self.c_aux, self.bomba]: self.content.add_widget(w)
        
        btn_v = Button(text="ATRÁS"); btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag2'))
        btn_s = Button(text="SIGUIENTE"); btn_s.bind(on_press=self.sig)
        self.nav.add_widget(btn_v); self.nav.add_widget(btn_s)
        self.add_widget(l)

    def sig(self, x):
        App.get_running_app().datos.update({
            'c_dist':self.c_dist.get_val(), 'c_aux':self.c_aux.get_val(), 'bomba':self.bomba.get_val()
        })
        self.manager.current = 'pag4'

class Pantalla4(PaginaGenerica):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.preparar("4. RUEDAS Y FRENOS")
        self.r_del = FilaPieza("Ruedas Del.", "Marca/KM:")
        self.r_tra = FilaPieza("Ruedas Tras.", "Marca/KM:")
        self.discos = FilaPieza("Discos Freno", "Estado:")
        self.pastillas = FilaPieza("Pastillas", "Estado:")
        self.luces = FilaPieza("Luces/Faros", "Estado:")
        for w in [self.r_del, self.r_tra, self.discos, self.pastillas, self.luces]: self.content.add_widget(w)
        
        btn_v = Button(text="ATRÁS"); btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag3'))
        btn_s = Button(text="SIGUIENTE"); btn_s.bind(on_press=self.sig)
        self.nav.add_widget(btn_v); self.nav.add_widget(btn_s)
        self.add_widget(l)

    def sig(self, x):
        App.get_running_app().datos.update({
            'r_del':self.r_del.get_val(), 'r_tra':self.r_tra.get_val(),
            'discos':self.discos.get_val(), 'pastillas':self.pastillas.get_val(), 'luces':self.luces.get_val()
        })
        self.manager.current = 'pag5'

class Pantalla5(PaginaGenerica):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.preparar("5. FINALIZAR")
        self.itv = TextInput(hint_text="Próxima ITV (Mes/Año)", size_hint_y=None, height='50dp')
        self.obs = TextInput(hint_text="Otras averías o notas...", multiline=True, size_hint_y=None, height='120dp')
        self.coste = TextInput(hint_text="Coste Total (€)", size_hint_y=None, height='50dp')
        for w in [self.itv, self.obs, self.coste]: self.content.add_widget(w)
        
        btn_v = Button(text="ATRÁS"); btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag4'))
        btn_g = Button(text="GUARDAR Y FINALIZAR", background_color=(0,0.6,0.2,1))
        btn_g.bind(on_press=self.finalizar)
        self.nav.add_widget(btn_v); self.nav.add_widget(btn_g)
        self.add_widget(l)

    def finalizar(self, x):
        d = App.get_running_app().datos
        fecha = datetime.now().strftime("%d/%m/%Y")
        conn = conectar_bd()
        c = conn.cursor()
        c.execute('''INSERT INTO fichas (mecanico, modelo, matricula, km_act, aceite, f_aire, f_aceite, f_polen, f_comb, c_distribucion, c_auxiliar, bomba_agua, r_del, r_tra, discos, pastillas, luces, averia, coste, fecha, itv) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (d.get('mec'), d.get('mod'), d.get('mat'), d.get('km'), d.get('aceite'), d.get('f_aire'), d.get('f_aceite'), d.get('f_polen'), d.get('f_comb'), d.get('c_dist'), d.get('c_aux'), d.get('bomba'), d.get('r_del'), d.get('r_tra'), d.get('discos'), d.get('pastillas'), d.get('luces'), self.obs.text, self.coste.text, fecha, self.itv.text))
        conn.commit(); conn.close()
        
        # Reset total
        App.get_running_app().datos = {}
        for s in self.manager.screens:
            for w in s.walk():
                if isinstance(w, TextInput): w.text = ""
                if isinstance(w, CheckBox): w.active = False
        self.manager.current = 'pag1'

class PantallaHistorial(PaginaGenerica):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.preparar("HISTORIAL DE TRABAJOS")
        self.busc = TextInput(hint_text="Buscar Matrícula...", size_hint_y=None, height='50dp')
        self.busc.bind(text=self.actualizar)
        l.add_widget(self.busc, index=2)
        btn_v = Button(text="VOLVER"); btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag1'))
        self.nav.add_widget(btn_v); self.add_widget(l)

    def actualizar(self, *args):
        self.content.clear_widgets()
        conn = conectar_bd()
        c = conn.cursor()
        c.execute("SELECT id, matricula, fecha, modelo FROM fichas WHERE matricula LIKE ? ORDER BY id DESC", (f'%{self.busc.text}%',))
        for f in c.fetchall():
            fila = BoxLayout(size_hint_y=None, height='60dp', spacing=5)
            # Botón principal para enviar WhatsApp
            btn = Button(text=f"{f[2]} | {f[1]} | {f[3]}", size_hint_x=0.85)
            btn.bind(on_press=lambda x, id_f=f[0]: self.enviar_wa(id_f))
            # Botón [X] roja para borrar
            btn_del = Button(text="X", size_hint_x=0.15, background_color=(1,0,0,1), bold=True)
            btn_del.bind(on_press=lambda x, id_f=f[0]: self.borrar_entrada(id_f))
            
            fila.add_widget(btn); fila.add_widget(btn_del)
            self.content.add_widget(fila)
        conn.close()

    def borrar_entrada(self, id_f):
        conn = conectar_bd()
        conn.execute("DELETE FROM fichas WHERE id=?", (id_f,))
        conn.commit(); conn.close()
        self.actualizar()

    def enviar_wa(self, id_f):
        conn = conectar_bd()
        f = conn.cursor().execute("SELECT * FROM fichas WHERE id=?", (id_f,)).fetchone()
        conn.close()
        # Mensaje con Iconos para WhatsApp
        msg = f"🚗 *INFORME MANTENIMIENTO: {f[2]}*\n"
        msg += f"📅 Fecha: {f[20]} | 📍 KM: {f[4]}\n"
        msg += f"━━━━━━━━━━━━━\n"
        msg += f"🛢️ *Motor:* {f[5]}\n"
        msg += f"💨 *Filtros:* Aire: {f[6]} | Polen: {f[8]}\n"
        msg += f"⚙️ *Correas:* Dist: {f[10]} | Aux: {f[11]}\n"
        msg += f"💧 *Bomba Agua:* {f[12]}\n"
        msg += f"🛞 *Ruedas:* D: {f[13]} | T: {f[14]}\n"
        msg += f"🛑 *Frenos:* Discos: {f[15]} | Past: {f[16]}\n"
        msg += f"💡 *Faros:* {f[17]}\n"
        msg += f"━━━━━━━━━━━━━\n"
        msg += f"⚠️ *Notas:* {f[18]}\n"
        msg += f"📋 *Próx. ITV:* {f[21]}\n"
        msg += f"💰 *TOTAL:* {f[19]}€\n\n_Garaje Pipo - Raul Plaza_"
        
        webbrowser.open(f"https://wa.me/?text={urllib.parse.quote(msg)}")

class MiApp(App):
    datos = {}
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(Pantalla1(name='pag1'))
        sm.add_widget(Pantalla2(name='pag2'))
        sm.add_widget(Pantalla3(name='pag3'))
        sm.add_widget(Pantalla4(name='pag4'))
        sm.add_widget(Pantalla5(name='pag5'))
        sm.add_widget(PantallaHistorial(name='historial'))
        return sm

if __name__ == '__main__':
    MiApp().run()
