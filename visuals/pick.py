"""Choose the next subject. Never runs out: no repeat within `avoid_last` posts,
and the sign whose calendar season it is comes up more often."""
import random

from . import catalog


def pick_subject(history, today=None, avoid_last=30, rng=None):
    rng = rng or random.Random()
    recent = set(history[-avoid_last:])
    season = catalog.sign_in_season(today)
    pool, weights = [], []
    for s in catalog.all_subjects():
        if s["key"] in recent:
            continue
        w = {"sign": 1.5, "tarot": 1.3}.get(s["kind"], 1.0)
        if s["key"] == season:
            w *= 6
        pool.append(s)
        weights.append(w)
    if not pool:
        pool, weights = catalog.all_subjects(), None
    return rng.choices(pool, weights=weights, k=1)[0]
