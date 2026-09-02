import os
import time
from fastapi import FastAPI
from contextlib import asynccontextmanager
import threading
import uvicorn

UVICORN_HOST = "localhost"
UVICORN_PORT = 8000

@asynccontextmanager
async def lifespan(app: FastAPI):
    Thread = threading.Thread(target=MainThread, daemon=True)
    Thread.start()

    # Datenbank Verbindung öffnen

    print("Anwendung startet: Synchroner Connection Pool initialisiert.")

    yield

    print("Anwendung schließt: Alle Pool-Verbindungen werden getrennt.")
    # Datenbank Verbindung trennen

    Thread.join(timeout=5.0)
    
app = FastAPI(title="Testserver",lifespan=lifespan)

def MainThread():
    while True:
        try:
            print ("Führe periodischen DB-Check im Hintergrund-Thread aus...")
            # Hier Ihr synchroner Code, z.B.
            # - Datenbank: Verbidnungen prüfen, Tabellen aufräumen, ...
            # - externe APIs abfragen
            
            time.sleep (10)
        
        except Exception as exception:
            print(f"Fehler im Hintergrund-Task: {exception}")
            break

@app.get("/hello")
def hello():
    return{"message": "Hello World"}



if __name__ == "__main__":
    uvicorn.run(app, host=UVICORN_HOST, port=UVICORN_PORT, log_level="info")