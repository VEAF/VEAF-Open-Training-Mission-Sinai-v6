"""Lot 07b : balises radio du circuit touristique des pyramides — sons fabriqués ici, émission FM en boucle.

Chaque balise répète son indicatif en morse (GIZ, SAQ, DAH) sur une tonalité de 800 Hz : des fichiers WAV écrits
par ce script dans tools/sons/ (aucun son emprunté), embarqués par add_sound. Fréquences FM 31.0-33.0, hors de la
bande des tours (38.4-42.2).
Les balises sont permanentes : leur nom ne commence pas par celui de la zone touristique, qui ne les capture
donc pas (elles guident vers le plateau avant toute activation).
Le guide (messages au survol des monuments) est du Lua dans src/scripts/mission-script.lua.
"""
import math
import struct
import wave

from lib import BLUE_EG, PLACES, ROOT, Batch, off, spot, xy

P = PLACES
MORSE = {"A": ".-", "D": "-..", "G": "--.", "H": "....", "I": "..", "Q": "--.-", "S": "...", "Z": "--.."}
RATE, TONE, DOT = 8000, 800, 0.1


def morse_wav(code, path):
    """Écrit l'indicatif `code` en morse (point 100 ms, trait 300 ms), suivi de 2 s de silence."""
    samples = []

    def tone(t):
        n = int(RATE * t)
        for i in range(n):
            env = min(1.0, i / 40, (n - i) / 40)   # attaque et relâche de 5 ms : pas de clic
            samples.append(int(12000 * env * math.sin(2 * math.pi * TONE * i / RATE)))

    def silence(t):
        samples.extend([0] * int(RATE * t))

    for letter in code:
        for sym in MORSE[letter]:
            tone(DOT if sym == "." else 3 * DOT)
            silence(DOT)
        silence(2 * DOT)
    silence(2.0)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", s) for s in samples))
    return len(samples) / RATE


DAHCHOUR = ((P["Red Pyramid"][0] + P["Bent Pyramid"][0]) / 2, (P["Red Pyramid"][1] + P["Bent Pyramid"][1]) / 2)
BEACONS = [  # nom, indicatif, MHz FM, position, sous-titre
    ("Balise GIZ", "GIZ", 31.0, off(P["Great Sphinx of Giza"], 90, 600), "GIZ — Gizeh"),
    ("Balise SAQ", "SAQ", 32.0, off(P["Pyramid of Djoser"], 180, 600), "SAQ — Saqqarah"),
    ("Balise DAH", "DAH", 33.0, DAHCHOUR, "DAH — Dahchour"),
]

if __name__ == "__main__":
    sons = ROOT / "tools/sons"
    sons.mkdir(exist_ok=True)
    b = Batch()
    for name, code, mhz, pos, sub in BEACONS:
        wav = sons / f"balise-{code}.wav"
        dur = morse_wav(code, wav)
        p = spot(pos, 0, 0, name)
        b.act("add_sound", sound_path=wav.as_posix())
        b.act("add_group", **BLUE_EG, category="vehicle", name=name, position=xy(p),
              units=[{"type": "Hummer", "name": name}], keep_position=True)
        b.act("edit_route", group_name=name, operation="add_task", index=1, task="set_frequency",
              task_params={"frequency_mhz": mhz, "modulation": "FM"})
        b.act("edit_route", group_name=name, operation="add_task", index=1, task="transmit_message",
              task_params={"sound": wav.name, "loop": True, "duration_s": math.ceil(dur), "subtitle": sub})
        print(f"{name:12} {mhz} FM  {dur:.1f} s  {round(p[0])} {round(p[1])}")
    b.save("07b-tourisme.json")
