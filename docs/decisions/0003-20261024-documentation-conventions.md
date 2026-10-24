# Documentation Language and Decision Record Naming

Date: 2026-10-24

## Status

Accepted

## Context

The project produces several kinds of written artefacts next to the source
code: a development diary, decision records, the README, the agent
instructions in `AGENTS.md` and inline documentation in the code itself.

Two questions came up while writing the first records:

 * Which language should be used for which artefact? The team language is
   German, the module exam is written in German, but the technical vocabulary
   of the stack (deployment, container, commit, build) is English and most
   reference material is English as well.
 * How should decision records be named? `AGENTS.md` asked for
   `0001-framework-choice.md`, while the records actually created follow a
   different pattern that also carries the date.

Without an explicit rule, both the team members and the AI agents used in this
project produce inconsistent results, because an agent has no way of knowing
the intended convention.

## Options Considered

 * Option 1: Everything in English. Consistent and close to the technical
   vocabulary, but the diary is a reflective text and reflection is more
   precise in the team's own language.
 * Option 2: Everything in German. Natural for the team, but forces awkward
   translations of established technical terms and drifts into mixed language.
 * Option 3: Language chosen per artefact type and written down as a rule:
   German for the reflective diary, English for everything else.
 * Option 4 (naming): Keep the template scheme `NNNN-short-title.md`, or adopt
   the scheme already used in practice, `NNNN-YYYYMMDD-short-title.md`.

## Decision

The team chose Option 3 for the language question and the dated scheme
`NNNN-YYYYMMDD-short-title.md` for decision record file names.

Concretely:

 * `docs/diary.md` is written in German, using Swiss spelling (`ss`, never
   `ß`).
 * All other documentation, decision records, code, comments, docstrings and
   commit messages are written in English.
 * Languages are not mixed within a single file. Established English technical
   terms may remain as-is inside German text where no natural German
   equivalent exists.
 * Decision records live in `docs/decisions` and are named
   `NNNN-YYYYMMDD-short-title.md`, with continuous numbering and lowercase
   words separated by hyphens.
 * Dates inside decision records use the ISO format `YYYY-MM-DD`.

Both rules are recorded in `AGENTS.md` so that AI agents follow them without
being reminded in every prompt.

## Reasons

The diary is the place where the team reflects on collaboration and on its own
learning process. That is done most precisely in the team's own language, and
it feeds directly into the written reflection of the module, which is also in
German.

Everything else is technical and surrounded by English vocabulary anyway.
Writing it in German would either require unusual translations or produce
mixed-language sentences that are harder to read than either language alone.

The dated file name makes the chronology of decisions visible in a directory
listing without opening the files, which is useful when the records are used
as evidence during the presentation and the reflection. The sequence number is
kept so that records can still be referenced unambiguously as "decision 0003".

## Consequences

 * Easier: Both team members and AI agents have an unambiguous rule, so
   artefacts stay consistent without repeated discussion.
 * Easier: The chronological order of decisions is visible directly in
   `docs/decisions`.
 * Harder: Team members switch languages depending on which file they are
   editing.
 * Follow-up: `AGENTS.md` receives a `## Language` section and its decision
   record naming rule is updated to the dated scheme.
 * Follow-up: Existing records are aligned with the convention. This includes
   renaming `0001-20261022-docker_vs_redner.md` to
   `0001-20261022-docker-vs-render.md` and changing the date in that record to
   the ISO format.
 * Risk: Agents may still drift between languages in longer sessions. The rule
   in `AGENTS.md` reduces this but does not guarantee it, so language
   consistency is checked during review.
