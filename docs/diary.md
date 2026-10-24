# Development Diary & Progress Log

In diesem File sind Notizen dessen festgehalten, was im Laufe des Projektes gemacht wurde. 

---

## 17.10.2026

Im Unterricht mit Silvan Wegmann ausgetauscht, Projekt "GO" erhalten.
Entscheidung, dass wir zu zweit sind wurde zur Kenntnis genommen.


---

## 22.10.2026
.venv und uv sync verstanden und auf verschiedenen Geräten getestet.
Git Desktop installiert um alles darüber zu syncen.

decision0001 erstellt bezüglich docker und/oder render.com

hello.py erstellt als ersten lauffähigen Prototyp. mit localhost:8000 getestet, damit im Anschluss render.com getestet werden konnte.

docker desktop installiert und ebenfalls getestet

render.com aufgesetzt und mit der git repo verbunden. automatisches deployment funktioniert. die einfache app funktioniert ebenfalls (nach entsprechender anpassung des docker files).

hello.py nach dem testing wieder entfernt, bzw. ins /root verfrachtet.

---

## 23.10.2026

anhand "SW04 - Technologien - Auswahl und Empfehlungen.pdf", die anzuwendenden Technologien besser verstanden, was in den weiteren Entscheidungsprozess einfliesst.

überlegungen für spätere "echte" Projekte, dass man dies auch eigenständig auf einem Raspberry Pi hosten könnte. (vorteile: kostengünstig, keine cloud-abhängigkeit, datenschutz). 

## 24.10.2026

Vorgehen bis zur lauffähigen Applikation besprochen und festgelegt. Die folgende
Kurzfassung wurde gemeinsam mit Claude (KI-Assistent von Anthropic) erarbeitet;
Repo, Aufgabenstellung und SW04-Folien wurden dabei als Grundlage verwendet.

Ablauf:

1. **Requirements Engineering (kurz):** Funktionsweise eines Spielautomaten klären
   (Walzen, Symbole, Walzenbelegung, Gewinnlinien, Auszahltabelle, Auszahlungsquote/RTP).
   Daraus die drei Kernfunktionen ableiten: Spielen, Konfigurieren, Auswerten.
   Mindestumfang (MVP) festlegen.
2. **Fachliche Grundentscheide:** Walzenmodell (Walzenbelegung vs. direkte
   Kombinations-Wahrscheinlichkeiten), Versionierung der Konfiguration.
3. **Technologie-Entscheide** als Decision Records: Backend-Framework (Flask/FastAPI),
   Datenbank und deren Hosting (Render-Postgres läuft nach 30 Tagen ab), Frontend
   (Vue via CDN, HTMX oder Alpine.js), externer Web Service (z.B. random.org mit
   lokalem Fallback). Decision 0002 konkretisieren, Follow-ups aus 0003 erledigen.
4. **Architektur:** Diagramm (Mermaid) mit Frontend, Backend, Datenbank und
   externem Service; Datenmodell (Symbole, Konfiguration, Spins).
5. **Walking Skeleton:** Minimale App mit einem Endpoint, einer DB-Tabelle und
   einer Seite, end-to-end auf Render deployt.
6. **CI:** GitHub Actions mit Linter (ruff) und Tests (pytest).
7. **Spiellogik:** Als reines Python-Modul ohne Web-Framework, mit Unittests.
8. **Feature Spielen:** Spin-Endpoint, Speicherung in der DB, Spiel-GUI.
9. **Feature Konfigurieren:** Konfigurations-GUI und -Endpoints.
10. **Feature Auswerten:** Soll- vs. Ist-Trefferquoten und Auszahlungsquote.
11. **Abschluss:** README, Diagramm, Tests vervollständigen; Präsentation
    vorbereiten (eine technische Herausforderung im Detail).

Laufend: Entscheide, Probleme und Diary führen (Grundlage für die Reflexion), sauber beschriebene Commits.


Requirements Engineering durchgeführt (gemeinsam mit Claude besprochen), Resultat
in `docs/requirements.md`. Wichtigste Entscheide: klassischer Automat mit 3 Walzen
und 1 Gewinnlinie, Konfiguration über Reel Strips inkl. Blanks, konfigurierbare
Auszahltabelle (drei Gleiche und Kirschen-Zähler), unveränderliche, versionierte
Konfigurationen in eigener Tabelle, Symbole als Codes im Backend und Darstellung
als Emoji im Frontend. Manuelle Spins nutzen random.org als externen Web Service
(Fallback auf Python), Autospin und Massensimulation laufen mit Python.
Grundregel für das Projekt: immer die pragmatische, einfachere Variante wählen.


aus der Diskussion mit der KI weitere decisions festgehalten.

Architecure.md erstellt und mittels mermaid grafisch dargestellt. (Erstes Mermaid Diagramm überhaupt für mich)

