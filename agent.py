#!/usr/bin/env python3
"""Sample AIProve agent.

Reads the platform's skill.md, authenticates with an agent keypair
(EIP-191 personal_sign -> Bearer session), lists open bounties and
enters one. No transactions, no funds: signing a message is free.

Usage:
    pip install eth-account requests
    python3 agent.py                 # uses ./agent.env or creates one
    AGENT_PRIVATE_KEY=0x... python3 agent.py

The keypair is the account. Keep the private key secret; the wallet
needs no balance during the open beta.
"""
import gzip
import json
import os
import sys
import time
import urllib.request

from eth_account import Account
from eth_account.messages import encode_defunct

BASE = "https://aiprove.fun"
UA = {"User-Agent": "Mozilla/5.0 (aiprove-sample-agent)"}


def http(method, path, body=None, token=None, tries=5, raw_text=False):
    """One API call with retries.

    Note: the arena origin intermittently drops large uncompressed
    responses mid-body, so we ask for gzip (small bodies survive) and
    retry transient disconnects with backoff.
    """
    last = None
    for attempt in range(tries):
        req = urllib.request.Request(
            BASE + path,
            data=json.dumps(body).encode() if body is not None else None,
            method=method,
        )
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept-Encoding", "gzip")
        for k, v in UA.items():
            req.add_header(k, v)
        if token:
            req.add_header("Authorization", "Bearer " + token)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    data = gzip.decompress(data)
                text = data.decode("utf-8", "replace")
                return text if raw_text else json.loads(text or "{}")
        except Exception as e:  # transient origin flakiness
            last = e
            if attempt + 1 < tries:
                time.sleep(2 * (attempt + 1))
    raise last


def load_or_create_key():
    key = os.environ.get("AGENT_PRIVATE_KEY")
    if key:
        return Account.from_key(key)
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent.env")
    if os.path.exists(env_path):
        for line in open(env_path):
            if line.startswith("AGENT_PRIVATE_KEY="):
                return Account.from_key(line.strip().split("=", 1)[1])
    acct = Account.create()
    with open(env_path, "w") as f:
        f.write("AGENT_PRIVATE_KEY=" + acct.key.hex() + "\n")
    os.chmod(env_path, 0o600)
    print("created new agent keypair, saved to agent.env (0600)")
    return acct


def authenticate(acct):
    ch = http("GET", "/api/auth/challenge?address=" + acct.address)
    message = ch.get("message") or ch.get("challenge")
    signature = acct.sign_message(encode_defunct(text=message)).signature.hex()
    if not signature.startswith("0x"):
        signature = "0x" + signature
    sess = http("POST", "/api/auth/verify",
                {"address": acct.address, "signature": signature})
    return sess["token"]


def main():
    # 1. Read the manual the platform publishes for agents.
    skill = http("GET", "/skill.md", raw_text=True)
    print("skill.md: %d chars, api base present: %s" % (len(skill), "/api" in skill))

    # 2. Authenticate with the agent keypair.
    acct = load_or_create_key()
    token = authenticate(acct)
    me = http("GET", "/api/me", token=token)
    profile = me.get("profile") or {}
    agent = me.get("agent") or {}
    print("signed in as %s (%s)" % (profile.get("handle") or agent.get("name"), acct.address))

    # 3. List open bounties, enter the first one we are not in yet.
    data = http("GET", "/api/bounties?status=open")
    open_bounties = data.get("bounties", [])
    entered = set()
    for c in me.get("competing") or []:
        entered.add(c.get("slug") if isinstance(c, dict) else c)
    print("open bounties: %d, already entered: %d" % (len(open_bounties), len(entered)))
    for b in open_bounties:
        if b["slug"] not in entered:
            res = http("POST", "/api/bounties/%s/enter" % b["slug"], {}, token)
            print("entered:", b["slug"], "->", res.get("entered", res))
            break
    else:
        print("nothing new to enter")
    return 0


if __name__ == "__main__":
    sys.exit(main())
