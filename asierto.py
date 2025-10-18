import logging

from threading import Thread

from kivy.config import Config

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.carousel import Carousel
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.settings import SettingsWithSidebar
from kivy.input.providers.mouse import MouseMotionEvent
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.clock import Clock, mainthread
from kivy.graphics import Color, Line
from kivy.animation import Animation
from kivy.storage.jsonstore import JsonStore
import random
import os, json, shutil
import uuid
import requests

__version__ = "0.1.11"

import globals as G
from manifest import Manifest
from settingOptionsScroll import SettingOptionsScroll

from kivy.core.text import LabelBase
LabelBase.register(name='fa',
                   fn_regular='fonts/Font Awesome 7 Free-Solid-900.otf')

def remove_widget(widget: Widget) -> bool:
    """remove widget from its parent if any"""
    if widget.parent:
        widget.parent.remove_widget(widget)
        return True
    return False

class ImageButton(FloatLayout):
    def __init__(self, image, **kwargs):

        bgcolor=kwargs.pop("background_color")
        on_press=kwargs.pop("on_press")
        super(ImageButton, self).__init__(**kwargs)

        # Aggiungi l'immagine
        self.img = image

        # Aggiungi il bottone sotto l'immagine
        self.button = Button(background_color=bgcolor, on_press=on_press,
                             size_hint=(1, 1),
                             pos_hint={'center_x': 0.5, 'center_y': 0.5})

        self.target = Button(size_hint=(1,0.1),
                             pos_hint={'center_x': 0.5, 'center_y': 0.05})
        self.target.background_disabled_normal = self.target.background_normal
        self.target.background_disabled_down = self.target.background_normal
        self.target.disabled=True
        self.add_widget(self.button)
        self.add_widget(self.img)

    @staticmethod
    def makeImage(type,color):
        image_source = f"imgs/skin/{type}/{color}.png"
        return Image(source=image_source,
                allow_stretch=True, keep_ratio=True, size_hint=(0.9, 0.9),
                pos_hint={'center_x': 0.5, 'center_y': 0.5})

    def update(self, color, image):
        self.img = image
        self.button.background_color = color
        self.clear_widgets()
        self.add_widget(self.button)
        self.add_widget(self.img)

    def disconnectImage(self):
        remove_widget(self.img)

    def enable(self):
        self.disabled = False
        remove_widget(self.target)

    def disable(self):
        self.disabled = True

    def showTarget(self,color):
        saturated_color = [min(1, c * 1.5) for c in color[:3]] + [color[3]]
        self.target.background_color = color
        self.add_widget(self.target)

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

class ManifestManager(FloatLayout):
    def __init__(self,app,manifest,**kwargs):
        super(ManifestManager,self).__init__(**kwargs)
        self.app = app
        self.manifest = manifest

    def show(self, root: BoxLayout=None):
        try:
            self.manifest.updateManifest()
        except Exception as e:
            logging.warning("Manifest issue: "+ str(e))
        if self.manifest.mustUpdate() == 0:
                self.app.show_welcome_screen()
                return
        self.showMe()
        Thread(target=self.updateManfest).start()

    def showMe(self):
        root = self.app.root
        root.clear_widgets()
        root.add_widget(self)

    def updateManfest(self):
        try:
            self.manifest.updateSkins(self.update)
        except Exception as e:
            logging.warning("Manifest issue: "+ str(e))


    @mainthread
    def update(self, action, skin):
        if action == "downloading":
            self.ids.message.text = f"Download... {skin.capitalize()}"
            return
        current = list(self.manifest.manifest["skins"]).index(skin) + 1
        total = len(self.manifest.manifest["skins"])
        value = current * 100 / total
        anim = Animation(value=value, duration=2)
        anim.start(self.ids.progress_bar)
        if current == total:
            self.app.show_welcome_screen()

class MoreInfo(BoxLayout):

    def __init__(self, app, **kwargs):
        super(MoreInfo,self).__init__(**kwargs)
        self.app = app
        changelog = open("resources/changelog.txt",encoding="utf-8").read()
        credits =open("resources/credits.txt",encoding="utf-8").read()
        print (self.ids)

        self.ids["version"].text = f"¡Asierto! versione {__version__}"
        self.ids["changelog"].text = changelog + "\n\nCREDITS:\n" + credits

    def on_back(self):
        if self.app:
            self.app.show_welcome_screen()


    def show(self, root: BoxLayout):
        root.clear_widgets()
        root.add_widget(self)

