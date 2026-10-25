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

---

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

---

## 25.10.2026

aufräumen: hello.py entfernt.

Account bei neon (database service) erstellt und connection-string erhalten.
String in .env eingerichtet und sichergestellt, dass .env von gitignore beachtet wird.
String in render.com als environment variable eingerichtet.

---

Walking Skeleton (Schritt 5): minimale App mit einem Endpoint, einer DB-Tabelle und einer Seite.
Mit Claude das "WS" erstellt und lokal gestartet. in Neon wurden die beiden Tables erfolgreich erstellt. auf localhost wird im browser der entsprechende erfolgt ausgewiesen.
Testing auf Render.com mit autodeploy war ebenfalls erfolgreich!

---

Continuous Integration (Schritt 6): GitHub Actions mit Linter (ruff) und Tests (pytest). Es wurden Tests für die Endpunkte und Tests für die Datenbankanbindung erstellt. Die Tests wurden erfolgreich durchgeführt.
Bewusster Fehler eingebaut, "assert b"Slot Machine Simulator" in response.data" geändert auf "assert b"Fehler" in response.data". Dies führte zu einem fehlerhaften Testresultat.
im Anschluss korrigiert und "assert b"Fehler" in response.data" geändert auf "assert b"Fehler" in response.data" .
verstanden, dass ci.yml automatische tests nach dem commit auf github durchführt. dies dient vor allem auch dazu, dass wenn verschiedene personen an etwas arbeiten, diese nicht unwissentlich fehlerhafte Code teile ins Hauptsystem bringen.

Fazit zu Schritt 6: Es gibt aktuell zwei Tests, einen für die Startseite und einen für den Health-Check inklusive DB-Verbindung. 

---

Spiellogik (Schritt 7): reines Python-Modul ohne Flask und ohne Datenbank (app/game.py, Zufallsquelle in app/rng.py) mit Unittests (tests/test_game.py).
Mit Claude die offenen Entscheide geklärt und in Decision 0012 festgehalten:
- Konfiguration und Auszahltabelle als einfache Dicts, genau so wie sie als JSON in der DB stehen.
- «Kirschen-Zähler» heisst genau n Kirschen, Position egal.
- Treffen mehrere Regeln zu, zahlt nur die höchste. So gehört jeder Spin zu höchstens einer Regel, was die Analyse pro Regel einfach macht.
- Die theoretischen Werte werden nicht mit Formeln berechnet, sondern alle Symbolkombinationen werden mit derselben Funktion ausgewertet wie beim Spielen. Theorie und Praxis können so nicht auseinanderlaufen.
- Die Zufallsquelle wird als Funktion übergeben. In den Tests liefert sie feste Stoppositionen.

Stolperstein: app/__init__.py hat beim Import die Tabellen erstellt. Jeder Import von app.game hätte damit eine Datenbank gebraucht. Lösung: Die Flask-App liegt neu in app/main.py, Gunicorn startet app.main:app (Dockerfile und README angepasst).

Ergebnis: 24 neue Tests laufen ohne Datenbank. Ein Test prüft, dass die theoretische Berechnung dasselbe ergibt wie das Durchprobieren aller Stoppositionen.

---

Feature: Spielen (Schritt 8):
Offene Punkte vorab mit Claude geklärt und als Decisions festgehalten:

* 0013 Startkonfiguration: Solange es keine Konfigurations-GUI gibt, legt die App
  beim Start eine Default-Konfiguration «Classic (default)» an, falls die Tabelle
  `configurations` leer ist. Die Konfiguration steht als `DEFAULT_CONFIG` im Code
  (`game.py`), wird also versioniert und per Unittest geprüft (gültig, RTP 91.0 %,
  Trefferquote 28.4 %). Damit hat jede neue Datenbank (Neon, Test, CI) sofort eine
  spielbare Konfiguration.
* 0014 random.org: Ein Request pro Walze statt ein Request mit drei Zahlen.
  Claude hat darauf hingewiesen, dass auch drei Zahlen aus einem Request
  unabhängig wären. Der eigentliche Vorteil von drei Requests: Jede Zahl liegt
  exakt im Bereich ihrer Walze, es braucht keinen Modulo und es gibt keine
  Verzerrung. Kein API-Key nötig. Fällt einer der drei Requests aus, wird der
  ganze Spin mit Python gezogen, damit `rng_source` eindeutig bleibt.
* 0015 Test-Datenbank: Eigener Neon-Branch `test` (Parent `production`), URL als
  `TEST_DATABASE_URL` in `.env`. `tests/conftest.py` biegt `DATABASE_URL` vor dem
  Import der App auf die Test-DB um. Ohne `TEST_DATABASE_URL` werden die API-Tests
  gar nicht erst gesammelt, so können sie nie versehentlich in die Produktiv-DB
  schreiben. Damit ist das Risiko aus 0011 erledigt. In der CI heisst die
  Variable jetzt ebenfalls `TEST_DATABASE_URL`.

Umgesetzt (Entwürfe von Claude, selbst eingebaut und committed):

