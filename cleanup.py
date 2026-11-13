#!/usr/bin/env python3
"""One-off cleanup: delete the account's old posts and its replies to others.

DELETION IS PERMANENT. Without CONFIRM=CANCELLA the script only lists what
it would delete. Posts published by the bot (state/posted.json) are kept.

Env vars:
  THREADS_ACCESS_TOKEN  required; the token needs the threads_delete permission
  CONFIRM=CANCELLA      actually delete (anything else = list only)
  INCLUDE_REPLIES=1     also delete replies written under other people's posts
  MAX_DELETE            max deletions in this run (default 95; Threads caps
                        deletions per 24 hours, so big accounts need several days)
"""
import json
import os
import sys
import time
from pathlib import Path

import requests

HOST = os.environ.get("THREADS_API_HOST", "https://graph.threads.net/v1.0")
USER = os.environ.get("THREADS_USER_ID", "me")
TOKEN = os.environ["THREADS_ACCESS_TOKEN"]
REALLY = os.environ.get("CONFIRM") == "CANCELLA"
INCLUDE_REPLIES = os.environ.get("INCLUDE_REPLIES") == "1"
MAX_DELETE = int(os.environ.get("MAX_DELETE", "95"))
STATE_FILE = Path(__file__).parent / "state" / "posted.json"


def bot_ids():
    if not STATE_FILE.exists():
        return set()
    state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    ids = set()
    for item in state.get("posts", []) + state.get("ghosts", []):
        ids.update(x for x in (item.get("thread_id"), item.get("reply_id")) if x)
    return ids


def fetch_all(edge):
    items, url = [], f"{HOST}/{USER}/{edge}"
    params = {"fields": "id,text,timestamp,permalink", "limit": 100, "access_token": TOKEN}
    while url:
        resp = requests.get(url, params=params, timeout=60)
        body = resp.json()
        if resp.status_code != 200:
            print(f"Could not read /{edge} ({resp.status_code}): {body.get('error', body)}")
            break
        items.extend(body.get("data", []))
        url = body.get("paging", {}).get("next")
        params = None  # the "next" link already carries everything
    return items


def main():
    keep = bot_ids()
    targets = [("post", p) for p in fetch_all("threads")]
    if INCLUDE_REPLIES:
        targets += [("reply", r) for r in fetch_all("replies")]
    seen, todo = set(), []
    for kind, item in targets:
        if item["id"] in keep or item["id"] in seen:
            continue
        seen.add(item["id"])
        todo.append((kind, item))

    posts = sum(1 for k, _ in todo if k == "post")
    print(f"Found {posts} posts and {len(todo) - posts} replies to delete ({len(keep)} bot items kept).")
    for kind, item in todo[:40]:
        first_line = (item.get("text") or "[no text]").replace("\n", " ")[:70]
        print(f"  {kind:5} {item.get('timestamp', '')[:10]}  {first_line}")
    if len(todo) > 40:
        print(f"  ... and {len(todo) - 40} more")

    if not REALLY:
        print("\nList only: nothing was deleted. Run again with the confirmation word to delete.")
        return 0

    deleted = 0
    for kind, item in todo[:MAX_DELETE]:
        resp = requests.delete(f"{HOST}/{item['id']}", params={"access_token": TOKEN}, timeout=60)
        if resp.status_code != 200:
            print(f"Stopped at {item['id']} ({resp.status_code}): {resp.text[:300]}")
            break
        deleted += 1
        time.sleep(2)
    left = len(todo) - deleted
    print(f"\nDeleted {deleted}. Still to delete: {left}." + (" Run again tomorrow." if left else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
