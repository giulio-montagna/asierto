import tkinter as tk
import random

# Lista di oggetti con colori
oggetti = ["rosso", "blu", "verde", "giallo", "nero"]
colori = {"rosso": "red", "blu": "blue", "verde": "green", "giallo": "yellow", "nero": "black"}

# Dizionario per numeri in lettere in spagnolo
numeri_in_spagnolo = {0: "cero", 1: "uno", 2: "dos", 3: "tres", 4: "cuatro", 5: "cinco"}

# Creazione di una sequenza casuale come soluzione
soluzione = oggetti[:]
random.shuffle(soluzione)

# Variabili globali
selezione = []
bottoni = []

# Funzione per gestire il clic sui bottoni
def clicca(indice):
    global selezione
    selezione.append(indice)
    if len(selezione) == 2:
        # Scambia gli oggetti
        oggetti[selezione[0]], oggetti[selezione[1]] = oggetti[selezione[1]], oggetti[selezione[0]]
        aggiorna_bottoni()
        verifica_vittoria()
        selezione = []

# Aggiorna i bottoni con i nuovi colori
def aggiorna_bottoni():
    for i, bottone in enumerate(bottoni):
        bottone.config(bg=colori[oggetti[i]])

# Verifica il numero di oggetti nella posizione corretta
def verifica_vittoria():
    corretti = sum(1 for i in range(len(oggetti)) if oggetti[i] == soluzione[i])
    numero_in_lettere = numeri_in_spagnolo[corretti]
    etichetta_feedback.config(text=f"{numero_in_lettere} asierto.")
    if corretti == len(oggetti):
        etichetta_feedback.config(text="¡Felicidades! Hai vinto!")
        for bottone in bottoni:
            bottone.config(state="disabled")

# Creazione della finestra principale
finestra = tk.Tk()
finestra.title("Gioco degli oggetti")

# Creazione dei bottoni per gli oggetti
for i, colore in enumerate(oggetti):
    bottone = tk.Button(finestra, width=15, height=5, bg=colori[colore], command=lambda i=i: clicca(i))
    bottone.grid(row=0, column=i, padx=10, pady=10)
    bottoni.append(bottone)

# Etichetta per il feedback
etichetta_feedback = tk.Label(finestra, text="Inizia il gioco!", font=("Arial", 20))
etichetta_feedback.grid(row=1, column=0, columnspan=len(oggetti), pady=20)

# Avvia il loop principale di tkinter
finestra.mainloop()