# Lastenheft – Film- & Serien-Tracker

| | |
|---|---|
| **Projektbezeichnung** | Film- & Serien-Tracker |
| **Modul** | Projekt: Software Engineering – 2. Semester |
| **Seminargruppe** | WI25 |
| **Erstellt von** | Matteo Kluge, Fabian Katzung, Simon Heckel |
| **Datum** | 05.05.2026 |
| **Version** | 1.3 |

---

## 1. Ausgangssituation und Zielsetzung

Nutzer von Streaming-Plattformen konsumieren Inhalte auf mehreren Diensten und verlieren schnell den Überblick darüber, welche Filme und Serien sie bereits gesehen haben, welche sie noch sehen möchten und was sie aktuell verfolgen. Ziel des Projekts ist die Entwicklung einer webbasierten Anwendung, die Nutzern ermöglicht, ihre persönlichen Film- und Serienaktivitäten zentral zu verwalten und nachzuverfolgen.

Die Anwendung soll plattformunabhängig als Website zugänglich sein und auf mobilen Geräten komfortabel genutzt werden können – etwa durch Hinzufügen zum Startbildschirm als Progressive Web App (PWA).

---

## 2. Produkteinsatz

Die Anwendung richtet sich an Privatnutzer, die:

- den Überblick über gesehene und geplante Inhalte behalten wollen,
- persönliche Listen verwalten möchten,
- plattformübergreifend (PC, Smartphone, Tablet) auf ihre Daten zugreifen wollen.

Die Anwendung wird als verteiltes System realisiert: Ein zentraler Server verwaltet Nutzerdaten und den gemeinsamen Medienkatalog; der Zugriff erfolgt ausschließlich über den Webbrowser.

---

## 3. Funktionale Anforderungen

### 3.1 Nutzerverwaltung

| ID | Anforderung | Priorität |
|---|---|---|
| FA-01 | Die Anwendung muss eine Registrierung mit Benutzername und Passwort ermöglichen. | Muss |
| FA-02 | Die Anwendung muss eine Anmeldefunktion (Login) bereitstellen. | Muss |
| FA-03 | Die Anwendung soll eine Passwort-vergessen-Funktion über Sicherheitsfragen anbieten. <br>(z. B. *Wie hieß dein erstes Haustier?*) | Kann |
| FA-04 | Jeder Nutzer muss über einen individuellen Datenbereich verfügen; <br>Alle Listen und Aktivitäten sind strikt von anderen Nutzern getrennt. | Muss |
| FA-05 | Nutzerdaten – insbesondere Passwörter – müssen sicher gespeichert werden (Hashing/Verschlüsselung). | Muss |

### 3.2 Filmkatalog

| ID | Anforderung | Priorität |
|---|---|---|
| FA-06 | Das System muss eine zentrale Schnittstelle auf eine Filmdatenbank bereitstellen mit den Feldern: <br>Titel, Erscheinungsjahr, Kurzbeschreibung, Altersbegrenzung, Laufzeit, Studio/Publisher, Genre(s), <br>Hauptdarsteller, Regisseur, Streaming-Dienste | Muss |
| FA-07 | Der Filmkatalog soll den einfachen Zugriff auf TMDb (Film- und Seriendatenbank) bereitstellen. | Soll |

### 3.3 Serienkatalog

| ID | Anforderung | Priorität |
|---|---|---|
| FA-08 | Das System muss eine zentrale Schnittstelle auf eine Seriendatenbank bereitstellen mit den Feldern: <br>Titel, Erscheinungsjahr, Kurzbeschreibung, Altersbegrenzung, Anzahl Staffeln und Folgen, Studio/Publisher, <br>Genre(s), Hauptdarsteller, Regisseur, Streaming-Dienste | Muss |
| FA-09 | Der Serienkatalog soll den einfachen Zugriff auf TMDb (Film- und Seriendatenbank) bereitstellen. | Soll |

### 3.4 Lokale Nutzerlisten

| ID | Anforderung | Priorität |
|---|---|---|
| FA-10 | Kann ein Nutzer einen Film oder eine Serie nicht im zentralen Katalog finden, soll er diesen Eintrag in einer <br>eigenen, nutzerspezifischen lokalen Liste speichern können. | Kann |

### 3.5 Listen-Features

| ID | Anforderung | Priorität |
|---|---|---|
| FA-11 | Jeder Nutzer soll eine **Watchlist** führen können (Inhalte, die er noch sehen möchte). | Soll |
| FA-12 | Jeder Nutzer muss eine **Schon-gesehen-Liste** führen können. | Muss |
| FA-13 | Jeder Nutzer soll eine **Schaue-ich-aktuell-Liste** führen können. | Kann |
| FA-14 | Einträge sollen zwischen den Listen verschoben werden können (z. B. von der Watchlist in die Schon-gesehen-Liste). | Kann |

### 3.6 Suche und Filter