class VideoTutorialScreen():
    def __init__(self, app):
        self.app = app
        self.screen =  FloatLayout()

        self.video = VideoPlayer(source="videos/Asierto Tutorial.mp4")
        self.video.state = "stop"
        self.video.options = {"eos":"stop"}
        self.video.allow_stretch = True
        self.screen.add_widget(self.video)

        self.prev =  Button(
            font_name="fa",
            font_size= 64,
            background_normal="",
            background_down="",
            color=(0.6,0.6,0.6,1),
            background_color=(0,0,0,0),
            text="\uf359",
            size_hint=(0.1, 0.15),  # dimensione relativa
            pos_hint={'right': 1, 'top': 1},  # allineato a destra in alto
            on_press=self.start_game,
        )
        controlLayout = self.video.children[0]
        controlBar = list(reversed(controlLayout.children))
        controlBar.insert(0,self.prev)
        controlBar.insert(1,Widget(width=5,size_hint_x=None))

        controlLayout.clear_widgets()
        for widget in controlBar:
                controlLayout.add_widget(widget)


    def start_game(self, *args):
        # Logica per iniziare il gioco
        self.video.position = 0
        self.video.play = False
        Window.clearcolor = (0.5, 0.5, 0.5, 1)
        self.app.show_welcome_screen()
        pass

    def show(self, root: BoxLayout):
        Window.clearcolor = (0,0,0,1)
        root.clear_widgets()
        self.video.play = True
        root.add_widget(self.screen)

