# -*- coding: utf-8 -*-
"""EXAMEN ANRE - versiunea pentru Android (Kivy)."""
import json, os, random

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition


def rgb(h, a=1.0):
    h = h.lstrip('#')
    return (int(h[0:2], 16) / 255., int(h[2:4], 16) / 255., int(h[4:6], 16) / 255., a)


FUNDAL   = rgb('ffffff')
PANOU    = rgb('f2f4f7')
TEXT     = rgb('1f2933')
SLAB     = rgb('8b95a1')
ALBASTRU = rgb('2f7ec4')
VERDE    = rgb('159c3c')
VERDE_I  = rgb('0d7a2d')
ROSU     = rgb('d32020')

Window.clearcolor = FUNDAL

AICI = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(AICI, 'intrebari.json'), encoding='utf-8') as f:
    BANCA = json.load(f)['seturi']


def eticheta(text, marime, culoare=TEXT, bold=False, aliniere='left'):
    l = Label(text=text, font_size=marime, bold=bold, color=culoare,
              size_hint_y=None, halign=aliniere, valign='top', markup=False)
    l.bind(width=lambda i, w: setattr(i, 'text_size', (w, None)))
    l.bind(texture_size=lambda i, ts: setattr(i, 'height', ts[1] + dp(6)))
    return l


class EcranMeniu(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        c = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(12))
        c.add_widget(Label(text='EXAMEN ANRE', bold=True, font_size=dp(27),
                           color=TEXT, size_hint_y=None, height=dp(110)))

        self.sp_set = Spinner(text='Alege setul...', values=[s['nume'] for s in BANCA],
                              size_hint_y=None, height=dp(56), font_size=dp(15),
                              background_normal='', background_color=PANOU, color=TEXT)
        self.sp_set.bind(text=self._schimbat)
        c.add_widget(self.sp_set)

        self.sp_lot = Spinner(text='Alege lotul...', values=[],
                              size_hint_y=None, height=dp(56), font_size=dp(15),
                              background_normal='', background_color=PANOU, color=TEXT)
        c.add_widget(self.sp_lot)

        r = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        self.cb = CheckBox(size_hint_x=None, width=dp(44), color=TEXT)
        r.add_widget(self.cb)
        e = eticheta('Amesteca lotul', dp(15))
        e.valign = 'middle'
        r.add_widget(e)
        c.add_widget(r)

        b = Button(text='START TEST', size_hint_y=None, height=dp(62), bold=True,
                   font_size=dp(18), background_normal='', background_color=VERDE)
        b.bind(on_release=self.start)
        c.add_widget(b)

        self.msg = eticheta('', dp(13), ROSU, aliniere='center')
        c.add_widget(self.msg)
        c.add_widget(Label())
        c.add_widget(eticheta('306 intrebari - numerotarea din PDF-ul original',
                              dp(12), SLAB, aliniere='center'))
        self.add_widget(c)

    def _schimbat(self, _s, val):
        for s in BANCA:
            if s['nume'] == val:
                self.sp_lot.values = [l['nume'] for l in s['loturi']]
                self.sp_lot.text = 'Alege lotul...'

    def start(self, *_):
        s = next((s for s in BANCA if s['nume'] == self.sp_set.text), None)
        if not s:
            self.msg.text = 'Alege intai setul de intrebari.'
            return
        lot = next((l for l in s['loturi'] if l['nume'] == self.sp_lot.text), None)
        if not lot:
            self.msg.text = 'Alege un lot.'
            return
        self.msg.text = ''
        q = list(lot['intrebari'])
        if self.cb.active:
            random.shuffle(q)
        self.manager.get_screen('test').porneste(q, self.cb.active)
        self.manager.current = 'test'


