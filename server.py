import asyncio
import json
import os
import logging
from pathlib import Path

from aiohttp import web
from androidtvremote2 import AndroidTVRemote, InvalidAuth, ConnectionClosed
from zeroconf import ServiceBrowser
from zeroconf.asyncio import AsyncZeroconf

from tv_lib import TVController, COMANDI

# --- File di stato ---
HOST_FILE = "tv_host.json"
CERT_FILE = "tv_cert.pem"
KEY_FILE = "tv_key.pem"

logging.basicConfig(level=logging.DEBUG)


# -------------------------------
# Scoperta e configurazione
# -------------------------------

async def discover_tvs(timeout: float = 4.0) -> list[dict]:
    """Scansiona la rete e restituisce lista di {'host': ip, 'name': nome}."""
    found = {}

    class Listener:
        def add_service(self, zc, type_, name):
            info = zc.get_service_info(type_, name)
            if info and info.parsed_addresses():
                host = info.parsed_addresses()[0]
                display = name.split(".")[0]
                found[host] = display

        def update_service(self, zc, type_, name):
            pass

        def remove_service(self, zc, type_, name):
            pass

    aiozc = AsyncZeroconf()
    browser = ServiceBrowser(aiozc.zeroconf, "_androidtvremote2._tcp.local.", Listener())
    print(f"Scansione rete in corso ({timeout}s)...")
    await asyncio.sleep(timeout)
    await aiozc.async_close()

    return [{"host": h, "name": n} for h, n in found.items()]


async def choose_tv() -> str | None:
    """Scopre, mostra menu, restituisce IP scelto o None."""
    devices = await discover_tvs()

    if not devices:
        print("Nessuna TV trovata. Assicurati che TV e Mac siano sulla stessa rete.")
        print("Puoi anche inserire l'IP manualmente.")
        manual = input("IP della TV (invio per uscire): ").strip()
        return manual if manual else None

    print("\nDispositivi trovati:")
    for i, d in enumerate(devices, 1):
        print(f"  {i}. {d['host']}  ({d['name']})")

    while True:
        try:
            choice = input(f"Scegli (1-{len(devices)}) o premi invio per uscire: ").strip()
            if not choice:
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(devices):
                return devices[idx]["host"]
        except ValueError:
            pass
        print("Scelta non valida.")


async def pair_if_needed(host: str, remote: AndroidTVRemote) -> bool:
    """Esegue l'accoppiamento se i certificati non esistono già."""
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        return True

    await remote.async_generate_cert_if_missing()
    print(f"\nAccoppiamento con {host}...")
    print("Sulla TV dovrebbe apparire un PIN di 6 cifre.")
    try:
        await remote.async_start_pairing()
    except Exception as e:
        print(f"Errore avvio accoppiamento: {type(e).__name__}: {repr(e)}")
        return False

    while True:
        code = input("Inserisci il PIN mostrato sulla TV: ").strip()
        try:
            await remote.async_finish_pairing(code)
            print("Accoppiamento completato.")
            return True
        except InvalidAuth:
            print("PIN errato, riprova.")
        except ConnectionClosed:
            print("Connessione chiusa durante l'accoppiamento.")
            return False


# -------------------------------
# Handler HTTP
# -------------------------------

async def send_power(host: str):
    controller = TVController(host, CERT_FILE, KEY_FILE)
    await controller.connect()
    try:
        await controller.power_toggle()
    finally:
        controller.disconnect()


async def handle_power(request):
    host = load_host()
    if not host:
        return web.json_response({"status": "error", "message": "TV non configurata"}, status=400)
    try:
        await send_power(host)
        return web.json_response({"status": "ok", "action": "power_toggled"})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({"status": "error", "message": f"{type(e).__name__}: {e}"}, status=500)


async def handle_command(request):
    """
    Endpoint generico: POST /command
    Body JSON: {"cmd": "home"} oppure {"cmd": "volume_su", "direction": "SHORT"}
    Accetta sia nomi amichevoli (da COMANDI) sia keycode Android (es. "KEYCODE_HOME").
    """
    host = load_host()
    if not host:
        return web.json_response({"status": "error", "message": "TV non configurata"}, status=400)

    try:
        body = await request.json()
    except Exception:
        return web.json_response({"status": "error", "message": "JSON non valido"}, status=400)

    cmd = body.get("cmd")
    if not cmd:
        return web.json_response({"status": "error", "message": "Campo 'cmd' mancante"}, status=400)

    direction = body.get("direction", "SHORT")

    controller = TVController(host, CERT_FILE, KEY_FILE)
    try:
        await controller.connect()
        controller.send(cmd, direction)
        return web.json_response({"status": "ok", "cmd": cmd, "direction": direction})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({"status": "error", "message": f"{type(e).__name__}: {e}"}, status=500)
    finally:
        controller.disconnect()


async def handle_commands_list(request):
    """GET /commands - elenca i comandi amichevoli disponibili."""
    return web.json_response({"commands": sorted(COMANDI.keys())})


# -------------------------------
# Stato su disco
# -------------------------------

def load_host() -> str | None:
    if Path(HOST_FILE).exists():
        try:
            return json.loads(Path(HOST_FILE).read_text())["host"]
        except Exception:
            pass
    return None


def save_host(host: str):
    Path(HOST_FILE).write_text(json.dumps({"host": host}, indent=2))


# -------------------------------
# Main
# -------------------------------

async def main():
    host = load_host()

    if not host:
        print("Nessun IP salvato, avvio scoperta...")
        host = await choose_tv()
        if not host:
            print("Nessuna TV selezionata, esco.")
            return
        save_host(host)
        print(f"IP salvato: {host}")
    else:
        print(f"Uso IP salvato: {host}")

    remote = AndroidTVRemote("tv-control-pc", CERT_FILE, KEY_FILE, host)
    ok = await pair_if_needed(host, remote)
    if not ok:
        print("Accoppiamento fallito.")
        return

    app = web.Application()
    app.router.add_post("/power", handle_power)
    app.router.add_post("/command", handle_command)
    app.router.add_get("/commands", handle_commands_list)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8787)
    await site.start()

    print(f"\nServer su http://localhost:8787 (TV: {host})")
    print("Endpoint disponibili:")
    print("  POST /power              - spegne/accende (con doppio invio per TCL)")
    print("  POST /command            - invia un comando qualsiasi")
    print("  GET  /commands           - elenca i comandi amichevoli")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())