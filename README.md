# pyTV

Controlla la tua Google TV / Android TV da terminale o via HTTP, usando il protocollo Android TV Remote v2.
Nessun adattatore, nessun hub: solo la TV sulla rete locale e un piccolo server Python.

## Caratteristiche

- Controllo completo della TV: accensione, volume, media, navigazione, keycode Android.
- Server HTTP locale con endpoint REST semplici.
- Accoppiamento sicuro tramite certificati TLS (certfile.pem / keyfile.pem).
- Comandi "amichevoli" in italiano (accendi, alza, muto, giu, ...).
- Supporto ai keycode Android nativi (KEYCODE_HOME, KEYCODE_MENU, ...).
- Supporto long-press (START_LONG / END_LONG).

## Requisiti

- Python 3.10+
- TV Android / Google TV sulla stessa rete locale

## Primo avvio e accoppiamento

La prima volta che ti connetti, la TV mostra un codice di 6 cifre.
Inseriscilo quando richiesto: verranno generati certfile.pem e keyfile.pem.

## Avvio del server

python3 server.py

Server in ascolto su http://localhost:8787.

| Metodo | Endpoint    | Descrizione                                 |
|--------|-------------|---------------------------------------------|
| POST   | /power      | Spegne/accende (doppio invio per TCL)       |
| POST   | /command    | Invia un comando qualsiasi                  |
| GET    | /commands   | Elenca i comandi amichevoli disponibili     |

## API HTTP

### POST /power

curl -X POST http://localhost:8787/power

### POST /command

Corpo JSON:

{
  "cmd": "home",
  "direction": "SHORT"
}

| Campo       | Tipo   | Obbligatorio | Valori ammessi                       |
|-------------|--------|--------------|--------------------------------------|
| cmd         | string | si           | comando amichevole o keycode Android |
| direction   | string | no           | SHORT, START_LONG, END_LONG          |

curl -X POST http://localhost:8787/command \
  -H "Content-Type: application/json" \
  -d '{"cmd": "home"}'

### GET /commands

curl http://localhost:8787/commands

## Comandi curl completi

### Alimentazione

# Toggle accensione/spegnimento (doppio invio per TCL)
curl -X POST http://localhost:8787/power

# Power tramite endpoint /command (invio singolo)
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "power"}'

# Accendi (alias di power)
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "accendi"}'

# Spegni (alias di power)
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "spegni"}'

### Volume

# Volume su
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "volume_su"}'

# Alza (alias di volume_su)
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "alza"}'

# Volume giu
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "volume_giu"}'

# Abbassa (alias di volume_giu)
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "abbassa"}'

# Muto
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "muto"}'

### Media

# Play
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "play"}'

# Pausa
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "pausa"}'

# Play/Pausa (toggle)
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "play_pausa"}'

# Riprendi (alias di play)
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "riprendi"}'

### Navigazione

# Home
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "home"}'

# Back
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "back"}'

# Indietro (alias di back)
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "indietro"}'

# OK / Conferma
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "ok"}'

# Conferma (alias di ok)
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "conferma"}'

# Su
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "su"}'

# Giu
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "giu"}'

# Sinistra
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "sinistra"}'

# Destra
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "destra"}'

### Keycode diretti

# Menu
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "KEYCODE_MENU"}'

# Impostazioni
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "KEYCODE_SETTINGS"}'

# Info
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "KEYCODE_INFO"}'

# Guida TV
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "KEYCODE_GUIDE"}'

# Canale su
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "KEYCODE_CHANNEL_UP"}'

# Canale giu
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "KEYCODE_CHANNEL_DOWN"}'

# Avanti veloce
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "KEYCODE_MEDIA_FAST_FORWARD"}'

# Indietro veloce
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "KEYCODE_MEDIA_REWIND"}'

# Prossimo
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "KEYCODE_MEDIA_NEXT"}'

# Precedente
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "KEYCODE_MEDIA_PREVIOUS"}'

# Stop
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "KEYCODE_MEDIA_STOP"}'

# Ricerca
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "KEYCODE_SEARCH"}'

# Assistente Google
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "KEYCODE_ASSIST"}'

# Input (cambio sorgente)
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "KEYCODE_TV_INPUT"}'

### Long press

# Long press OK - inizio
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "ok", "direction": "START_LONG"}'

# Long press OK - fine
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "ok", "direction": "END_LONG"}'

# Long press Back - inizio
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "back", "direction": "START_LONG"}'

# Long press Back - fine
curl -X POST http://localhost:8787/command -H "Content-Type: application/json" -d '{"cmd": "back", "direction": "END_LONG"}'

### Diagnostica

# Elenco comandi
curl http://localhost:8787/commands

## Comandi

| Comando       | Alias                | Keycode Android    |
|---------------|----------------------|--------------------|
| power         | accendi, spegni      | POWER              |
| volume_su     | alza                 | VOLUME_UP          |
| volume_giu    | abbassa              | VOLUME_DOWN        |
| muto          |                      | VOLUME_MUTE        |
| play          | riprendi             | MEDIA_PLAY         |
| pausa         |                      | MEDIA_PAUSE        |
| play_pausa    |                      | MEDIA_PLAY_PAUSE   |
| home          |                      | HOME               |
| back          | indietro             | BACK               |
| ok            | conferma             | DPAD_CENTER        |
| su            |                      | DPAD_UP            |
| giu           |                      | DPAD_DOWN          |
| sinistra      |                      | DPAD_LEFT          |
| destra        |                      | DPAD_RIGHT         |

Qualsiasi altro valore in cmd viene trattato come keycode Android: se non inizia con KEYCODE_, il prefisso viene aggiunto automaticamente.

## Risoluzione problemi

### Il server risponde ok ma la TV non fa nulla

Il servizio Android TV Remote Service sulla TV e' in stato anomalo.

1. Impostazioni -> App -> Visualizza tutte le app -> Mostra app di sistema
2. Trova Android TV Remote Service
3. Cancella dati / Cancella spazio di archiviazione
4. Riavvia la TV (stacca la spina per 10 secondi)
5. Riconnetti e riprova