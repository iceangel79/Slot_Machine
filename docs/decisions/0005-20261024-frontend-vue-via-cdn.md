# Frontend: Vue 3 via CDN

Date: 2026-10-24

## Status

Accepted

## Context

The frontend consists of three views: play (shows three symbols and the
payout), configure (edit reel strips and paytable, see probabilities and RTP
update while editing) and analyse (tables that change with the selected
configuration). Frontend technologies without a build step are preferred.

## Options Considered

 * Option 1: Plain JavaScript. Nothing new to learn, but every change of the
   displayed data has to be written to the page by hand, which becomes
   cluttered in the configuration view.
 * Option 2: Vue 3 included via CDN. One script tag, no build tools. Reactive:
   the display updates automatically when the data changes. Recommended by
   the lecturers.
 * Option 3: HTMX or Alpine.js. Lightweight, but less suited to the
   interactive configuration editor.
 * Option 4: Vue with build tools, React or Angular. Too complex for the scope.

## Decision

Option 2, Vue 3 via CDN, without build tools.

## Reasons

Starting with plain JavaScript would be simpler, but the project as a whole is
simpler with Vue, because the configuration and analysis views are highly
dynamic. No npm or build step is needed.

## Consequences

 * Easier: Dynamic views with little code; no frontend tooling.
 * Harder: Basic Vue concepts (reactive data, templates) must be learned.
 * Rule: All calculations (probabilities, RTP) are done in the backend. The
   frontend only displays results, so the logic exists once and is tested in
   Python.
