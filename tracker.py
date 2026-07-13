#!/usr/bin/env python3
"""
Kava delegation tracker — hourly append-only CSV log.
Columns: timestamp_utc, delegator_count, total_bonded_ukava,
         self_delegation_ukava, external_delegated_ukava, rank, active_set_size
"""
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path.home() / "delegation-metrics"
HISTORY = BASE / "history.csv"
KAVA = "/home/cosmos/go/bin/kava"
NODE = "tcp://localhost:26657"
VALOPER = "kavavaloper1hymhtrelxqnf7p6ua06eh69u4kc36hq2sf9vtu"
VOTER = "kava1hymhtrelxqnf7p6ua06eh69u4kc36hq2allynt"

COLUMNS = [
    "timestamp_utc",
    "delegator_count",
    "total_bonded_ukava",
    "self_delegation_ukava",
    "external_delegated_ukava",
    "rank",
    "active_set_size",
]

def kquery(args):
    r = subprocess.run(
        [KAVA, "query", *args, "--node", NODE, "-o", "json"],
        capture_output=True, text=True, timeout=45,
    )
    if r.returncode != 0:
        raise RuntimeError(f"kava query failed: {' '.join(args)} :: {r.stderr.strip()}")
    return json.loads(r.stdout)

def get_delegator_count():
    count = 0
    key = None
    while True:
        args = ["staking", "delegations-to", VALOPER, "--limit", "500"]
        if key:
            args += ["--page-key", key]
        data = kquery(args)
        count += len(data.get("delegation_responses", []))
        key = (data.get("pagination") or {}).get("next_key")
        if not key:
            break
    return count

def get_validator_bonded():
    v = kquery(["staking", "validator", VALOPER])
    return int(v["tokens"])

def get_self_delegation():
    d = kquery(["staking", "delegation", VOTER, VALOPER])
    return int(d["balance"]["amount"])

def get_rank_and_setsize():
    data = kquery(["staking", "validators", "--limit", "500"])
    bonded = [v for v in data["validators"] if v.get("status") == "BOND_STATUS_BONDED"]
    bonded.sort(key=lambda v: int(v["tokens"]), reverse=True)
    rank = next(
        (i + 1 for i, v in enumerate(bonded) if v["operator_address"] == VALOPER),
        None,
    )
    return rank, len(bonded)

def main():
    ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    delegator_count = get_delegator_count()
    total_bonded = get_validator_bonded()
    self_del = get_self_delegation()
    external = total_bonded - self_del
    rank, setsize = get_rank_and_setsize()

    row = {
        "timestamp_utc": ts,
        "delegator_count": delegator_count,
        "total_bonded_ukava": total_bonded,
        "self_delegation_ukava": self_del,
        "external_delegated_ukava": external,
        "rank": rank if rank is not None else "",
        "active_set_size": setsize,
    }

    new_file = not HISTORY.exists()
    with HISTORY.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        if new_file:
            w.writeheader()
        w.writerow(row)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sys.stderr.write(f"delegation-tracker error: {e}\n")
        sys.exit(1)