class GameScreen:
    def __init__(self, app,type_=None):
        self.app = app
        self.oggetti = ["rosso", "blu", "verde", "giallo", "nero"]
        self.colori = {
            "rosso": [1, 0, 0, 1],
            "blu": [0, 0, 1, 1],
            "verde": [0, 1, 0, 1],
            "giallo": [1, 1, 0, 1],
            "nero": [0.2, 0.2, 0.2, 1]
        }

        self.immagini = self.make_images()
        self.numeri_in_spagnolo = {0: "cero", 1: "uno", 2: "dos", 3: "tres", 4: "cuatro", 5: "cinco"}
        self.click_sound = SoundLoader.load('suoni/click.mp3')
        self.victory_sound = SoundLoader.load('suoni/win.mp3')
        self.bottoni = []
        self.use_enter_button = False
        self.reset_game_variables()
        self.setup_game_window()

    def make_images(self,update_buttons=False):
        skin  = self.app.config.get("Game","skin")
        if skin == None or skin not in self.app.manifest.types:
            skin = random.choice(self.app.manifest.types)

        if not update_buttons:
            return {colore: ImageButton.makeImage(skin.lower(), colore) for colore in self.oggetti}
        self.immagini = {colore: ImageButton.makeImage(skin.lower(), colore) for colore in self.oggetti}
        self.aggiorna_bottoni()
        self.current_skin = skin

    def reset_game_variables(self):
        self.soluzione = self.oggetti[:]
        random.shuffle(self.soluzione)
        logging.info(f"sequenza misteriosa: {self.soluzione}")
        self.selezione = []
        self.turn_limit = 0

    def setup_game_window(self):
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.grid = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.6))
        self.footer = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.2))
        self.bottoni =[]
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
            font_size=G.MSG_SIZE,
            size_hint=(1, 0.2)
        )
        self.layout.add_widget(self.feedback_label)
        self.layout.add_widget(self.footer)

        self.enter_btn = Button(
            text="Enter",
            size_hint=(1, 1),
            font_size=G.BUTTON_SIZE,
            on_press=self.misura_asierto
        )
        self.replay_btn = Button(
            text="Menu principale",
            size_hint=(1, 1),
            font_size=G.BUTTON_SIZE,
            on_press=self.app.restart_game
        )
        self.footer.add_widget(self.replay_btn)

    def clicca(self, indice):
        if self.turn_limit <= 0:
            # self.feedback_label.text = "Gioco terminato! Limite di turni raggiunto."
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
        if not self.selezione:
            # selezione was resetted before the end of the animation: abort.
            return
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
            self.feedback_label.text = f"¡Felicidades! Hai vinto! (Turni rimasti: {self.turn_limit - 1})"
            if self.victory_sound:
                self.victory_sound.play()
            self.app.user.storeGame(result="win",startTime= self.start_time, totalTurns=self.total_turns, turnLimit=self.turn_limit,
                                    mode=self.current_mode, skin=self.current_skin)
            self.replay()
            return
        else:
            self.feedback_label.text = f"{numero_in_spagnolo} asierto. Turni rimasti: {self.turn_limit - 1}"

        if self.turn_limit > 0:
            self.turn_limit -= 1
        if self.turn_limit <= 0:
            self.feedback_label.text = "Gioco terminato! Limite di turni raggiunto."
            self.app.user.storeGame(result="lost",startTime=self.start_time, totalTurns=self.total_turns, turnLimit=self.turn_limit,
                                    mode=self.current_mode, skin=self.current_skin)
            self.replay()
            return

    def aggiorna_bottoni(self):
        # smontare le immagini dai bottoni precedenti
        for btn in self.bottoni:
            btn.disconnectImage()
        # aggiornare colore e immagine nei bottoni
        for bottone,colore in zip(self.bottoni,self.oggetti):
            bottone.update(
                color=self.colori[colore],
                image=self.immagini[colore]
                )

    def reset(self,include_images=False):
        # disconnect enter
        # remove_widget(self.enter_btn)
        self.enter_btn.disabled = True
        # disconnect replay
        # remove_widget(self.replay_btn)
        # reset feedback Label
        self.feedback_label.text = f"Inizia il gioco! Turni rimasti: {self.turn_limit}"
        # enable buttons
        for bottone in self.bottoni:
            bottone.enable()
            bottone.showBorder(False)
        # disconnect images
        if include_images:
            for btn in self.bottoni:
                btn.disconnectImage()


    def show_enter(self,show=True):
        if show:
            remove_widget(self.enter_btn)
            self.footer.add_widget(self.enter_btn)
            self.enter_btn.disabled = False
        else:
            remove_widget(self.enter_btn)

    def start_with_button(self):
        self.make_images(update_buttons=True)
        self.use_enter_button = True
        self.reset(include_images=False)
        self.show_enter()
        self.enter_btn.size_hint[0] = 0.7
        self.replay_btn.size_hint[0] = 0.3
        self.show()

    def start_without_button(self):
        self.make_images(update_buttons=True)
        self.use_enter_button = False
        self.reset(include_images=False)
        self.show_enter(False)
        self.enter_btn.size_hint[0] = 1
        self.replay_btn.size_hint[0] = 1
        self.show()

    def set_turn_limit(self,limit):
        self.turn_limit = limit
        self.total_turns = limit
        self.start_time = str(datetime.datetime.now())

    def replay(self):
        for bottone,colore in zip(self.bottoni,self.soluzione):
            bottone.disable()
            bottone.showTarget(self.colori[colore])
        # remove_widget(self.enter_btn)
        self.enter_btn.disabled = True
        #self.layout.add_widget(self.replay_btn)

    def show(self, root: BoxLayout=None):
        if root is None:
            root= self.app.root
        root.clear_widgets()
        root.add_widget(self.layout)

json = '''
[{
   "type": "options",
   "title": "Turni",
   "desc": "Quanti turni vuoi giocare",
   "section": "Game",
   "key": "turni",
   "options": ["5", "10", "15"] },
 {
  "type": "options",
  "title": "Modalità",
  "desc": "Seleziona modalità",
  "section": "Game",
  "key": "scambio",
  "options": ["Scambio Singolo", "Scambio Multiplo"]
  },
{
 "type": "options",
 "title": "Skin",
 "desc": "Seleziona la skin preferita",
 "section": "Game",
 "key": "skin",
 "options": ["casuale","orsi","papere","pinguini","zebre"]
 }
]
'''
import datetime
from kivy.network.urlrequest import UrlRequest
class User:
    def __init__(self,app):
        self.app = app
        self.gamesStore = JsonStore('games.json')
        if not G.store.exists('user'):
            G.store.put("user",id=str(uuid.uuid4()))
        self.id = G.store.get("user")["id"]

    def storeGame(self,**data):
        import json
        now = str(datetime.datetime.now())
        utcnow = str(datetime.datetime.utcnow())
        gameid = str(uuid.uuid4())
        payload = dict(id=gameid,time=now,utcTime=utcnow,user=self.id,**data)
        self.gamesStore.put(gameid,**payload)

        headers = {'Content-type': 'application/json',
                  'Accept': 'application/json'}
        url = G.system.get("analytics")["url"]
        req = UrlRequest(url,
                req_headers=headers,
                req_body=json.dumps(payload).encode())



