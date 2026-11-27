"""Zero-cost captions: written by code from templates, no API call.

First line is always the fixed, correct title (name + dates, or numeral + card
+ meaning). The second part comes from a rotating set of templates filled with
data about the subject, so captions stay varied across thousands of posts.
"""
import random

SIGN_DATA = {
    "aries": (["bold", "direct", "fearless", "first to begin"], "I trust the fire that gets me started.", "What would you start today if you knew you couldn't fail?"),
    "taurus": (["steady", "sensual", "loyal", "patient"], "I am allowed to slow down and enjoy what I have built.", "What small comfort makes you feel truly safe?"),
    "gemini": (["curious", "quick", "playful", "endlessly talkative"], "My curiosity is a compass, not a distraction.", "Which idea have you not been able to stop thinking about?"),
    "cancer": (["tender", "intuitive", "protective", "deeply caring"], "My softness is a strength I no longer hide.", "Who makes you feel at home, and when did you last tell them?"),
    "leo": (["radiant", "generous", "warm", "brave of heart"], "I am allowed to take up space and shine.", "When did you last let yourself be truly seen?"),
    "virgo": (["thoughtful", "precise", "devoted", "quietly wise"], "Done with care is better than done perfectly.", "What would change if you were as gentle with yourself as with others?"),
    "libra": (["graceful", "fair", "romantic", "a lover of beauty"], "I choose peace that does not cost me my voice.", "Where in your life are you ready to restore balance?"),
    "scorpio": (["intense", "magnetic", "loyal", "unafraid of the deep"], "I let go of what no longer deserves my energy.", "What truth are you finally ready to look at?"),
    "sagittarius": (["free", "optimistic", "adventurous", "always seeking meaning"], "Every horizon I chase brings me closer to myself.", "Where would you go tomorrow if nothing held you back?"),
    "capricorn": (["ambitious", "patient", "grounded", "built to last"], "I build slowly, and what I build stays.", "What are you building that your future self will thank you for?"),
    "aquarius": (["original", "visionary", "independent", "ahead of their time"], "My difference is exactly what the world needs.", "Which part of you did you stop hiding this year?"),
    "pisces": (["dreamy", "empathic", "creative", "guided by intuition"], "My dreams are messages worth listening to.", "What did your last dream try to tell you?"),
}

CONSTELLATION_LINES = {
    "orion": "the great hunter of winter skies, three bright stars at his belt",
    "ursa_major": "the great bear that has guided travellers home for thousands of years",
    "cassiopeia": "the queen on her throne, a bright W above the northern sky",
    "lyra": "the lyre of Orpheus, whose music could soften stone",
    "cygnus": "the swan flying along the Milky Way with open wings",
    "andromeda": "the princess chained to the rocks, and the galaxy that bears her name",
    "perseus": "the hero who came back from the impossible",
    "pegasus": "the winged horse, its great square marking autumn nights",
    "corona_borealis": "the crown of Ariadne, a small half circle of stars",
    "ursa_minor": "the little bear holding Polaris, the star that does not move",
    "draco": "the dragon coiled around the pole, guardian of the golden apples",
}

TEMPLATES = {
    "sign": [
        "{name} energy: {t0}, {t1} and {t2}.",
        "A {element} sign ruled by {ruler}. {T1}, {t2}, {t3}.",
        "{name} affirmation: “{affirm}”",
        "Journal prompt for {name} energy: {prompt}",
        "If you are a {name}, this one is yours. Save it for your season.",
        "To every {name}: you are {t0} and {t3}. Never let anyone dim that.",
        "{name} in three words: {t0}, {t1}, {t2}.",
    ],
    "tarot": [
        "Keywords: {meaning}.",
        "If this card found you today, read it as a sign of {k0}.",
        "Journal prompt: where in your life are you ready for {k0}?",
        "{name} reminds you that {k1} is allowed.",
        "Pull this card and breathe. {K0}, {k1}, {k2}.",
        "Affirmation from {name}: “I welcome {k0} into my life.”",
    ],
    "constellation": [
        "{name}: {line}.",
        "Look up tonight and find {name}, {line}.",
        "Make a wish on {name}, {line}.",
    ],
    "moon": [
        "{name}: a time for {meaning}.",
        "Under the {name}, give your energy to {k0}.",
        "{name} journal prompt: what does {k0} look like for you right now?",
        "Small {name} ritual: light a candle and write one line about {k0}.",
    ],
    "element": [
        "{name}: {meaning}. The {name} signs are {signs}.",
        "How does {name} live in you? {K0}, {k1}, {k2}.",
        "A {name} ritual for today: make room for {k0}.",
    ],
    "planet": [
        "{name} rules {meaning}.",
        "Affirmation for {name} energy: “I honour my {k0}.”",
        "Journal prompt: where is {name} asking for your {k0}?",
    ],
}

