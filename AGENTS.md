## Technology stack

This project represents a web application with a backend and a frontend part.
The backend is to be kept completely in Python. The frontend stack can be chosen
freely.

 * We use `uv` for any Python related tasks
 * Chosen stack: Flask (Gunicorn), Vue 3 via CDN, PostgreSQL on Neon with
   plain SQL (`psycopg`), random.org as external web service. See
   `README.md` and decisions 0004 to 0010.

## Language

 * All code, comments, docstrings, commit messages, decision records and
   general documentation are written in English.
 * The development diary in `docs/diary.md` is written in German. Keep new
   entries in German as well.
 * Swiss spelling conventions apply to all German text: use `ss` instead of
   `ß` and avoid Germany-specific wording.
 * Do not mix languages within a single file. Established English technical
   terms (deployment, commit, container) may stay as-is inside German text
   where no natural German equivalent exists.
 * When editing an existing file, keep its current language. Only switch
   languages when the developers explicitly ask for it.

## Files and directories

 * Check `docs/directories.md` for the directory structure.
 * The Flask application lives in `src/app/main.py`; Gunicorn starts
   `app.main:app` (decision 0012). Keep the package `app` free of side
   effects on import, so the game logic can be tested without a database.
 * Game logic stays in `src/app/game.py` without Flask and database.
 * The application is deployed as Docker image on Render (decision 0001).

## Design guidelines

This is a project that is to be developed in the course of a master degree in
business informatics. The focus is on exploring and learning about all the parts
involved in running a full web application rather than building a fully
productive, scalable and long-term maintainable application. The created
elements should be easy to understand.

 * When discussing design options, start with the simpler options; for example
   suggest to start with Flask or Starlette rather than Django, suggest vanilla
   JavaScript, HTMX or Alpine.js rather than going straight for full fledged
   solutions like Angular or React. Accept more complex solutions once the
   developers made it clear that they are needed and they understand the
   implications.
 * Prefer frontend technologies that can be used through CDN and don't need any
   frontend build steps.
 * For WSGI/ASGI start with either Gunicorn or Uvicorn depending on the web
   framework used.
 * Document architectural design decisions that were discussed with the
   developers in the folder `docs/decisions`. Use a new file for every
   decision, named `NNNN-YYYYMMDD-short-title.md` with continuous numbering,
   for example `0003-20261101-database-choice.md`.

## Educational collaboration

This template is used for learning software development, not only for producing
code. When students ask an agent to add a feature, choose a technology, or make
an architectural change, the agent should first help them reason about the
decision before implementing it.

Reusable guidance for this behavior is stored as the generic agent skill
`.agents/skills/challenge-development-decisions`. Agents that support skills
should use that skill for feature requests, technology choices, architecture
placement questions, and decision records in this project.

Decision records for this project belong in `docs/decisions` and should be
based on `docs/decision-template.md`. They describe the decision, not who made
it.

