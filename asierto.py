from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
import random


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
        self.reset_game_variables()
        self.root = BoxLayout()
        self.show_welcome_screen()
        return self.root

    def reset_game_variables(self):
        self.soluzione = self.oggetti[:]
        random.shuffle(self.soluzione)
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
            font_size=48,
            size_hint=(1, 0.5),
            bold=True
        )
        subtitle = Label(
            text="un gioco di ..., bello",
            font_size=24,
            size_hint=(1, 0.3)
        )
        start_button = Button(
            text="Inizia",
            font_size=24,
            size_hint=(1, 0.2),
            on_press=lambda instance: self.show_turn_limit_popup()
        )
        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(start_button)
        self.root.clear_widgets()
        self.root.add_widget(layout)

    def show_turn_limit_popup(self):
        layout = BoxLayout(orientation='vertical', spacing=30, padding=30)
        label = Label(text="Quanti turni vuoi giocare?", font_size=28, size_hint=(1, 0.3))
        layout.add_widget(label)

        button_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint=(1, 0.7))
        for limit in [5, 10, 15]:
            btn = Button(
                text=f"{limit} turni",
                size_hint=(1, 1),
                font_size=24
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
        label = Label(text="Vuoi giocare con o senza il tasto Enter?", font_size=28, size_hint=(1, 0.3))
        layout.add_widget(label)

        button_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint=(1, 0.7))
        with_button = Button(
            text="Con tasto Enter",
            size_hint=(1, 1),
            font_size=24
        )
        with_button.bind(on_press=self.start_with_button)
        without_button = Button(
            text="Senza tasto Enter",
            size_hint=(1, 1),
            font_size=24
        )
        without_button.bind(on_press=self.start_without_button)
        button_layout.add_widget(with_button)
        button_layout.add_widget(without_button)
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

    def start_game(self):
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.grid = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.6))
        self.bottoni = []
        for i, colore in enumerate(self.oggetti):
            btn = Button(
                background_color=self.colori[colore],
                size_hint=(1, 1),
                on_press=lambda instance, i=i: self.clicca(i)
            )
            self.bottoni.append(btn)
            self.grid.add_widget(btn)
        self.layout.add_widget(self.grid)

        self.feedback_label = Label(
            text=f"Inizia il gioco! Turni rimasti: {self.turn_limit}",
            font_size=28,
            size_hint=(1, 0.2)
        )
        self.layout.add_widget(self.feedback_label)

        if self.use_enter_button:
            self.enter_btn = Button(
                text="Enter",
                size_hint=(1, 0.2),
                on_press=self.misura_asierto
            )
            self.layout.add_widget(self.enter_btn)

        self.root.clear_widgets()
        self.root.add_widget(self.layout)

    def clicca(self, indice):
        if self.turn_limit <= 0:
            self.feedback_label.text = "Gioco terminato! Limite di turni raggiunto."
            return

        if len(self.selezione) == 1 and self.selezione[0] == indice:
            return

        self.selezione.append(indice)
        if len(self.selezione) == 2:
            if self.click_sound:
                self.click_sound.play()
            self.oggetti[self.selezione[0]], self.oggetti[self.selezione[1]] = self.oggetti[self.selezione[1]], \
            self.oggetti[self.selezione[0]]
            self.aggiorna_bottoni()
            self.selezione = []

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
        else:
            self.feedback_label.text = f"{numero_in_spagnolo} asierto. Turni rimasti: {self.turn_limit - 1}"

        if self.turn_limit > 0:
            self.turn_limit -= 1
        if self.turn_limit <= 0:
            self.feedback_label.text = "Gioco terminato! Limite di turni raggiunto."
            self.remove_enter_button()
            self.show_replay_button()

    def remove_enter_button(self):
        if self.use_enter_button and hasattr(self, 'enter_btn'):
            self.layout.remove_widget(self.enter_btn)

    def show_replay_button(self):
        replay_btn = Button(
            text="Replay",
            size_hint=(1, 0.2),
            on_press=self.restart_game
        )
        self.layout.add_widget(replay_btn)

    def restart_game(self, instance):
        self.reset_game_variables()
        self.root.clear_widgets()
        self.show_turn_limit_popup()

    def aggiorna_bottoni(self):
        for i, bottone in enumerate(self.bottoni):
            bottone.background_color = self.colori[self.oggetti[i]]


if __name__ == "__main__":
    GameApp().run()
