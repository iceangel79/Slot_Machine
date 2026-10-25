# Slot Machine Simulator

A web application that simulates a classic three-reel Las Vegas slot machine with a freely configurable setup (symbols, reel strips, and paytable combinations). The application provides an interactive game interface to execute single manual spins or automated spins, with every spin recorded in a persistent database. An integrated analysis dashboard evaluates collected spin data, comparing configured theoretical probabilities and Return to Player (RTP) ratios against actual empirical hit rates and payout statistics.

---

## Table of Contents

- [Features](#features)
- [Architecture & Tech Stack](#architecture--tech-stack)
- [Get Started](#get-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Configuration](#environment-configuration)
  - [Running Locally](#running-locally)
- [Local Deployment with Docker](#local-deployment-with-docker)
- [Understanding the Architecture & Concepts](#understanding-the-architecture--concepts)
  - [Domain Model & Mechanics](#domain-model--mechanics)
  - [Immutable, Versioned Configurations](#immutable-versioned-configurations)
  - [Dual Random Number Generation (RNG) Strategy](#dual-random-number-generation-rng-strategy)
  - [Separation of Concerns](#separation-of-concerns)
- [Architecture Decision Records (ADRs)](#architecture-decision-records-adrs)
- [Testing & Code Quality](#testing--code-quality)

---

## Features

- **Interactive Play (F1):** Run manual single spins with visual display of reel stops and calculated payouts. Each spin records the exact outcome, bet, payout, and RNG source.
- **Autospin & Mass Simulation (F2):** Run continuous spins with visual feedback or execute high-volume batch simulations directly in the backend to rapidly gather empirical data.
- **Dynamic Configuration (F3):** Freely define reel strips (including explicit blanks) and paytable winning combinations (three-of-a-kind and cherry counts). Live theoretical odds, hit frequency, and RTP are calculated and previewed before saving.
- **Statistical Analysis (F4):** Inspect stored spin results per configuration, contrasting theoretical expectations with actual outcomes (total bet/payout, RTP, hit frequency, and hit rates per paytable rule).

---

## Architecture & Tech Stack

| Layer | Technology | Details |
|---|---|---|
| **Backend** | Python 3.13+ / Flask | Lightweight REST API and static file server; game logic kept in a framework-independent core module. |
| **WSGI Server** | Gunicorn / Waitress | Gunicorn for production/Linux; Waitress for local Windows execution. |
| **Frontend** | Vue 3 (via CDN) | Reactive Single-Page Application loaded without a build step or Node.js tooling. |
| **Database** | PostgreSQL on Neon | Managed serverless PostgreSQL persistent across deployments and app restarts. |
| **External Service** | random.org API | Atmospheric noise RNG for single manual spins, with graceful local fallback. |
| **Package Manager** | `uv` | Fast, deterministic Python package management and virtual environment tool. |
| **Containerization** | Docker | Container runtime using `python:3.13-slim` base image. |
| **Hosting & CI/CD** | Render.com | Automated cloud deployment directly connected to GitHub repository commits. |

---

## Get Started

### Prerequisites

- **Python:** Version 3.13 or newer
- **uv:** Fast Python package manager ([Astral uv documentation](https://docs.astral.sh/uv/))
- **PostgreSQL Database:** Connection string to a PostgreSQL instance (e.g., free tier on [Neon](https://neon.tech))

### Installation

Clone the repository and set up the virtual environment with all required dependencies using `uv`:

```bash
git clone https://github.com/iceangel79/Slot_Machine.git
cd Slot_Machine
uv sync
```

### Environment Configuration

The application requires a PostgreSQL database connection string. Create a local `.env` file in the project root (never committed to git):

```env
DATABASE_URL=postgresql://<user>:<password>@<host>/<dbname>?sslmode=require
```

### Running Locally

Activate the environment and launch the WSGI server:

- **On Linux / macOS:**
  ```bash
  uv run gunicorn --bind 127.0.0.1:8000 app.main:app
  ```

- **On Windows:**
  ```powershell
  uv run waitress-serve --port=8000 app.main:app
  ```

Open your browser and navigate to `http://localhost:8000`.

---

## Local Deployment with Docker

To build and test the application in an isolated container environment matching production:

1. **Build the Docker image:**
   ```bash
   docker build -t slot-machine .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 -e DATABASE_URL="postgresql://<user>:<password>@<host>/<dbname>?sslmode=require" slot-machine
   ```

3. Open `http://localhost:8000` in your web browser.

---

## Understanding the Architecture & Concepts

### Domain Model & Mechanics

The game simulates a classic mechanical three-reel Las Vegas slot machine with a single center payline:
- **Symbols:** Represented by canonical codes in the backend (`CHERRY`, `LEMON`, `BELL`, `BAR`, `SEVEN`, `BLANK`). Blanks are treated as physical stops on the reel strips.
- **Reel Strips:** Each of the 3 reels has an ordered sequence of symbols. Symbol frequency on the strip directly determines stop probability.
- **Payline & Paytable:** The center row forms the evaluation line. Winning conditions include three-of-a-kind (e.g., `SEVEN SEVEN SEVEN`) and cherry-count combinations (e.g., 1 or 2 cherries anywhere on the payline).
- **RTP & Hit Frequency:** Return to Player (expected payout per unit wagered) and hit frequency are calculated analytically from the reel strips and paytable before spins take place.

### Immutable, Versioned Configurations

To ensure absolute statistical integrity, configurations are **immutable**:
- Whenever a user edits reel strips or paytables, the backend creates a new configuration entry (`configuration_id`).
- Every spin references its specific `configuration_id`.
- This ensures that historical spins are always evaluated against the exact mathematical odds under which they were generated, even after subsequent rules or reel strips change.

### Dual Random Number Generation (RNG) Strategy

The simulator implements a hybrid RNG architecture balancing true randomness with API quotas:
1. **Single Manual Spins:** Query the external [random.org](https://www.random.org) API for genuine atmospheric noise randomness.
2. **Resilient Fallback:** If `random.org` encounters network latency, rate limits, or downtime, the backend automatically falls back to Python's cryptographically secure pseudo-random number generator (`secrets` / `os.urandom`). The source is recorded per spin (`rng_source`).
3. **Autospin & Mass Simulation:** High-volume automated spins exclusively use Python's internal generator to prevent quota exhaustion and provide high throughput.

### Separation of Concerns

- **Decoupled Core Logic:** All slot calculation rules (reel stopping, payline evaluation, theoretical probability formulas, RTP calculation) reside in a pure Python domain module, fully decoupled from Flask and tested with unit tests.
- **API-Driven Presentation:** The backend operates exclusively with canonical symbol codes. The frontend maps codes to visual representations (emoji for the MVP). This allows alternative frontends to connect without modifying backend or database schemas.
- **Zero-Build Frontend:** Vue 3 is included via CDN directly in static templates, providing dynamic reactivity for configuration updates and live statistics without requiring Node.js build tooling.

---

## Architecture Decision Records (ADRs)

Key architectural and technological choices are documented in `docs/decisions/`:

- [ADR 0001: Docker vs. Render.com Deployment](docs/decisions/0001-20261022-docker_vs_render.md)
- [ADR 0002: Base Tech-Stack Selection](docs/decisions/0002-20261024-tech.md)
- [ADR 0003: Documentation Language & Decision Record Conventions](docs/decisions/0003-20261024-documentation-conventions.md)
- [ADR 0004: Backend Framework: Flask](docs/decisions/0004-20261024-backend-framework-flask.md)
- [ADR 0005: Frontend Architecture: Vue 3 via CDN](docs/decisions/0005-20261024-frontend-vue-via-cdn.md)
- [ADR 0006: Database Selection: PostgreSQL on Neon](docs/decisions/0006-20261024-database-postgres-on-neon.md)
- [ADR 0007: Immutable, Versioned Configurations](docs/decisions/0007-20261024-immutable-versioned-configurations.md)
- [ADR 0008: Random Number Sources: random.org & Python](docs/decisions/0008-20261024-random-number-sources.md)
- [ADR 0009: Symbol Codes & Frontend Emoji Representation](docs/decisions/0009-20261024-symbol-codes-and-emoji-display.md)

---

## Testing & Code Quality

- **Test Suite:** Executed with `pytest` and test coverage reporting via `pytest-cov`:
  ```bash
  uv run pytest
  ```
- **Linting & Formatting:** Managed with `ruff`:
  ```bash
  uv run ruff check
  uv run ruff format
  ```

