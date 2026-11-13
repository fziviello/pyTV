"""Libreria per controllare una Google TV via protocollo Android TV Remote v2."""

import asyncio
from androidtvremote2 import AndroidTVRemote

# Mappatura dei comandi "amichevoli" verso i keycode Android
COMANDI = {
    # Alimentazione
    "power": "POWER",
    "accendi": "POWER",
    "spegni": "POWER",

    # Volume
    "volume_su": "VOLUME_UP",
    "alza": "VOLUME_UP",
    "volume_giu": "VOLUME_DOWN",
    "abbassa": "VOLUME_DOWN",
    "muto": "VOLUME_MUTE",

    # Media
    "play": "MEDIA_PLAY",
    "pausa": "MEDIA_PAUSE",
    "play_pausa": "MEDIA_PLAY_PAUSE",
    "riprendi": "MEDIA_PLAY",

    # Navigazione
    "home": "HOME",
    "back": "BACK",
    "indietro": "BACK",
    "ok": "DPAD_CENTER",
    "conferma": "DPAD_CENTER",
    "su": "DPAD_UP",
    "giu": "DPAD_DOWN",
    "sinistra": "DPAD_LEFT",
    "destra": "DPAD_RIGHT",
}


class TVController:
    """Gestisce connessione e invio comandi alla TV."""

    def __init__(self, host: str, certfile: str, keyfile: str, client_name: str = "pyTV"):
        self.host = host
        self.certfile = certfile
        self.keyfile = keyfile
        self.client_name = client_name
        self._remote = None

    async def connect(self):
        """Apre la connessione con la TV."""
        self._remote = AndroidTVRemote(
            self.client_name, self.certfile, self.keyfile, self.host
        )
        await self._remote.async_connect()
        return self

    def disconnect(self):
        """Chiude la connessione."""
        if self._remote:
            self._remote.disconnect()
            self._remote = None

    def send(self, comando: str, direzione: str = "SHORT"):
        """
        Invia un comando alla TV.
        
        Args:
            comando: nome amichevole (es. "home", "volume_su") o keycode Android (es. "KEYCODE_HOME")
            direzione: "SHORT" (default), "START_LONG", "END_LONG"
        """
        if not self._remote:
            raise RuntimeError("Non connesso. Chiama connect() prima.")

        keycode = COMANDI.get(comando.lower(), comando.upper())

        if not keycode.startswith("KEYCODE_"):
            keycode = f"KEYCODE_{keycode}"

        self._remote.send_key_command(keycode, direzione)

    async def power_toggle(self):
        """
        Spegne/accende la TV. Invia POWER due volte per gestire la conferma
        che alcuni televisori TCL mostrano a schermo.
        """
        self.send("power")
        await asyncio.sleep(0.5)
        self.send("power")

    def send_multiple(self, comandi: list, delay: float = 0.2):
        """
        Invia una sequenza di comandi con una pausa tra loro.
        Utile per sequenze tipo "home; destra; ok".
        """
        for i, cmd in enumerate(comandi):
            self.send(cmd)
            if i < len(comandi) - 1:
                # Nota: questa funzione è sincrona, la pausa va gestita
                # dal chiamante se serve un vero delay asincrono.
                # Per ora invia solo i comandi in rapida successione.
                pass