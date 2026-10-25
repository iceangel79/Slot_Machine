-- Database schema. Executed at every application start (decision 0010).
-- CREATE TABLE IF NOT EXISTS never changes an existing table; changes to
-- existing tables must be done by hand (ALTER TABLE).

CREATE TABLE IF NOT EXISTS configurations (
    id          SERIAL PRIMARY KEY,
    name        TEXT        NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    reel_strips JSONB       NOT NULL,
    paytable    JSONB       NOT NULL
);

CREATE TABLE IF NOT EXISTS spins (
    id               SERIAL PRIMARY KEY,
    configuration_id INTEGER     NOT NULL REFERENCES configurations (id),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    symbol_1         TEXT        NOT NULL,
    symbol_2         TEXT        NOT NULL,
    symbol_3         TEXT        NOT NULL,
    bet              INTEGER     NOT NULL,
    payout           INTEGER     NOT NULL,
    rng_source       TEXT        NOT NULL CHECK (rng_source IN ('random.org', 'python'))
);