class GameApp(App):
    G = G
    def build(self):
        Window.clearcolor = (0.5, 0.5, 0.5, 1)
        self.manifest = Manifest()
        self.game = GameScreen(app=self)
        self.root = BoxLayout()
        self.more_info = MoreInfo(app=self)
        self.settings_cls = SettingsWithSidebar
        self.tutorial = VideoTutorialScreen(app=self)
        self.manifestManager = ManifestManager(self,self.manifest)
        self.use_kivy_settings = False
        self.manifestManager.show(self.root)
        self.user = User(app=self)


    def show_welcome_screen(self):
        float = FloatLayout()
        layout = BoxLayout(orientation='vertical', spacing=30, padding=30)

        exit =  Button(
            font_name="fa",
            font_size= G.MID_TITLE_SIZE,
            background_normal="",
            background_down="",
            color=(0.4,0.4,0.4,1),
            background_color=(0,0,0,0),
            text="\uf057",
            size_hint=(0.1, 0.15),  # dimensione relativa
            pos_hint={'right': 1, 'top': 1},  # allineato a destra in alto
            on_press=lambda *a,**k:self.stop(),
        )

        title = Label(
            text="¡Asierto!",
            font_size=G.TITLE_SIZE,
            size_hint=(1, 0.5),
            bold=True
        )
        title = Image(source="imgs/Asierto.png",
                allow_stretch=True, keep_ratio=True, size_hint=(0.5, 0.5),
                pos_hint={'center_x': 0.5, 'center_y': 0.5})
        subtitle = Label(
            text=self.manifest.message,
            font_size=G.MSG_SIZE,
            size_hint=(1, 0.2),
        )
        buttons = BoxLayout(orientation='horizontal', spacing=10, padding=0, size_hint=(1, 0.3))
        start_button = Button(
            text="Inizia",
            font_size=G.BUTTON_SIZE,
            size_hint=(0.4, 1),
            #on_press=lambda instance: self.show_turn_limit_popup()
            on_press= lambda instance: self.start_game()
        )
        tutorial_button =Button(
            text="Tutorial",
            font_size=G.BUTTON_SIZE,
            size_hint=(0.2, 1),
            on_press=lambda instance: self.tutorial.show(self.root)
        )
        info_button = Button(
            text="Info",
            font_size=G.BUTTON_SIZE,
            size_hint=(0.2, 1),
            on_press=lambda instance: self.more_info.show(self.root)
        )
        settings_button = Button(
            text="Opzioni",
            font_size=G.BUTTON_SIZE,
            size_hint=(0.2, 1),
            on_press=lambda instance: self.open_settings()
        )
        buttons.add_widget(start_button)
        buttons.add_widget(tutorial_button)
        buttons.add_widget(info_button)
        buttons.add_widget(settings_button)
        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(buttons)
        float.add_widget(layout)
        float.add_widget(exit)
        self.root.clear_widgets()
        self.root.add_widget(float)

    def start_game(self):
        limit = int(self.config.get("Game","turni"))
        self.game.set_turn_limit(limit)
        with_button = self.config.get("Game","scambio") != "Scambio Singolo"
        self.game.current_mode = self.config.get("Game","scambio")
        if with_button:
            self.game.start_with_button()
        else:
            self.game.start_without_button()



    def show_turn_limit_popup(self):
        layout = BoxLayout(orientation='vertical', spacing=30, padding=30)
        label = Label(text="Per quanti turni vuoi giocare?", font_size=G.TITLE_SIZE, size_hint=(1, 0.3))
        layout.add_widget(label)

        def set_turn_limit(limit):
            self.game.set_turn_limit(limit)
            self.turn_limit_popup.dismiss()
            self.show_mode_selection_popup()

        button_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint=(1, 0.7))
        for limit in [5, 10, 15]:
            btn = Button(
                text=f"{limit} turni",
                size_hint=(1, 1),
                font_size=G.BUTTON_SIZE
            )
            btn.bind(on_press=lambda instance, limit=limit: set_turn_limit(limit))
            button_layout.add_widget(btn)
        layout.add_widget(button_layout)

        self.turn_limit_popup = Popup(
            title="Imposta limite di turni",
            content=layout,
            size_hint=(0.8, 0.5),
            auto_dismiss=False
        )
        self.turn_limit_popup.open()

    def show_mode_selection_popup(self):
        layout = BoxLayout(orientation='vertical', spacing=30, padding=30)
        label = Label(text="Seleziona Modalità", font_size=G.TITLE_SIZE, size_hint=(1, 0.3))
        layout.add_widget(label)

        def start_game(with_button):
            def cb(instance):
                if with_button:
                    self.game.start_with_button()
                else:
                    self.game.start_without_button()
                self.mode_selection_popup.dismiss()
            return cb

        button_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint=(1, 0.7))
        with_button = Button(
            text="Scambio Multiplo",
            size_hint=(1, 1),
            font_size=G.BUTTON_SIZE
        )
        with_button.bind(on_press=start_game(with_button=True))
        without_button = Button(
            text="Scambio Singolo",
            size_hint=(1, 1),
            font_size=G.BUTTON_SIZE
        )
        without_button.bind(on_press=start_game(with_button=False))
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

    def restart_game(self, instance):
        self.game.reset_game_variables()
        self.root.clear_widgets()
        # self.show_turn_limit_popup()
        self.show_welcome_screen()

    def build_config(self, config):
       config.setdefaults(
         'Game', {'turni': "15", 'scambio': "Scambio Singolo","skin": "Casuale"}
       )
       self.config = config

    def build_settings(self, settings):
       from json import loads,dumps
       data = loads(json)
       settings.register_type('options', SettingOptionsScroll)
       skin = [i for i in data if i["title"]=="Skin"][0]
       skin["options"] = ["Casuale"] + self.manifest.types
       data = dumps(data)
       skin = self.config.get("Game","skin")
       if skin not in self.manifest.types:
           self.config.set("Game","skin","Casuale")
       logging.info("skin: "+ str(self.config.get("Game","skin")))
       settings.add_json_panel('Opzioni', self.config, data=data)