* `POST /api/spins` mit `mode` manual (1 Spin, random.org mit Fallback) und
  auto (bis 10'000 Spins, Python), dazu `GET /api/configurations` und
  `GET /api/configurations/<id>`.
* Die Obergrenze von 10'000 Spins pro Request schützt vor dem 30-Sekunden-Timeout
  von Gunicorn. Grössere Massensimulationen teilt das Frontend auf mehrere
  Requests auf.
* Speichern aller Spins eines Requests in einer Transaktion mit `executemany`,
  damit die Massensimulation trotz Netzwerk zur Neon-DB schnell bleibt.
* Spiel-GUI in Vue: manueller Spin mit Anzeige der Zufallsquelle, Autospin mit
  Verzögerung und Stop, Massensimulation mit Ist-RTP, Summen der Session.
* 46 Tests (Spiellogik, random.org-Parsing und Fallback, Endpoints). random.org
  wird in den Tests nie aufgerufen, sondern mit `monkeypatch` ersetzt.

Erkenntnisse:

* Neon-Branch: Beim Kopieren des Connection Strings unbedingt im Connect-Dialog
  den Branch `test` wählen, sonst landen die Testdaten doch in `production`.
  Kontrolle über den Hostnamen (`ep-...`), der sich je Branch unterscheidet.
* Trick mit `lambda _lengths: stops`: `game.spin()` erwartet eine Zufallsquelle
  als Funktion. Die Zahlen von random.org sind aber schon gezogen, also bekommt
  `spin()` eine Funktion, die genau diese Zahlen zurückgibt. So bleibt `game.py`
  frei von Netzwerk und Fallback.
* Die Massensimulation mit 10'000 Spins ergibt einen RTP von rund 91 %, die
  Praxis bestätigt also die Theorie.

Test:

* Lokal und auf Render alles funktionsfähig, auch auf dem Smartphone über das
  Internet getestet.
* random.org funktioniert auch von Render aus (Quelle wird als `random.org`
  angezeigt).
* Gespeicherte Spins inkl. `rng_source` manuell in der Neon Console geprüft.


---

Schritt 9: Feature Konfigurieren

Offene Punkte vorab mit Claude geklärt und als Decisions festgehalten:

* 0016 Konfigurations-Editor:
  * Die Walzen werden als Anzahl Positionen pro Symbol und Walze in einem Raster
    (6 Symbole × 3 Walzen) erfasst, nicht als geordnete Liste. Bei einer
    Gewinnlinie und gleich wahrscheinlichen Stopps hat die Reihenfolge auf der
    Walze keinen Einfluss auf die Wahrscheinlichkeiten. Backend und DB bleiben
    unverändert, gespeichert wird weiterhin die Liste.
  * Der Editor startet immer als Kopie einer bestehenden Konfiguration und
    speichert als neue Konfiguration (passt zu den unveränderlichen
    Konfigurationen aus 0007).
  * Die theoretischen Werte (RTP, Trefferquote, Wahrscheinlichkeit pro Regel)
    berechnet das Backend live über `POST /api/configurations/evaluate`, jeweils
    300 ms nach der letzten Änderung (Debounce). Keine Berechnung in
    JavaScript, damit Theorie und Spiel dieselbe Funktion verwenden.
  * Eine Seite pro Feature (`index.html`, `configure.html`, später
    `analyse.html`) mit Navigation. Gemeinsame Styles in `style.css`, die
    Emoji-Tabelle in `common.js`.
* 0017 Walzenlänge: maximal 30 Positionen. Begründung mit den klassischen
  Vegas-Automaten: Die ersten Automaten um 1900 hatten etwa 10 Symbole pro
  Walze, später waren 20 und ab den 1960er-Jahren meist 22 Stopps üblich.
  Mehr ging mechanisch nicht. Erst virtuelle Walzen ab den 1980er-Jahren
  erlaubten mehr Positionen (bei uns out of scope). Die Länge macht die
  Konfiguration übrigens nicht aufwendiger: Erfasst wird nur die Anzahl pro
  Symbol, und die Berechnung prüft immer höchstens 216 Kombinationen.

Weitere Regeln: Name ist Pflicht (max. 100 Zeichen). Ein RTP über 100 % darf
gespeichert werden, der Editor zeigt aber eine Warnung. Konfigurationen können
nicht gelöscht werden, weil Spins darauf verweisen.

Umgesetzt (Entwürfe von Claude, selbst eingebaut und committed):

* Begrenzung der Walzenlänge in `validate_config()`.
* Endpoints `POST /api/configurations/evaluate` und `POST /api/configurations`.
* Gemeinsame `style.css` und `common.js`, Navigation auf allen Seiten.
* Editor-Seite `configure.html`.
* 56 Tests.

Erkenntnisse:

* Die Umrechnung zwischen Liste und Anzahl pro Symbol passiert nur im Frontend
  (`countSymbols()` beim Laden, `buildStrip()` beim Senden).
* Vorher in der CI ein roter Lauf: Die Zeile mit dem User-Agent für random.org
  war mit meiner E-Mail-Adresse länger als 88 Zeichen (ruff E501). Korrigiert.
* Fehler beim Einbauen: Den `<link>` zur CSS-Datei und das `<script>` für
  `common.js` hatte ich innerhalb von `<style>` platziert. Der Browser liest
  dort alles als CSS-Text und ignoriert die Tags, darum fehlten Styles und die
  Emoji-Tabelle (`EMOJI is not defined`). Zusätzlich hiess die Datei
  `styles.css` statt `style.css`. Beides korrigiert. Lehre: Bei Problemen im
  Frontend zuerst die Browser-Konsole (F12) anschauen.


