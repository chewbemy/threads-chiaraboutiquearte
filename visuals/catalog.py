"""Subjects for the animated posts: zodiac signs, Major Arcana, constellations,
moon phases, elements and planets.

The catalogue is finite, but the bot never runs out: every render uses a new
random seed (layout, geometry, motion, accents) and a new caption angle, and the
picker only avoids repeating the same subject too soon.

Constellation shapes are artistic approximations (x right, y down, 0..1).
Coordinates shown on screen are the constellation's approximate centre.
"""
import datetime as _dt

SIGNS = [
    # id, name, glyph, start (m,d), end (m,d), element, ruler, constellation key
    ("aries", "Aries", "♈", (3, 21), (4, 19), "Fire", "Mars", "aries"),
    ("taurus", "Taurus", "♉", (4, 20), (5, 20), "Earth", "Venus", "taurus"),
    ("gemini", "Gemini", "♊", (5, 21), (6, 20), "Air", "Mercury", "gemini"),
    ("cancer", "Cancer", "♋", (6, 21), (7, 22), "Water", "Moon", "cancer"),
    ("leo", "Leo", "♌", (7, 23), (8, 22), "Fire", "Sun", "leo"),
    ("virgo", "Virgo", "♍", (8, 23), (9, 22), "Earth", "Mercury", "virgo"),
    ("libra", "Libra", "♎", (9, 23), (10, 22), "Air", "Venus", "libra"),
    ("scorpio", "Scorpio", "♏", (10, 23), (11, 21), "Water", "Pluto", "scorpius"),
    ("sagittarius", "Sagittarius", "♐", (11, 22), (12, 21), "Fire", "Jupiter", "sagittarius"),
    ("capricorn", "Capricorn", "♑", (12, 22), (1, 19), "Earth", "Saturn", "capricornus"),
    ("aquarius", "Aquarius", "♒", (1, 20), (2, 18), "Air", "Uranus", "aquarius"),
    ("pisces", "Pisces", "♓", (2, 19), (3, 20), "Water", "Neptune", "pisces"),
]

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

