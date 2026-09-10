import getpass
import json
import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

UVICORN_HOST = os.getenv("UVICORN_HOST", "127.0.0.1")
UVICORN_PORT = int(os.getenv("UVICORN_PORT", "8000"))
REST_API_URL = f"http://{UVICORN_HOST}:{UVICORN_PORT}"
SESSION = requests.Session()


def clearScreen():
    """Loescht den Bildschirm mit dem plattformspezifischen Befehl."""
    os.system("cls" if os.name == "nt" else "clear")


def showMenu():
    print("Client fuer Projekt1-Gruppe2 - FilmeSerienTracker")
    print()
    print("Bitte Option auswaehlen:")
    print("r - Registrieren")
    print("l - Login")
    print("a - Aktuell angemeldeten Benutzer anzeigen")
    print("o - Logout")
    print("h - Hello World")
    print("m - Film ueber den Server bei TMDB suchen")
    print("e - Programm beenden")
    print()


def print_api_error(response: requests.Response):
    try:
        detail = response.json().get("detail", "Unbekannter API-Fehler")
    except (json.JSONDecodeError, AttributeError):
        detail = "Antwort des Servers konnte nicht gelesen werden"
    print(f"Fehler ({response.status_code}): {detail}")


def request_api(method: str, endpoint: str, **kwargs) -> requests.Response | None:
    try:
        return SESSION.request(method, REST_API_URL + endpoint, timeout=10.0, **kwargs)
    except requests.exceptions.Timeout:
        print("Fehler bei der Anfrage: Timeout")
    except requests.exceptions.ConnectionError:
        print("Fehler bei der Anfrage: Verbindungsfehler")
    except requests.exceptions.RequestException as exception:
        print(f"Fehler bei der Anfrage: {exception}")
    return None


def requestRegister():
    username = input("Benutzername: ").strip()
    password = getpass.getpass("Passwort: ")
    confirmation = getpass.getpass("Passwort wiederholen: ")
    if password != confirmation:
        print("Die Passwoerter stimmen nicht ueberein.")
        return

    response = request_api(
        "POST", "/auth/register", json={"username": username, "password": password}
    )
    if response is None:
        return
    if response.status_code == 201:
        print(f"Benutzer {response.json()['username']} wurde angelegt. Bitte jetzt anmelden.")
    else:
        print_api_error(response)


def requestLogin():
    username = input("Benutzername: ").strip()
    password = getpass.getpass("Passwort: ")
    response = request_api(
        "POST", "/auth/login", json={"username": username, "password": password}
    )
    if response is None:
        return
    if response.status_code == 200:
        print(f"Angemeldet als {response.json()['username']}.")
    else:
        print_api_error(response)


def requestCurrentUser():
    response = request_api("GET", "/auth/me")
    if response is None:
        return
    if response.status_code == 200:
        user = response.json()
        print(f"Angemeldet als {user['username']} (ID {user['user_id']}).")
    else:
        print_api_error(response)


def requestLogout():
    response = request_api("POST", "/auth/logout")
    if response is None:
        return
    if response.status_code == 204:
        print("Erfolgreich abgemeldet.")
    else:
        print_api_error(response)


def requestHelloWorld():
    response = request_api("GET", "/hello")
    if response is None:
        return
    if response.status_code == 200:
        print(response.json())
    else:
        print_api_error(response)


def requestMovie():
    query = input("Filmname: ").strip()
    if not query:
        print("Bitte einen Filmnamen eingeben.")
        return

    response = request_api("GET", "/movie/search", params={"query": query})
    if response is None:
        return
    if response.status_code != 200:
        print_api_error(response)
        return

    for movie in response.json().get("results", []):
        print(f"\nTitel: {movie.get('title', 'Unbekannter Titel')}")
        print(f"Veroeffentlichung: {movie.get('release_date', 'Keine Angabe')}")
        print(f"Beschreibung: {movie.get('overview', 'Keine Beschreibung')}")


def main():
    actions = {
        "r": requestRegister,
        "l": requestLogin,
        "a": requestCurrentUser,
        "o": requestLogout,
        "h": requestHelloWorld,
        "m": requestMovie,
    }

    while True:
        clearScreen()
        showMenu()
        try:
            option = input("Auswahl: ").strip().lower()
            if option == "e":
                print("Programm wird beendet.")
                break
            action = actions.get(option)
            if action is None:
                print("Ungueltige Option. Bitte erneut versuchen.")
            else:
                action()
            input("\nEnter druecken, um fortzufahren ...")
        except KeyboardInterrupt:
            print("\nProgramm wird abgebrochen.")
            return

    time.sleep(1)
    print("Programm beendet. Auf Wiedersehen!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
