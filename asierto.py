import logging

from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.animation import Animation
import random

__version__ = "0.1.5"

# font sizes
TEXT_SIZE = "18sp"
MSG_SIZE = "24sp"
BUTTON_SIZE = "24sp"
TITLE_SIZE = "48sp"
SUB_TITLE_SIZE = "24sp"

class ImageButton(FloatLayout):
    def __init__(self, image, **kwargs):

        bgcolor=kwargs.pop("background_color")
        on_press=kwargs.pop("on_press")
        super(ImageButton, self).__init__(**kwargs)

        # Aggiungi l'immagine
        self.img = image

        # Aggiungi il bottone sovrapposto all'immagine
        self.button = Button(background_color=bgcolor, on_press=on_press,
        size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(self.button)
        self.add_widget(self.img)

    @staticmethod
    def makeImage(type,color):
        image_source = f"imgs/{type}/{color}.png"
        return Image(source=image_source,
                allow_stretch=True, keep_ratio=True, size_hint=(0.9, 0.9),
                pos_hint={'center_x': 0.5, 'center_y': 0.5})

    def update(self, color, image):
        self.img = image
        self.button.background_color = color
        self.clear_widgets()
        self.add_widget(self.button)
        self.add_widget(self.img)

    def showBorder(self, show=True):
        bgcolor = self.button.background_color
        saturated_color = [min(1, c * 1.5) for c in bgcolor[:3]] + [bgcolor[3]]
        if show:
            with self.canvas.after:
                Color(*saturated_color)
                w = 6
                self.border_line = Line(rectangle=(self.x+w/2, self.y+w/2,
                                                   self.width-w/2, self.height-w/2), width=w)
        else:
            self.canvas.after.clear()

class MoreInfo:
    def __init__(self, app: "GameApp"):
        self.app = app
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.subtitle = Label(
            text="¡Asierto! versione " + __version__,
            font_size=SUB_TITLE_SIZE,
            size_hint=(1, 0.1)
        )
        self.changelog = TextInput(
            text=open("resources/changelog.txt").read(),
            font_size=TEXT_SIZE,
            size_hint=(1, 0.4),
            readonly=True,
        )
        self.credits = TextInput(
            text=open("resources/credits.txt").read(),
            font_size=TEXT_SIZE,
            size_hint=(1, 0.4),
            readonly=True,
        )
        self.back_button = Button(
            text="Torna al menu principale",
            font_size=BUTTON_SIZE,
            size_hint=(1, 0.1),
            on_press=lambda instance: self.app.show_welcome_screen()
        )
        self.layout.add_widget(self.subtitle)
        self.layout.add_widget(self.changelog)
        self.layout.add_widget(self.credits)
        self.layout.add_widget(self.back_button)

    def show(self, root: BoxLayout):
        root.clear_widgets()
        root.add_widget(self.layout)


class GameApp(App):
    def build(self):
        Window.clearcolor = (0.5, 0.5, 0.5, 1)
        self.oggetti = ["rosso", "blu", "verde", "giallo", "nero"]
        self.colori = {
            "rosso": [1, 0, 0, 1],
            "blu": [0, 0, 1, 1],
            "verde": [0, 1, 0, 1],
            "giallo": [1, 1, 0, 1],
            "nero": [0.2, 0.2, 0.2, 1]
        }
        self.immagini = {colore: ImageButton.makeImage("pinguini",colore) for colore in self.oggetti}
        self.bottoni = []
        self.reset_game_variables()
        self.root = BoxLayout()
        self.more_info = MoreInfo(self)
        self.show_welcome_screen()
        return self.root

    def reset_game_variables(self):
        self.soluzione = self.oggetti[:]
        random.shuffle(self.soluzione)
        logging.info(f"sequenza misteriosa: {self.soluzione}")
        self.selezione = []
        self.turn_limit = 0
        self.use_enter_button = False
        self.numeri_in_spagnolo = {0: "cero", 1: "uno", 2: "dos", 3: "tres", 4: "cuatro", 5: "cinco"}
        self.click_sound = SoundLoader.load('suoni/click.mp3')
        self.victory_sound = SoundLoader.load('suoni/win.mp3')

    def show_welcome_screen(self):
        layout = BoxLayout(orientation='vertical', spacing=30, padding=30)
        title = Label(
            text="¡Asierto!",
            font_size=TITLE_SIZE,
            size_hint=(1, 0.5),
            bold=True
        )
        subtitle = Label(
            text="Clicca su due colori per scambiarli.\nScopri se hai indovinato la sequenza misteriosa!",
            font_size=MSG_SIZE,
            size_hint=(1, 0.2),
        )
        buttons = BoxLayout(orientation='horizontal', spacing=10, padding=0, size_hint=(1, 0.3))
        start_button = Button(
            text="Inizia",
            font_size=BUTTON_SIZE,
            size_hint=(0.8, 1),
            on_press=lambda instance: self.show_turn_limit_popup()
        )
        info_button = Button(
            text="Info",
            font_size=BUTTON_SIZE,
            size_hint=(0.2, 1),
            on_press=lambda instance: self.more_info.show(self.root)
        )
        buttons.add_widget(start_button)
        buttons.add_widget(info_button)
        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(buttons)
        self.root.clear_widgets()
        self.root.add_widget(layout)

    def show_turn_limit_popup(self):
        layout = BoxLayout(orientation='vertical', spacing=30, padding=30)
        label = Label(text="Quanti turni vuoi giocare?", font_size=SUB_TITLE_SIZE, size_hint=(1, 0.3))
        layout.add_widget(label)

        button_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint=(1, 0.7))
        for limit in [5, 10, 15]:
            btn = Button(
                text=f"{limit} turni",
                size_hint=(1, 1),
                font_size=BUTTON_SIZE
            )
            btn.bind(on_press=lambda instance, limit=limit: self.set_turn_limit(limit))
            button_layout.add_widget(btn)
        layout.add_widget(button_layout)

        self.turn_limit_popup = Popup(
            title="Imposta limite di turni",
            content=layout,
            size_hint=(0.8, 0.5),
            auto_dismiss=False
        )
        self.turn_limit_popup.open()

    def set_turn_limit(self, limit):
        self.turn_limit = limit
        self.turn_limit_popup.dismiss()
        self.show_mode_selection_popup()

    def show_mode_selection_popup(self):
        layout = BoxLayout(orientation='vertical', spacing=30, padding=30)
        label = Label(text="Seleziona Modalità", font_size=SUB_TITLE_SIZE, size_hint=(1, 0.3))
        layout.add_widget(label)

        button_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint=(1, 0.7))
        with_button = Button(
            text="Scambio Multiplo",
            size_hint=(1, 1),
            font_size=BUTTON_SIZE
        )
        with_button.bind(on_press=self.start_with_button)
        without_button = Button(
            text="Scambio Singolo",
            size_hint=(1, 1),
            font_size=BUTTON_SIZE
        )
        without_button.bind(on_press=self.start_without_button)
        button_layout.add_widget(without_button)
        button_layout.add_widget(with_button)
        layout.add_widget(button_layout)

        self.mode_selection_popup = Popup(
            title="Seleziona modalità",
            content=layout,
            size_hint=(0.8, 0.5),
            auto_dismiss=False
        )
        self.mode_selection_popup.open()

    def start_with_button(self, instance):
        self.use_enter_button = True
        self.mode_selection_popup.dismiss()
        self.start_game()

    def start_without_button(self, instance):
        self.use_enter_button = False
        self.mode_selection_popup.dismiss()
        self.start_game()

    def setup_game_window(self):
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.grid = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.6))
        # se ci sono bottoni dal gioco precedente
        if len(self.bottoni) > 0:
            # staccare le immagini dai vecchi bottoni
            # prima di proseguire con il setup
            for btn in self.bottoni:
                btn.clear_widgets()
        self.bottoni = []
        for i, colore in enumerate(self.oggetti):
            btn = ImageButton(
                image=self.immagini[colore],
                background_color=self.colori[colore],
                size_hint=(1, 1),
                on_press=lambda instance, i=i: self.clicca(i)
            )
            self.bottoni.append(btn)
            self.grid.add_widget(btn)
        self.layout.add_widget(self.grid)

        self.feedback_label = Label(
            text=f"Inizia il gioco! Turni rimasti: {self.turn_limit}",
            font_size=MSG_SIZE,
            size_hint=(1, 0.2)
        )
        self.layout.add_widget(self.feedback_label)

        if self.use_enter_button:
            self.enter_btn = Button(
                text="Enter",
                size_hint=(1, 0.2),
                font_size=BUTTON_SIZE,
                on_press=self.misura_asierto
            )
            self.layout.add_widget(self.enter_btn)

    def start_game(self):
        self.setup_game_window()

        self.root.clear_widgets()
        self.root.add_widget(self.layout)

    def clicca(self, indice):
        if self.turn_limit <= 0:
            self.feedback_label.text = "Gioco terminato! Limite di turni raggiunto."
            return

        btn = self.bottoni[indice]

        if len(self.selezione) == 1 and self.selezione[0] == indice:
            # toglere il bordo
            btn.showBorder(False)
            # svuotare la selezione
            self.selezione = []
            # fine gestione
            return

        btn.showBorder(True)

        self.selezione.append(indice)
        if len(self.selezione) == 2:
            boxA, boxB = self.bottoni[self.selezione[0]], self.bottoni[self.selezione[1]]
            # setup animations
            # slow swap then snap to previous position so we can trigger
            # the old complete_swap procedure
            animA = (
                Animation(x=boxB.x,y=boxB.y,duration=0.4) +
                Animation(x=boxA.x,y=boxA.y,duration=0))
            animB = (
                Animation(x=boxA.x,y=boxA.y,duration=0.4) +
                Animation(x=boxB.x,y=boxB.y,duration=0.0))
            animB.on_complete = lambda *x:self.complete_swap()

            # remove the borders
            boxA.showBorder(False)
            boxB.showBorder(False)

            # start animations
            animA.start(boxA)
            animB.start(boxB)

            self.click_sound.play()
            #Clock.schedule_once(lambda dt: self.complete_swap(), 0.4)

    def complete_swap(self):
        self.oggetti[self.selezione[0]], self.oggetti[self.selezione[1]] = self.oggetti[self.selezione[1]], \
        self.oggetti[self.selezione[0]]

        for i in self.selezione:
            btn = self.bottoni[i]
            btn.showBorder(False)

        self.selezione = []
        self.aggiorna_bottoni()

        if not self.use_enter_button:
            self.misura_asierto()

    def misura_asierto(self, instance=None):
        corretti = sum(1 for i in range(len(self.oggetti)) if self.oggetti[i] == self.soluzione[i])
        numero_in_spagnolo = self.numeri_in_spagnolo.get(corretti, str(corretti))
        if corretti == len(self.oggetti):
            self.feedback_label.text = "¡Felicidades! Hai vinto!"
            if self.victory_sound:
                self.victory_sound.play()
            for bottone in self.bottoni:
                bottone.disabled = True
            self.remove_enter_button()
            self.show_replay_button()
            return
        else:
            self.feedback_label.text = f"{numero_in_spagnolo} asierto. Turni rimasti: {self.turn_limit - 1}"

        if self.turn_limit > 0:
            self.turn_limit -= 1
        if self.turn_limit <= 0:
            self.feedback_label.text = "Gioco terminato! Limite di turni raggiunto."
            # disabilitiamo i bottoni quando il gioco finisce
            for bottone in self.bottoni:
                bottone.disabled = True
            self.remove_enter_button()
            self.show_replay_button()

    def remove_enter_button(self):
        if self.use_enter_button and hasattr(self, 'enter_btn'):
            self.layout.remove_widget(self.enter_btn)

    def show_replay_button(self):
        replay_btn = Button(
            text="Replay",
            size_hint=(1, 0.2),
            font_size=BUTTON_SIZE,
            on_press=self.restart_game
        )
        self.layout.add_widget(replay_btn)

    def restart_game(self, instance):
        self.reset_game_variables()
        self.root.clear_widgets()
        self.show_turn_limit_popup()

    def aggiorna_bottoni(self):
        # smontare le immagini dai bottoni precedenti
        for i, bottone in enumerate(self.bottoni):
            bottone.clear_widgets()
        # aggiornare colore e immagine nei bottoni
        for i, bottone in enumerate(self.bottoni):
            bottone.update(
                color=self.colori[self.oggetti[i]],
                image=self.immagini[self.oggetti[i]]
            )


if __name__ == "__main__":
    GameApp().run()