# name, RA, Dec, stars [(x, y, size 1-3)], edges [(i, j)]
CONSTELLATIONS = {
    "aries": ("Aries", "02h 38m", "+20°", [(.18, .30, 2), (.52, .46, 3), (.66, .58, 2), (.72, .66, 1)], [(0, 1), (1, 2), (2, 3)]),
    "taurus": ("Taurus", "04h 42m", "+15°", [(.50, .62, 3), (.42, .55, 2), (.38, .62, 1), (.45, .70, 1), (.20, .30, 2), (.80, .25, 2), (.62, .52, 1), (.30, .80, 1)],
               [(0, 1), (1, 4), (0, 6), (6, 5), (1, 2), (2, 3), (3, 7)]),
    "gemini": ("Gemini", "07h 04m", "+23°", [(.30, .18, 3), (.48, .14, 3), (.30, .40, 1), (.50, .38, 2), (.25, .62, 1), (.55, .60, 2), (.20, .85, 2), (.62, .82, 1)],
               [(0, 2), (2, 4), (4, 6), (1, 3), (3, 5), (5, 7), (0, 1)]),
    "cancer": ("Cancer", "08h 39m", "+20°", [(.50, .45, 2), (.48, .20, 1), (.25, .75, 2), (.72, .78, 2), (.52, .55, 1)], [(1, 0), (0, 4), (4, 2), (4, 3)]),
    "leo": ("Leo", "10h 40m", "+14°", [(.25, .62, 3), (.22, .45, 1), (.28, .30, 2), (.40, .22, 1), (.48, .30, 1), (.45, .55, 2), (.78, .58, 2), (.82, .45, 1)],
            [(0, 1), (1, 2), (2, 3), (3, 4), (1, 5), (0, 5), (5, 6), (6, 7), (7, 5)]),
    "virgo": ("Virgo", "13h 24m", "−04°", [(.55, .78, 3), (.48, .55, 2), (.30, .48, 1), (.62, .40, 2), (.75, .28, 1), (.20, .30, 1), (.82, .62, 1), (.40, .70, 1)],
              [(0, 1), (1, 2), (2, 5), (1, 3), (3, 4), (0, 6), (0, 7), (7, 2)]),
    "libra": ("Libra", "15h 12m", "−15°", [(.50, .25, 2), (.25, .50, 2), (.75, .52, 3), (.30, .78, 1), (.70, .80, 1)], [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4)]),
    "scorpius": ("Scorpius", "16h 53m", "−27°", [(.78, .15, 2), (.80, .25, 2), (.72, .30, 1), (.62, .38, 3), (.55, .48, 1), (.50, .60, 1), (.45, .72, 1), (.35, .80, 1), (.22, .78, 2), (.18, .68, 2)],
                 [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]),
    "sagittarius": ("Sagittarius", "19h 06m", "−25°", [(.30, .60, 3), (.40, .48, 2), (.55, .50, 2), (.62, .38, 2), (.70, .55, 1), (.55, .68, 2), (.40, .72, 2), (.22, .45, 1)],
                    [(0, 1), (1, 2), (2, 3), (2, 4), (2, 5), (5, 6), (6, 0), (0, 7), (1, 6)]),
    "capricornus": ("Capricornus", "21h 03m", "−18°", [(.80, .25, 2), (.70, .45, 1), (.55, .70, 2), (.35, .62, 1), (.18, .40, 3), (.30, .38, 1)],
                    [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]),
    "aquarius": ("Aquarius", "22h 17m", "−11°", [(.20, .25, 2), (.35, .30, 3), (.50, .38, 1), (.58, .30, 1), (.60, .55, 2), (.48, .70, 1), (.70, .78, 2), (.80, .62, 1)],
                 [(0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (4, 6), (6, 7)]),
    "pisces": ("Pisces", "00h 29m", "+14°", [(.15, .70, 2), (.30, .62, 1), (.48, .55, 1), (.70, .48, 3), (.62, .30, 1), (.58, .15, 2), (.82, .58, 1), (.78, .75, 1), (.88, .70, 2)],
               [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (3, 6), (6, 8), (8, 7), (7, 3)]),
    "orion": ("Orion", "05h 35m", "+05°", [(.30, .20, 3), (.70, .22, 2), (.42, .50, 2), (.50, .52, 2), (.58, .54, 2), (.32, .85, 2), (.72, .82, 3), (.52, .10, 1)],
              [(0, 2), (1, 4), (2, 3), (3, 4), (2, 5), (4, 6), (0, 7), (1, 7)]),
    "ursa_major": ("Ursa Major", "11h 19m", "+51°", [(.10, .35, 2), (.25, .32, 2), (.38, .38, 2), (.50, .45, 1), (.55, .65, 2), (.80, .68, 2), (.82, .45, 3)],
                   [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 3)]),
    "cassiopeia": ("Cassiopeia", "01h 00m", "+62°", [(.12, .40, 2), (.32, .62, 2), (.50, .42, 3), (.70, .60, 2), (.88, .35, 2)], [(0, 1), (1, 2), (2, 3), (3, 4)]),
    "lyra": ("Lyra", "18h 51m", "+37°", [(.50, .18, 3), (.42, .40, 1), (.58, .42, 1), (.40, .70, 2), (.60, .72, 2)], [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4)]),
    "cygnus": ("Cygnus", "20h 35m", "+45°", [(.50, .12, 3), (.50, .40, 2), (.50, .82, 2), (.18, .35, 2), (.82, .48, 2)], [(0, 1), (1, 2), (3, 1), (1, 4)]),
    "andromeda": ("Andromeda", "00h 48m", "+37°", [(.15, .75, 3), (.38, .60, 2), (.62, .45, 2), (.85, .25, 2), (.45, .40, 1), (.55, .28, 1)], [(0, 1), (1, 2), (2, 3), (1, 4), (4, 5)]),
    "perseus": ("Perseus", "03h 10m", "+45°", [(.50, .20, 2), (.48, .40, 3), (.35, .55, 2), (.62, .58, 1), (.25, .78, 1), (.70, .80, 2)], [(0, 1), (1, 2), (1, 3), (2, 4), (3, 5)]),
    "pegasus": ("Pegasus", "22h 42m", "+19°", [(.30, .30, 2), (.70, .30, 2), (.70, .65, 3), (.30, .65, 2), (.15, .85, 1), (.88, .80, 1)], [(0, 1), (1, 2), (2, 3), (3, 0), (3, 4), (2, 5)]),
    "corona_borealis": ("Corona Borealis", "15h 51m", "+32°", [(.15, .40, 1), (.28, .60, 2), (.45, .70, 3), (.62, .68, 2), (.78, .55, 1), (.85, .35, 1)], [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]),
    "ursa_minor": ("Ursa Minor", "15h 00m", "+77°", [(.15, .20, 3), (.30, .32, 1), (.45, .45, 1), (.60, .55, 1), (.62, .78, 2), (.85, .75, 2), (.82, .55, 1)],
                   [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 3)]),
    "draco": ("Draco", "15h 09m", "+67°", [(.15, .20, 2), (.25, .12, 2), (.32, .25, 1), (.40, .40, 1), (.60, .45, 2), (.75, .60, 1), (.65, .78, 1), (.45, .85, 2)],
              [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)]),
}

