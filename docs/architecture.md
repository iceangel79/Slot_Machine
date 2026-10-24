# Architecture

Date: 2026-10-24

Overview of the Slot Machine Simulator. Requirements: `docs/requirements.md`.
Decisions: `docs/decisions/` (in particular 0004 to 0009).

## Components

```mermaid
flowchart LR
    user([User / Browser])

    subgraph render["Render (web service)"]
        subgraph backend["Python backend (Flask, Gunicorn)"]
            api["API routes<br/>app/__init__.py"]
            game["Game logic<br/>app/game.py"]
            rng["Random sources<br/>app/rng.py"]
            db["Database access<br/>app/db.py"]
            static["Static frontend<br/>app/static/ (HTML, Vue via CDN)"]
        end
    end

    neon[("PostgreSQL<br/>(Neon)")]
    randomorg["random.org<br/>(external web service)"]

    user -- "HTTP: pages" --> static
    user -- "HTTP: JSON API" --> api
    api --> game
    api --> db
    game --> rng
    rng -- "HTTP (manual spins)" --> randomorg
    db -- "SQL" --> neon
```

| Component | Responsibility |
|---|---|
| Static frontend | Three views: play, configure, analyse. Maps symbol codes to emoji. No calculations. |
| API routes | Receives requests, validates input, returns JSON. |
| Game logic | Pure Python, no Flask: draws stop positions, evaluates the paytable, calculates theoretical probabilities, hit frequency and RTP. Unit tested. |
| Random sources | random.org for manual spins, Python (`secrets`) for autospin and mass simulation and as fallback. |
| Database access | Reads and writes configurations and spins. |
| PostgreSQL (Neon) | Persistent storage. Connection string in `DATABASE_URL`. |
| random.org | True random numbers based on atmospheric noise. |

## Data model

```mermaid
erDiagram
    CONFIGURATIONS ||--o{ SPINS : "played with"

    CONFIGURATIONS {
        int id PK
        text name
        timestamp created_at
        jsonb reel_strips "3 lists of symbol codes"
        jsonb paytable "list of rules"
    }

    SPINS {
        int id PK
        int configuration_id FK
        timestamp created_at
        text symbol_1
        text symbol_2
        text symbol_3
        int bet
        int payout
        text rng_source "random.org or python"
    }
```

Notes:

 * Configurations are immutable (decision 0007). A change creates a new row.
 * Reel strips and paytable are stored as JSON in one row each. They are
   always read and written as a whole, so separate tables are not needed.
 * The bet is fixed at 1 credit per spin in the MVP; the payout is the
   paytable multiplier.

## API (first draft)

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/configurations` | List all configurations |
| GET | `/api/configurations/<id>` | One configuration |
| POST | `/api/configurations` | Save a new configuration |
| POST | `/api/configurations/evaluate` | Calculate probabilities and RTP without saving (live in the editor) |
| POST | `/api/spins` | Execute spins: `{configuration_id, mode, count}` with `mode` = `manual` (1 spin, random.org) or `auto` (n spins, Python) |
| GET | `/api/configurations/<id>/analysis` | Theoretical vs. actual values for one configuration |

Autospin with delay is a loop in the frontend that calls `/api/spins` with
`mode=auto, count=1`. Mass simulation is a single call with a large `count`.

## Manual spin with fallback

```mermaid
sequenceDiagram
    actor U as User
    participant F as Frontend
    participant B as Backend
    participant R as random.org
    participant D as PostgreSQL

    U->>F: click "Spin"
    F->>B: POST /api/spins (mode=manual)
    B->>R: request 3 random numbers
    alt random.org reachable
        R-->>B: numbers
    else error or timeout
        B->>B: use Python (secrets) instead
    end
    B->>B: map numbers to stop positions, evaluate paytable
    B->>D: INSERT spin (incl. rng_source)
    B-->>F: symbols, payout, rng_source
    F-->>U: show emoji and payout
```
