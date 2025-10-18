from kivy.storage.jsonstore import JsonStore
# font sizes
TEXT_SIZE = "18sp"
MSG_SIZE = "24sp"
BUTTON_SIZE = "24sp"
TITLE_SIZE = "48sp"
MID_TITLE_SIZE = "32sp"
SUB_TITLE_SIZE = "24sp"

store = JsonStore('game.json')
system = JsonStore('system.json')

TYPES = ["Pinguini", "Papere", "Orsi", "Zebre"]
COLORS = ["rosso", "blu", "verde", "giallo", "nero"]