MAJOR_ARCANA = [
    ("0", "The Fool", "new beginnings, trust, leap of faith", "star8"),
    ("I", "The Magician", "willpower, manifestation, skill", "lemniscate"),
    ("II", "The High Priestess", "intuition, mystery, inner voice", "crescent"),
    ("III", "The Empress", "abundance, nurture, creativity", "venus"),
    ("IV", "The Emperor", "structure, stability, leadership", "square"),
    ("V", "The Hierophant", "wisdom, tradition, guidance", "key"),
    ("VI", "The Lovers", "union, choice, alignment", "heart"),
    ("VII", "The Chariot", "drive, victory, direction", "star8"),
    ("VIII", "Strength", "courage, patience, soft power", "lemniscate"),
    ("IX", "The Hermit", "solitude, reflection, inner light", "lantern"),
    ("X", "Wheel of Fortune", "cycles, change, destiny", "wheel"),
    ("XI", "Justice", "truth, balance, cause and effect", "scales"),
    ("XII", "The Hanged Man", "surrender, new perspective, pause", "triangle_down"),
    ("XIII", "Death", "endings, transformation, release", "rose"),
    ("XIV", "Temperance", "balance, moderation, flow", "triangle_up"),
    ("XV", "The Devil", "attachment, shadow, liberation", "pentagram"),
    ("XVI", "The Tower", "sudden change, revelation, awakening", "bolt"),
    ("XVII", "The Star", "hope, renewal, healing", "star8"),
    ("XVIII", "The Moon", "dreams, illusion, the subconscious", "crescent"),
    ("XIX", "The Sun", "joy, success, vitality", "sun"),
    ("XX", "Judgement", "rebirth, calling, reckoning", "sun"),
    ("XXI", "The World", "completion, wholeness, fulfilment", "wheel"),
]

MOON_PHASES = [
    ("new_moon", "New Moon", 0.0, "intentions, seeds, quiet beginnings"),
    ("waxing_crescent", "Waxing Crescent", 0.125, "hope, first steps, momentum"),
    ("first_quarter", "First Quarter", 0.25, "decisions, action, courage"),
    ("waxing_gibbous", "Waxing Gibbous", 0.375, "refining, patience, trust"),
    ("full_moon", "Full Moon", 0.5, "illumination, gratitude, release"),
    ("waning_gibbous", "Waning Gibbous", 0.625, "sharing, wisdom, thanks"),
    ("last_quarter", "Last Quarter", 0.75, "letting go, forgiveness, clearing"),
    ("waning_crescent", "Waning Crescent", 0.875, "rest, surrender, renewal"),
]