def fullscreen_fix(cls):
    # Save original build if exists
    original_func = getattr(cls, 'build', None)
    original_resume = getattr(cls, 'on_resume',None)

    def force_redraw(self, dt, attempt_num):
        if self.root:
            # Force canvas update
            self.root.canvas.ask_update()
            Window.update_viewport()

            logging.warning(f"[AndroidFullscreenFix] Forced redraw #{attempt_num} at {dt:.2f}s")

    def schedule_all_redraws(self, dt):
        logging.warning("[AndroidFullscreenFix] Now scheduling all redraws...")

        # Now schedule the actual redraws
        for i in range(2):
            Clock.schedule_once(
                lambda dt, num=i: force_redraw(self, dt, num+1),
                0.5 * i
            )

    def new_resume(self):
        # Call original on_resume
        results = original_resume(self) if original_resume else True

        logging.warning("[AndroidFullscreenFix] Resuming, calling redraw")
        Clock.schedule_once(lambda dt: schedule_all_redraws(self, dt), 0)
        return results

    def new_func(self):
        # Call original build
        root = original_func(self) if original_func else None

        logging.warning("[AndroidFullscreenFix] Build completed, scheduling redraw scheduler...")

        # Schedule the scheduler (will run in main loop)
        Clock.schedule_once(lambda dt: schedule_all_redraws(self, dt), 0)

        return root

    # Replace build method
    cls.build = new_func

    # Add utility methods to class
    cls.force_redraw = force_redraw
    cls.schedule_all_redraws = schedule_all_redraws
    cls.on_resume = new_resume

    return cls


if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        fullscreen_fix(GameApp)().async_run(async_lib='asyncio'))
