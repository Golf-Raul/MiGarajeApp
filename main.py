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
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

Window.clearcolor = (0.95, 0.95, 0.95, 1)

def conectar_bd():
    directorio = App.get_running_app().user_data_dir
    ruta_db = os.path.join(directorio, 'mantenimiento_raul_final.db')
    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS fichas 
                      (id INTEGER PRIMARY KEY, modelo TEXT, matricula TEXT, km_act TEXT,
                       aceite_chk TEXT, aceite_det TEXT, aceite_km TEXT,
                       caja_chk TEXT, caja_det TEXT, caja_km TEXT,
                       f_aire TEXT, f_aceite TEXT, f_polen TEXT, f_comb TEXT, f_anti TEXT,
                       r_del_chk TEXT, r_del_km TEXT, r_tra_chk TEXT, r_tra_km TEXT, frenos TEXT,
                       luces TEXT, agua TEXT, limpias TEXT,
                       averia TEXT, coste TEXT, fecha TEXT)''')
    conn.commit()
    return conn

class Bloque(BoxLayout):
    def __init__(self, titulo, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, spacing=10, padding=20, **kwargs)
        self.bind(minimum_height=self.setter('height'))
        self.add_widget(Label(text=titulo.upper(), size_hint_y=None, height=50, 
                              bold=True, color=(0.1, 0.4, 0.7, 1), font_size=20, halign="left"))

class PantallaBase(Screen):
    def crear_contenedor(self, titulo_pantalla):
        layout_principal = BoxLayout(orientation='vertical')
        cabecera = Label(text=titulo_pantalla, size_hint_y=None, height=90, bold=True, font_size=26, color=(1,1,1,1))
        with cabecera.canvas.before:
            Color(0.1, 0.4, 0.7, 1)
            self.rect = Rectangle(size=cabecera.size, pos=cabecera.pos)
        cabecera.bind(size=self._update_rect, pos=self._update_rect)
        layout_principal.add_widget(cabecera)
        self.scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=25, padding=20)
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        layout_principal.add_widget(self.scroll)
        return layout_principal

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def input_est(self, hint, multi=False, alto=80):
        return TextInput(hint_text=hint, multiline=multi, size_hint_y=None, height=alto, font_size=22, padding=[15, 20])

    def check_est(self, texto):
        box = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
        box.add_widget(Label(text=texto, color=(0.2, 0.2, 0.2, 1), font_size=20))
        cb = CheckBox(color=(0.1, 0.4, 0.7, 1), size_hint_x=None, width=80)
        box.add_widget(cb)
        return box, cb

class PaginaUno(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("1. DATOS VEHÍCULO")
        b1 = Bloque("IDENTIFICACIÓN")
        self.mod = self.input_est("Modelo"); b1.add_widget(self.mod)
        self.mat = self.input_est("Matrícula"); b1.add_widget(self.mat)
        self.km = self.input_est("Km Actuales"); b1.add_widget(self.km)
        self.content.add_widget(b1)
        btn = Button(text="CONTINUAR", size_hint_y=None, height=100, background_color=(0.1, 0.7, 0.3, 1), bold=True, font_size=24)
        btn.bind(on_press=lambda x: self.ir_sig()); self.content.add_widget(btn)
        btn_h = Button(text="VER HISTORIAL", size_hint_y=None, height=80, background_color=(0.5, 0.5, 0.5, 1), font_size=22)
        btn_h.bind(on_press=lambda x: setattr(self.manager, 'current', 'historial')); self.content.add_widget(btn_h)
        self.add_widget(l)
    def ir_sig(self):
        App.get_running_app().datos.update({'mod':self.mod.text, 'mat':self.mat.text, 'km':self.km.text})
        self.manager.current = 'pag2'

class PaginaDos(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("2. MOTOR Y CAJA")
        b_aceite = Bloque("ACEITE MOTOR")
        l1, self.ac = self.check_est("Cambio Aceite Motor"); b_aceite.add_widget(l1)
        self.ad = self.input_est("Densidad/Marca Aceite"); b_aceite.add_widget(self.ad)
        self.ak = self.input_est("Km del cambio"); b_aceite.add_widget(self.ak)
        b_caja = Bloque("CAJA DE CAMBIOS")
        l2, self.cc = self.check_est("Cambio Aceite Caja"); b_caja.add_widget(l2)
        self.cd = self.input_est("Densidad/Marca Valvulina"); b_caja.add_widget(self.cd)
        self.ck = self.input_est("Km del cambio (Caja)"); b_caja.add_widget(self.ck)
        self.content.add_widget(b_aceite); self.content.add_widget(b_caja)
        btn = Button(text="SIGUIENTE", size_hint_y=None, height=100, background_color=(0.1, 0.7, 0.3, 1), font_size=24); btn.bind(on_press=lambda x: self.ir_sig())
        self.content.add_widget(btn); self.add_widget(l)
    def ir_sig(self):
        App.get_running_app().datos.update({'ac':str(self.ac.active),'ad':self.ad.text,'ak':self.ak.text,'cc':str(self.cc.active),'cd':self.cd.text,'ck':self.ck.text})
        self.manager.current = 'pag3'

class PaginaTres(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("3. FILTROS Y MOTOR")
        b_fil = Bloque("FILTROS Y ANTICONGELANTE")
        l1, self.f1 = self.check_est("Aire"); b_fil.add_widget(l1)
        l2, self.f2 = self.check_est("Aceite"); b_fil.add_widget(l2)
        l3, self.f3 = self.check_est("Polen"); b_fil.add_widget(l3)
        l4, self.f4 = self.check_est("Combustible"); b_fil.add_widget(l4)
        l_anti, self.fa = self.check_est("Anticongelante"); b_fil.add_widget(l_anti)
        b_rue = Bloque("RUEDAS Y FRENOS")
        l5, self.rdc = self.check_est("Ruedas Delanteras"); b_rue.add_widget(l5)
        self.rdk = self.input_est("Km Ruedas Del."); b_rue.add_widget(self.rdk)
        l6, self.rtc = self.check_est("Ruedas Traseras"); b_rue.add_widget(l6)
        self.rtk = self.input_est("Km Ruedas Tra."); b_rue.add_widget(self.rtk)
        l7, self.fre = self.check_est("Estado Frenos"); b_rue.add_widget(l7)
        self.content.add_widget(b_fil); self.content.add_widget(b_rue)
        btn = Button(text="SIGUIENTE", size_hint_y=None, height=100, background_color=(0.1, 0.7, 0.3, 1), font_size=24); btn.bind(on_press=lambda x: self.ir_sig())
        self.content.add_widget(btn); self.add_widget(l)
    def ir_sig(self):
        App.get_running_app().datos.update({'f1':str(self.f1.active),'f2':str(self.f2.active),'f3':str(self.f3.active),'f4':str(self.f4.active),'fa':str(self.fa.active),'rdc':str(self.rdc.active),'rdk':self.rdk.text,'rtc':str(self.rtc.active),'rtk':self.rtk.text,'fre':str(self.fre.active)})
        self.manager.current = 'pag4'

class PaginaCuatro(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = self.crear_contenedor("4. EXTERIOR")
        b_ext = Bloque("LÍQUIDOS Y LUCES")
        l1, self.luc = self.check_est("Luces"); b_ext.add_widget(l1)
        l2, self.agu = self.check_est("Nivel Agua"); b_ext.add_widget(l2)
        l3, self.lim = self.check_est("Limpiaparabrisas"); b_ext.add_widget(l3)
        b_fin = Bloque("RESUMEN FINAL")
        self.ave = self.input_est("Observaciones/Averías", multi=True, alto=150); b_fin.add_widget(self.ave)
        self.cos = self.input_est("Coste Total (€)"); b_fin.add_widget(self.cos)
        self.content.add_widget(b_ext); self.content.add_widget(b_fin)
        btn = Button(text="GUARDAR FICHA", size_hint_y=None, height=110, background_color=(0, 0.6, 0.2, 1), bold=True, font_size=26)
        btn.bind(on_press=self.guardar); self.content.add_widget(btn); self.add_widget(l)
    def guardar(self, x):
        conn = conectar_bd(); c = conn.cursor(); d = App.get_running_app().datos
        f_hoy = datetime.now().strftime("%d/%m/%Y")
        c.execute("INSERT INTO fichas (modelo, matricula, km_act, aceite_chk, aceite_det, aceite_km, caja_chk, caja_det, caja_km, f_aire, f_aceite, f_polen, f_comb, f_anti, r_del_chk, r_del_km, r_tra_chk, r_tra_km, frenos, luces, agua, limpias, averia, coste, fecha) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (d['mod'],d['mat'],d['km'],d['ac'],d['ad'],d['ak'],d['cc'],d['cd'],d['ck'],d['f1'],d['f2'],d['f3'],d['f4'],d['fa'],d['rdc'],d['rdk'],d['rtc'],d['rtk'],d['fre'],str(self.luc.active),str(self.agu.active),str(self.lim.active),self.ave.text,self.cos.text,f_hoy))
        conn.commit(); conn.close()
        self.manager.current = 'pag1'

class PantallaHistorial(PantallaBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.l = self.crear_contenedor("HISTORIAL")
        # Aquí la mejora: busca por nombre o matricula
        self.buscador = self.input_est("Busca por Nombre o Matrícula...")
        self.buscador.bind(text=self.cargar_datos)
        self.content.add_widget(self.buscador)
        self.lista_resultados = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15)
        self.lista_resultados.bind(minimum_height=self.lista_resultados.setter('height'))
        self.content.add_widget(self.lista_resultados)
        btn_v = Button(text="VOLVER", size_hint_y=None, height=80, background_color=(0.7, 0.1, 0.1, 1), font_size=22)
        btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'pag1'))
        self.content.add_widget(btn_v)
        self.add_widget(self.l)

    def cargar_datos(self, instance, value):
        self.lista_resultados.clear_widgets()
        if len(value) < 1: return
        conn = conectar_bd(); c = conn.cursor()
        # Mejora en la consulta SQL para buscar en ambos campos
        c.execute("SELECT modelo, matricula, fecha, coste FROM fichas WHERE matricula LIKE ? OR modelo LIKE ?", ('%'+value+'%', '%'+value+'%'))
        for r in c.fetchall():
            btn = Button(text=f"{r[2]} | {r[0]} | {r[1]} | {r[3]}€", size_hint_y=None, height=80, font_size=18)
            self.lista_resultados.add_widget(btn)
        conn.close()

class MiApp(App):
    datos = {}
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(PaginaUno(name='pag1')); sm.add_widget(PaginaDos(name='pag2'))
        sm.add_widget(PaginaTres(name='pag3')); sm.add_widget(PaginaCuatro(name='pag4'))
        sm.add_widget(PantallaHistorial(name='historial'))
        return sm

if __name__ == '__main__':
    MiApp().run()