ELEMENTS = [
    ("fire", "Fire", "triangle_up", "Aries · Leo · Sagittarius", "passion, courage, spark"),
    ("water", "Water", "triangle_down", "Cancer · Scorpio · Pisces", "emotion, intuition, depth"),
    ("air", "Air", "triangle_up_bar", "Gemini · Libra · Aquarius", "thought, voice, freedom"),
    ("earth", "Earth", "triangle_down_bar", "Taurus · Virgo · Capricorn", "grounding, body, abundance"),
]

PLANETS = [
    ("sun", "The Sun", "☉", "identity, vitality, purpose"),
    ("moon", "The Moon", "☽", "emotion, instinct, inner tides"),
    ("mercury", "Mercury", "☿", "mind, words, messages"),
    ("venus", "Venus", "♀", "love, beauty, values"),
    ("mars", "Mars", "♂", "drive, desire, courage"),
    ("jupiter", "Jupiter", "♃", "growth, luck, expansion"),
    ("saturn", "Saturn", "♄", "discipline, time, mastery"),
]


def _fmt_date(md):
    return f"{MONTHS[md[0] - 1]} {md[1]}"


def all_subjects():
    """Flat list of dicts. `community` is the suggested Threads topic tag."""
    out = []
    for sid, name, glyph, start, end, element, ruler, ckey in SIGNS:
        out.append({"key": "sign:" + sid, "kind": "sign", "name": name, "glyph": glyph,
                    "subtitle": f"{_fmt_date(start)} – {_fmt_date(end)}", "start": start, "end": end,
                    "element": element, "ruler": ruler, "constellation": ckey, "community": "astrology"})
    for num, name, meaning, icon in MAJOR_ARCANA:
        out.append({"key": "tarot:" + name.lower().replace(" ", "_"), "kind": "tarot", "name": name.upper(),
                    "numeral": num, "subtitle": meaning.split(",")[0].strip().upper(), "meaning": meaning,
                    "icon": icon, "community": "manifestation"})
    zodiac_keys = {s[7] for s in SIGNS}
    for ckey, (name, ra, dec, *_rest) in CONSTELLATIONS.items():
        if ckey in zodiac_keys:
            continue
        out.append({"key": "const:" + ckey, "kind": "constellation", "name": name.upper(),
                    "subtitle": f"RA {ra} · DEC {dec}", "constellation": ckey, "community": "astrology"})
    for pid, name, phase, meaning in MOON_PHASES:
        out.append({"key": "moon:" + pid, "kind": "moon", "name": name.upper(), "phase": phase,
                    "subtitle": meaning.split(",")[0].strip().upper(), "meaning": meaning, "community": "manifestation"})
    for eid, name, icon, signs, meaning in ELEMENTS:
        out.append({"key": "element:" + eid, "kind": "element", "name": name.upper(), "icon": icon,
                    "subtitle": signs.upper(), "meaning": meaning, "community": "astrology"})
    for pid, name, glyph, meaning in PLANETS:
        out.append({"key": "planet:" + pid, "kind": "planet", "name": name.upper(), "glyph": glyph,
                    "subtitle": meaning.split(",")[0].strip().upper(), "meaning": meaning, "community": "astrology"})
    return out


def sign_in_season(today=None):
    """Key of the sign whose (calendar) season contains `today`."""
    today = today or _dt.date.today()
    md = (today.month, today.day)
    for sid, _n, _g, start, end, *_ in SIGNS:
        if start <= end:
            if start <= md <= end:
                return "sign:" + sid
        elif md >= start or md <= end:
            return "sign:" + sid
    return None
