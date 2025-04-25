from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
import random

class GameApp(App):
    def build(self):
        # Set the background color to gray
        Window.clearcolor = (0.5, 0.5, 0.5, 1)  # RGBA format

        # Load sounds
        self.click_sound = SoundLoader.load('suoni/click.mp3')  # Replace with your sound file
        self.win_sound = SoundLoader.load('suoni/win.mp3')      # Replace with your sound file

        self.oggetti = ["rosso", "blu", "verde", "giallo", "nero"]
        self.colori = {"rosso": [1, 0, 0, 1], "blu": [0, 0, 1, 1], "verde": [0, 1, 0, 1], "giallo": [1, 1, 0, 1], "nero": [0, 0, 0, 1]}
        self.soluzione = self.oggetti[:]
        random.shuffle(self.soluzione)
        self.selezione = []

        # Main layout
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Grid for buttons
        self.grid = GridLayout(cols=len(self.oggetti), spacing=10, size_hint=(1, 0.6))
        self.bottoni = []
        for i, colore in enumerate(self.oggetti):
            btn = Button(background_color=self.colori[colore], on_press=lambda instance, i=i: self.clicca(i))
            self.bottoni.append(btn)
            self.grid.add_widget(btn)
        self.layout.add_widget(self.grid)

        # Feedback label
        self.feedback_label = Label(text="Inizia il gioco!", font_size=20, size_hint=(1, 0.2))
        self.layout.add_widget(self.feedback_label)

        # Replay button
        replay_btn = Button(text="Replay", size_hint=(1, 0.2), on_press=self.reset_game)
        self.layout.add_widget(replay_btn)

        # Bind keyboard events
        Window.bind(on_key_down=self.on_key_down)

        return self.layout

    def clicca(self, indice):


        self.selezione.append(indice)
        if len(self.selezione) == 2:  # Fixed comparison
            # Swap objects
            self.oggetti[self.selezione[0]], self.oggetti[self.selezione[1]] = self.oggetti[self.selezione[1]], self.oggetti[self.selezione[0]]

            # Play click sound
            if self.click_sound:
                self.click_sound.play()

            self.aggiorna_bottoni()
            self.verifica_vittoria()
            self.selezione = []

    def aggiorna_bottoni(self):
        for i, bottone in enumerate(self.bottoni):
            bottone.background_color = self.colori[self.oggetti[i]]

    def verifica_vittoria(self):
        corretti = sum(1 for i in range(len(self.oggetti)) if self.oggetti[i] == self.soluzione[i])
        if corretti == len(self.oggetti):
            self.feedback_label.text = "¡Felicidades! Hai vinto!"
            for bottone in self.bottoni:
                bottone.disabled = True

            # Play win sound
            if self.win_sound:
                self.win_sound.play()
        else:
            self.feedback_label.text = f"{corretti} asierto."

    def reset_game(self, instance):
        random.shuffle(self.oggetti)
        self.soluzione = self.oggetti[:]
        random.shuffle(self.soluzione)
        self.selezione = []
        self.aggiorna_bottoni()
        self.feedback_label.text = "Inizia il gioco!"
        for bottone in self.bottoni:
            bottone.disabled = False

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        if codepoint is not None and codepoint.isdigit():
            indice = int(codepoint) - 1
            if 0 <= indice < len(self.oggetti):
                self.clicca(indice)

if __name__ == "__main__":
    GameApp().run()