MORE = {
    "sign": [
        "Born between {dates}? Then you know: {t0} first, {t1} always.",
        "The {name} way of loving: {t2}, {t3}, all in.",
        "What the stars gave {name}: a heart that is {t0} and a mind that is {t1}.",
        "Dear {name}, your {element} nature is not too much. It is exactly enough.",
        "{name} season is a reminder to be {t0}, even for a day.",
        "A soft note for {name}: {prompt}",
        "Repeat after me, {name}: \u201c{affirm}\u201d",
    ],
    "tarot": [
        "Card of the moment: {name}. Let it ask you about {k1}.",
        "When {name} appears, it rarely whispers. It speaks of {k0} and {k2}.",
        "Today's card carries three gifts: {k0}, {k1} and {k2}.",
        "Sit with {name} for a minute. What does {k0} mean for you right now?",
        "Your sign to stop waiting: {name}, the card of {k0}.",
    ],
    "constellation": [
        "Ancient sailors read {name} like a map: {line}.",
        "Some stars have been telling the same story for millennia. {name}: {line}.",
        "Tonight's star story is {name}, {line}.",
    ],
    "moon": [
        "The {name} is not asking you to rush. It asks for {k1}.",
        "Three words for the {name}: {k0}, {k1}, {k2}.",
        "Let the {name} remind you that every phase has a purpose.",
    ],
    "element": [
        "{K0} is your {name} gift. Use it gently.",
        "Every chart holds some {name}. Where is yours?",
    ],
    "planet": [
        "Where {name} lives in your chart, {k0} wants attention.",
        "{name}, keeper of {k0} and {k1}.",
        "Three gifts of {name}: {k0}, {k1}, {k2}.",
    ],
}
for _k, _v in MORE.items():
    TEMPLATES[_k].extend(_v)

CLOSERS = [
    "", "", "", "",
    "Save this for the day you need it.",
    "Keep this one close.",
    "Send it to someone who needs the reminder.",
    "Breathe in, read it twice.",
    "A little magic for your feed.",
    "Let this one stay with you tonight.",
    "Screenshot it, set it as your wallpaper.",
    "Read it, then close your eyes for three breaths.",
    "Your daily dose of stardust.",
    "Written in the stars, delivered to you.",
    "Pause here for a moment.",
    "Hold onto this energy today.",
]

REPLY_INTROS = [
    "If this one spoke to you, this is where I would start.",
    "For the nights you want to go deeper with this energy:",
    "Made for exactly this kind of reflection:",
    "Keep this feeling going on paper:",
    "If you want a ritual to go with it:",
    "A little something to carry this energy with you:",
]


def _kw(meaning):
    return [k.strip() for k in meaning.split(",") if k.strip()]


def first_line(s):
    if s["kind"] == "sign":
        return f"{s['name']} · {s['subtitle'].title()}"
    if s["kind"] == "tarot":
        return f"{s['numeral']} · {s['name'].title()}"
    if s["kind"] == "planet":
        return s["name"].title()
    return s["name"].title()


def body(s, rng):
    kind = s["kind"]
    tpl = rng.choice(TEMPLATES[kind])
    v = {"name": s["name"].title() if kind != "sign" else s["name"]}
    if kind == "sign":
        traits, affirm, prompt = SIGN_DATA[s["key"].split(":")[1]]
        t = traits[:]
        rng.shuffle(t)
        v.update(dates=s["subtitle"].title(), t0=t[0], t1=t[1], t2=t[2], t3=t[3], T1=t[1].capitalize(), element=s["element"].lower(),
                 ruler=s["ruler"], affirm=affirm, prompt=prompt)
    elif kind == "constellation":
        v["line"] = CONSTELLATION_LINES.get(s["constellation"], "a pattern of stars older than every story")
    else:
        k = _kw(s["meaning"])
        while len(k) < 3:
            k.append(k[-1])
        v.update(meaning=s["meaning"], k0=k[0], k1=k[1], k2=k[2], K0=k[0].capitalize(), signs=s.get("subtitle", "").title())
    if kind == "element":
        v["signs"] = s["subtitle"].title()
    return tpl.format(**v)


def make_caption(s, palette, rng=None):
    rng = rng or random.Random()
    n = rng.choice([1, 2, 2, 3])
    em = rng.sample(palette, n)
    text = body(s, rng)
    closer = rng.choice(CLOSERS)
    if closer:
        text = f"{text}\n\n{closer}"
    style = rng.randrange(3)
    if style == 0:
        text = f"{text} {' '.join(em)}"
    elif style == 1:
        text = f"{em[0]} {text}" + (f" {' '.join(em[1:])}" if n > 1 else "")
    else:
        text = f"{text}\n\n{''.join(em)}"
    return f"{first_line(s)}\n\n{text}"


def make_reply_intro(palette, rng=None):
    rng = rng or random.Random()
    intro = rng.choice(REPLY_INTROS)
    return f"{intro} {rng.choice(palette)}" if rng.random() < 0.6 else intro
