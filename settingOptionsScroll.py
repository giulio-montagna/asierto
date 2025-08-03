from kivy.uix.settings import SettingOptions,SettingSpacer,GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.metrics import dp

class SettingOptionsScroll(SettingOptions):
    def _create_popup(self, instance):
        # create the popup
        content = BoxLayout(orientation='vertical', spacing='5dp')
        popup_width = min(0.95 * Window.width, dp(500))
        self.popup = popup = Popup(
            content=content, title=self.title, size_hint=(None, None),
            size=(popup_width, '400dp'))

        # Create a ScrollView
        scroll_view = ScrollView(size_hint=(1, 1), size=(popup_width, '300dp'))

        # Create a GridLayout to hold the options
        options_layout = GridLayout(cols=1, size_hint_y=None, spacing=5 ,padding =5)
        options_layout.bind(minimum_height=options_layout.setter('height'))

        # Add all the options to the GridLayout
        uid = str(self.uid)
        for option in self.options:
            state = 'down' if option == self.value else 'normal'
            btn = ToggleButton(text=option, state=state, group=uid,size_hint_y=None, height=dp(50))
            btn.bind(on_release=self._set_option)
            options_layout.add_widget(btn)

        # Add the GridLayout to the ScrollView
        scroll_view.add_widget(options_layout)

        # Add the ScrollView to the content
        content.add_widget(scroll_view)

        # Finally, add a cancel button to return on the previous panel
        content.add_widget(SettingSpacer())
        btn = Button(text='Cancel', size_hint_y=None, height=dp(50))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)

        # And open the popup!
        popup.open()
