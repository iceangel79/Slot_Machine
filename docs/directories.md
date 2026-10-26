# Directory Structure

What each directory and file of the project is for.

## Directories

 * `.github/workflows` contains the CI pipeline `ci.yml` (GitHub Actions,
   decision 0011): `ruff check` and `pytest` on every push and pull request.
 * `.agents/skills` contains a reusable skill for coding agents (from the
   course template): agents challenge feature requests and technology choices
   before implementing them.
 * `.vscode` contains settings and tasks for VS Code (e.g. `uv sync` when the
   project is opened).
 * `.venv` contains the locally installed libraries, created by `uv sync`.
   Not versioned.
 * `docs` contains the project documentation:
    * `requirements.md`: goal, domain concepts, functional and non-functional
      requirements.
    * `architecture.md`: components, deployment, data model, API and
      sequences as Mermaid diagrams.
    * `decisions/`: one decision record per important decision, named
      `NNNN-YYYYMMDD-short-title.md` (decision 0003), based on
      `decision-template.md`.
    * `diary.md`: development diary (German).
 * `src/app` contains the Python backend:
    * `main.py`: Flask application with the JSON API; serves the frontend.
      Creates the tables and the default configuration at startup.
    * `game.py`: game logic without Flask and database (spin, paytable,
      theoretical values, analysis).
    * `rng.py`: random sources (random.org with fallback, Python).
    * `db.py`: database access with plain SQL.
    * `schema.sql`: tables and index.
    * `__init__.py`: marks the package; intentionally without side effects,
      so the game logic can be tested without a database (decision 0012).
 * `src/app/static` contains the frontend: `index.html` (play),
   `configure.html`, `analyse.html`, `common.js` (emoji table shared by all
   pages) and `style.css`.
 * `tests` contains the pytest tests: `test_game.py` (game logic and random
   sources, no database), `test_api.py` (endpoints, test database) and
   `conftest.py` (selects the test database, decision 0015).

## Files in the root directory

 * `README.md`: overview, installation, tests and deployment.
 * `AGENTS.md`: instructions for coding agents (language, conventions,
   design guidelines).
 * `pyproject.toml` and `uv.lock`: project description and dependencies.
   Packages are added and removed with `uv add ...` and `uv remove ...`.
 * `Dockerfile`: container image, built and deployed by Render
   (decision 0001).
 * `.python-version`: Python version used by `uv`.
 * `.gitignore`: files that are never versioned, in particular `.env` with
   the connection strings.
 * `.env` (local only, not versioned): `DATABASE_URL` and
   `TEST_DATABASE_URL`.
