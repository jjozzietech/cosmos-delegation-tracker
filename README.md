# cosmos-delegation-tracker

> **SUPERSEDED (November 2026).** This is the original single-chain version.
> jjozzietech no longer runs or maintains it; it was replaced in production by an
> internal multi-chain version. Kept for reference only.

hourly append-only CSV logger for Cosmos SDK validator delegation metrics.
tracks delegator count, total bonded tokens, self-delegation vs external
delegation, active-set rank, and active-set size over time. one row per
run, so you build a historical time series for free.

built for a Kava validator; chain-agnostic by construction, see
"using on another chain" below.

## requirements

- python3 (stdlib only, no pip packages required)
- the chain's daemon binary available locally, with access to a synced
  node's RPC endpoint

## install

git clone https://github.com/jjozzietech/cosmos-delegation-tracker.git
cd cosmos-delegation-tracker

edit the config constants in tracker.py (see below), then run.

## configure

chain-specific constants are set directly in tracker.py near the top:

    KAVA = "/home/cosmos/go/bin/kava"
    NODE = "tcp://localhost:26657"
    VALOPER = "kavavaloper1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    VOTER = "kava1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

VALOPER is your validator's operator address. VOTER is the account
address holding your self-delegation. both are public on-chain data,
not secrets, but are specific to your validator.

## output

writes to history.csv (gitignored, this is your local data, not
committed). columns:

    timestamp_utc, delegator_count, total_bonded_ukava,
    self_delegation_ukava, external_delegated_ukava, rank,
    active_set_size

denominations follow the chain's base unit (ukava for Kava — adjust
expectations if repointing to a chain with a different base denom).

## run

    python3 tracker.py

test manually first, then cron it hourly:

    crontab -e

add:

    0 * * * * /usr/bin/python3 /home/youruser/delegation-metrics/tracker.py >> /home/youruser/delegation-metrics/cron.log 2>&1

## using on another chain

four-line change in tracker.py:

    KAVA = "/path/to/your/chain-daemon"
    NODE = "tcp://localhost:26657"
    VALOPER = "yourchainvaloper1..."
    VOTER = "yourchain1..."

the query CLI flags used (query staking delegations-to, query staking
validator, query staking delegation, query staking validators) are
standard across Cosmos SDK chains using the staking module, so no
other changes are typically needed. delete or rename history.csv when
switching chains to avoid mixing data series from different chains.

## license

MIT, see LICENSE.
