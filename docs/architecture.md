# Architecture

Date: 2026-10-24, updated 2026-10-26

Overview of the Slot Machine Simulator. Requirements: `docs/requirements.md`.
Decisions: `docs/decisions/` (0004 to 0018).

## Components

```mermaid
flowchart LR
    user([User / Browser])

    subgraph render["Render (web service, Docker)"]
        subgraph backend["Python backend (Flask, Gunicorn)"]
            api["API routes<br/>app/main.py"]
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
    api --> rng
    api --> db
    rng -- "HTTP (manual spins)" --> randomorg
    db -- "SQL" --> neon
```

| Component | Responsibility |
|---|---|
| Static frontend | Three pages: `index.html` (play), `configure.html`, `analyse.html`. `common.js` maps symbol codes to emoji, `style.css` holds the shared styles. No calculations (decisions 0005, 0016). |
| API routes | Receives requests, validates input, returns JSON. Calls the random source and passes the drawn stop positions to the game logic. |
| Game logic | Pure Python, no Flask, no database: evaluates the paytable, executes spins with a given random source, calculates theoretical values and the analysis (decisions 0012, 0018). Unit tested. |
| Random sources | random.org for manual spins with fallback to Python; Python (`secrets`) for autospin and mass simulation (decisions 0008, 0014). |
| Database access | Plain SQL with `psycopg`: configurations, spins, grouped spins for the analysis (decision 0010). |
| PostgreSQL (Neon) | Persistent storage. Connection string in `DATABASE_URL` (decision 0006). |
| random.org | True random numbers based on atmospheric noise. |

## Deployment and CI

```mermaid
flowchart LR
    dev([Developer]) -- "git push" --> github["GitHub<br/>repository"]
    github -- "every push" --> actions["GitHub Actions<br/>ruff + pytest"]
    actions -- "SQL" --> pgci[("PostgreSQL<br/>service container")]
    github -- "every push<br/>(auto deploy)" --> renderbuild["Render<br/>Docker build"]
    renderbuild --> app["Web service<br/>slot-machine-nlsl.onrender.com"]
    app -- "DATABASE_URL" --> prod[("Neon branch<br/>production")]
    local["Local pytest"] -- "TEST_DATABASE_URL" --> test[("Neon branch<br/>test")]
```

 * CI and deployment run in parallel; Render does not wait for the CI result
   (decision 0011).
 * Tests never use the production database (decision 0015).
 * Tables, index and default configuration are created at startup
   (decisions 0010, 0013).

## Data model

```mermaid
erDiagram
    CONFIGURATIONS ||--o{ SPINS : "played with"

    CONFIGURATIONS {
        int id PK
        text name
        timestamptz created_at
        jsonb reel_strips "3 lists of symbol codes"
        jsonb paytable "list of rules"
    }

    SPINS {
        int id PK
        int configuration_id FK
        timestamptz created_at
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
 * The bet is fixed at 1 credit per spin; the payout is the paytable
   multiplier.
 * The winning rule of a spin is not stored; the analysis recalculates it from
   the three symbols (decisions 0012 and 0018). An index on
   `spins (configuration_id)` keeps the analysis fast with many spins.

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Check that the backend runs and the database is reachable |
| GET | `/api/configurations` | List all configurations (id, name, created_at), newest first |
| GET | `/api/configurations/<id>` | One configuration with reel strips and paytable |
| POST | `/api/configurations` | Save a new configuration: `{name, reel_strips, paytable}` |
| POST | `/api/configurations/evaluate` | Theoretical values without saving (live in the editor) |
| POST | `/api/spins` | Execute spins: `{configuration_id, mode, count}` with `mode` = `manual` (1 spin, random.org) or `auto` (1 to 10,000 spins, Python) |
| GET | `/api/configurations/<id>/analysis` | Actual vs. theoretical values; optional `?source=random.org` or `?source=python` |

Invalid input returns `400` with `{"error": "..."}`, an unknown configuration
`404`.

Autospin with delay is a loop in the frontend that calls `/api/spins` with
`mode=auto, count=1`. The mass simulation calls `/api/spins` with up to
10,000 spins per request and repeats the call until the requested number is
reached, so no request runs into Gunicorn's timeout of 30 seconds.

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
    loop one request per reel (0..length-1)
        B->>R: GET /integers/
        R-->>B: number
    end
    opt any request fails (error, timeout 3 s, quota)
        B->>B: draw all 3 stop positions with Python (secrets)
    end
    B->>B: game.spin(): symbols at stop positions, evaluate paytable
    B->>D: INSERT spin (incl. rng_source)
    B-->>F: symbols, payout, rng_source
    F-->>U: show emoji and payout
```

## Theory and practice: one evaluation function

The theoretical values and the analysis both reuse `game.evaluate()`, the
function that decides the payout of a spin (decisions 0012 and 0018). The
amount of work in Python is constant: at most 6 x 6 x 6 = 216 symbol
combinations, independent of the reel length and of the number of spins.

```mermaid
flowchart TB
    subgraph theory["Theoretical values: game.theoretical_stats()"]
        strips["Reel strips"] --> counts["Count symbols per reel"]
        counts --> combos["All symbol combinations<br/>(max. 216), weight =<br/>product of counts"]
    end
    subgraph practice["Analysis: game.analyse()"]
        spins[("spins table<br/>any number of rows")] --> group["SQL: GROUP BY<br/>symbol_1, symbol_2, symbol_3"]
        group --> groups["Max. 216 groups<br/>with number of spins"]
    end
    combos --> evaluate["game.evaluate(symbols, paytable)<br/>same function as when playing"]
    groups --> evaluate
    evaluate --> result["Per rule: probability vs. actual share<br/>RTP, hit frequency<br/>95 % expected range"]
```

Expected range: theoretical value +/- 1.96 standard errors. Standard error of
a frequency: `sqrt(p * (1 - p) / n)`; of the RTP: `sigma / sqrt(n)`, with the
standard deviation `sigma` of the payout per spin calculated exactly from the
rule probabilities.