class EcranTest(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        r = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(6))
        self.antet = Label(text='', size_hint_y=None, height=dp(30),
                           font_size=dp(13), color=TEXT)
        r.add_widget(self.antet)
        sv = ScrollView()
        self.corp = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(7))
        self.corp.bind(minimum_height=self.corp.setter('height'))
        sv.add_widget(self.corp)
        r.add_widget(sv)
        self.btn = Button(text='VERIFICA', size_hint_y=None, height=dp(58), bold=True,
                          font_size=dp(17), background_normal='', background_color=VERDE_I)
        self.btn.bind(on_release=self.apasat)
        r.add_widget(self.btn)
        self.add_widget(r)

    def porneste(self, intrebari, amestecat):
        self.intrebari, self.amestecat = intrebari, amestecat
        self.idx, self.scor, self.gresite = 0, 0, []
        self.btn.unbind(on_release=self.reia)
        self.btn.bind(on_release=self.apasat)
        self.arata()

    def _antet(self):
        q = self.intrebari[self.idx]
        self.antet.text = ('Intrebarea %d/%d   |   Scor: %d   |   nr. %d din PDF'
                           % (self.idx + 1, len(self.intrebari), self.scor, q['nr']))

    def arata(self):
        self.verificat = False
        self.corp.clear_widgets()
        q = self.intrebari[self.idx]
        self._antet()
        self.corp.add_widget(eticheta(q['enunt'], dp(16), TEXT, bold=True))
        n = sum(1 for o in q['optiuni'] if o['c'])
        self.corp.add_widget(eticheta(
            'Un singur raspuns corect' if n == 1
            else '%d raspunsuri corecte - bifeaza-le pe toate' % n, dp(12), ALBASTRU))

        self.butoane = []
        optiuni = list(q['optiuni'])
        if self.amestecat:
            random.shuffle(optiuni)
        for o in optiuni:
            b = Button(text=o['t'], size_hint_y=None, background_normal='',
                       background_color=ALBASTRU, font_size=dp(14),
                       halign='left', valign='middle')
            b.bind(width=lambda i, w: setattr(i, 'text_size', (w - dp(28), None)))
            b.bind(texture_size=lambda i, ts: setattr(i, 'height', max(dp(50), ts[1] + dp(24))))
            b.optiune, b.eticheta_txt, b.ales = o, o['t'], False
            b.bind(on_release=self.comuta)
            self.butoane.append(b)
            self.corp.add_widget(b)

        self.verdict = eticheta('', dp(19), ROSU, bold=True)
        self.corp.add_widget(self.verdict)
        self.explic = eticheta('', dp(13), TEXT)
        self.corp.add_widget(self.explic)
        self.btn.text = 'VERIFICA'
        self.btn.background_color = VERDE_I

    def comuta(self, b):
        if self.verificat:
            return
        b.ales = not b.ales
        b.text = ('\u25cf  ' + b.eticheta_txt) if b.ales else b.eticheta_txt
        b.bold = b.ales

    def apasat(self, *_):
        if not self.verificat:
            self.verifica()
        else:
            self.idx += 1
            self.arata() if self.idx < len(self.intrebari) else self.final()

    def verifica(self):
        self.verificat = True
        q = self.intrebari[self.idx]
        alese = set(b.optiune['l'] for b in self.butoane if b.ales)
        corecte = set(o['l'] for o in q['optiuni'] if o['c'])

        for b in self.butoane:
            if b.optiune['c']:
                b.background_color = VERDE
                b.text = '\u2714  ' + b.eticheta_txt
                b.bold = True
            elif b.ales:
                b.background_color = ROSU
                b.text = '\u2718  ' + b.eticheta_txt
                b.bold = True
            else:
                b.background_color = ALBASTRU
                b.text = b.eticheta_txt
                b.bold = False

        corect = (alese == corecte)
        if corect:
            self.scor += 1
        else:
            self.gresite.append(q)
        self.verdict.text = 'CORECT!' if corect else 'GRESIT!'
        self.verdict.color = VERDE if corect else ROSU

        linii = []
        if not corect:
            lit = sorted(corecte)
            linii.append('Raspunsul corect: varianta %s.' % lit[0] if len(lit) == 1
                         else 'Raspunsurile corecte: variantele %s si %s.'
                              % (', '.join(lit[:-1]), lit[-1]))
        if q.get('nota'):
            linii.append(q['nota'])
        if q.get('avertisment'):
            linii.append('Atentie: ' + q['avertisment'] + '.')
        self.explic.text = '\n\n'.join(linii)

        self._antet()
        self.btn.text = 'URMATOAREA >' if self.idx + 1 < len(self.intrebari) else 'REZULTAT'
        self.btn.background_color = VERDE

    def final(self):
        n = len(self.intrebari)
        proc = 100.0 * self.scor / n if n else 0
        self.corp.clear_widgets()
        self.antet.text = 'Rezultat final'
        self.corp.add_widget(eticheta('%d din %d  (%.0f%%)' % (self.scor, n, proc),
                                      dp(25), VERDE if proc >= 70 else ROSU,
                                      bold=True, aliniere='center'))
        if self.gresite:
            self.corp.add_widget(eticheta('Intrebari gresite (numerele din PDF):',
                                          dp(14), TEXT, aliniere='center'))
            self.corp.add_widget(eticheta(', '.join(str(x['nr']) for x in self.gresite),
                                          dp(14), ROSU, aliniere='center'))
        else:
            self.corp.add_widget(eticheta('Niciun raspuns gresit.', dp(16), VERDE,
                                          aliniere='center'))
        b = Button(text='INAPOI LA MENIU', size_hint_y=None, height=dp(54),
                   background_normal='', background_color=PANOU, color=TEXT, font_size=dp(15))
        b.bind(on_release=lambda *_: setattr(self.manager, 'current', 'meniu'))
        self.corp.add_widget(b)
        self.btn.text = 'REIA ACELASI LOT'
        self.btn.background_color = VERDE_I
        self.btn.unbind(on_release=self.apasat)
        self.btn.bind(on_release=self.reia)

    def reia(self, *_):
        self.porneste(self.intrebari, self.amestecat)


class ExamenANRE(App):
    title = 'Examen ANRE'

    def build(self):
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(EcranMeniu(name='meniu'))
        sm.add_widget(EcranTest(name='test'))
        return sm


if __name__ == '__main__':
    ExamenANRE().run()