| ID | Anforderung | Priorität |
|---|---|---|
| FA-15 | Die Anwendung muss eine Suchfunktion für Filme und Serien nach Titel bereitstellen. | Muss |
| FA-16 | Die Anwendung kann eine Filterfunktion bereitstellen, z. B. nach Genre, Erscheinungsjahr oder Laufzeit. | Kann |
| FA-17 | Die Suchfunktion kann aus der bestehenden Eingabe eine Vervollständigung vorschlagen. | Kann |

---

## 4. Optionale Anforderungen (Wunschfunktionen)

Die folgenden Funktionen werden angestrebt, sind jedoch nicht zwingend für den Grundbetrieb erforderlich:

| ID | Anforderung |
|---|---|
| OA-01 | **Statistiken:** Anzeige persönlicher Statistiken, z. B. Anzahl gesehener Filme pro Genre oder Gesamtanzahl gesehener Inhalte. |
| OA-02 | **Bewertungsfunktion:** Nutzer können gesehenen Inhalten eine persönliche Bewertung vergeben. |
| OA-03 | **Empfehlungen:** Unter einem angezeigten Film oder einer Serie werden ähnliche Inhalte vorgeschlagen. |
| OA-04 | **Entdecken-Bereich:** Eine eigene Sektion mit kuratierten oder zufälligen Inhaltsvorschlägen. |
| OA-05 | **Medienanzeige:** Thumbnails und ggf. Trailer-Links werden bei Filmen und Serien angezeigt. |
| OA-06 | **Erweitertes Login:** Anzeigename getrennt vom Login-Namen; optionale Anmeldung über Apple- oder Google-Konto (SSO). |
| OA-07 | **Lieblingsschauspieler:** Nutzer können Schauspieler als Favoriten markieren und erhalten Hinweise auf Neuerscheinungen. |
| OA-08 | **Präferenzbasierter Algorithmus:** Auf Basis von Nutzerbewertungen werden Filmvorschläge personalisiert. |

---

## 5. Nicht-funktionale Anforderungen

| ID | Anforderung |
|---|---|
| NFA-01 | Die Anwendung muss mehrere Nutzer gleichzeitig unterstützen, ohne merkbare Leistungseinbußen. |
| NFA-02 | Die Anwendung muss über einen Standard-Webbrowser ohne gesonderte Installation nutzbar sein. |
| NFA-03 | Die Anwendung kann auf mobilen Geräten korrekt dargestellt werden (Responsive Design bzw. PWA-Verknüpfung). |
| NFA-04 | Nutzerdaten dürfen ausschließlich dem jeweiligen Nutzer zugänglich sein (strikte Datentrennung). |
| NFA-05 | Passwörter dürfen nicht im Klartext gespeichert werden. |
| NFA-06 | Die Antwortzeiten der Anwendung sollen bei normaler Last unter 2 Sekunden liegen. |

---

## 6. Systemabgrenzung – bewusste Ausschlüsse

Folgende Funktionen wurden bewusst aus dem Projektumfang ausgeschlossen:

- **Nutzer-seitige Katalogbeiträge:** Nutzer können keine neuen Einträge zur zentralen Datenbank einreichen oder beantragen. Als Alternative steht die individuelle lokale Liste je Nutzer zur Verfügung (vgl. FA-09).  
  *Grund: Skalierbarkeits- und Moderationsaufwand.*

---

## 7. Daten und Schnittstellen

- Der zentrale Medienkatalog wird über eine externe Film-API (z. B. TMDb) oder eine KI-gestützte Methode initial befüllt und kann periodisch aktualisiert werden.
- Die Kommunikation zwischen Client (Browser) und Server erfolgt über definierte API-Endpunkte, sodass Frontend und Backend unabhängig voneinander betrieben werden können (verteilte Architektur).
- Jeder Nutzer besitzt einen eigenen, isolierten Datenbereich in der Nutzerdatenbank sowie eine eigene lokale Liste für nicht im Katalog gefundene Einträge.

---

## 8. Glossar

| Begriff | Erläuterung |
|---|---|
| **Watchlist** | Liste der Inhalte, die ein Nutzer noch sehen möchte. |
| **Schon-gesehen-Liste** | Liste bereits konsumierter Film- und Serieninhalte. |
| **Schaue-ich-aktuell** | Liste von Inhalten, die gerade aktiv verfolgt werden. |
| **Verteilte Anwendung** | System, bei dem Client und Server auf getrennten Systemen laufen. |
| **Lokale Nutzerliste** | Nutzerspezifische Liste für Einträge, die nicht im zentralen Katalog vorhanden sind. |
| **PWA** | Progressive Web App – Webanwendung, die sich auf mobilen Geräten wie eine native App verhält. |
| **SSO** | Single Sign-On – Anmeldung über einen externen Identitätsanbieter (z. B. Google, Apple). |
| **TMDb** | The Movie Database – frei verfügbare Film- und Serien-API. |
