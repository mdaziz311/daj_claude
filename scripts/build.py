import os, glob, subprocess, json, sys
from best import best

S = os.path.dirname(os.path.abspath(__file__))
D = f"{S}/src/video/GRADUATION AZRAHEIN"
SEG = f"{S}/seg"; os.makedirs(SEG, exist_ok=True)
OUT = "/home/user/daj_claude/output"; os.makedirs(OUT, exist_ok=True)

# (key, search_a, search_b, length, role)  role: A = A-roll (natural sound up), B = B-roll
# fixed in-point when search_a == search_b
EDL = [
    ("20260724_152426", 5.0, 11.3, 4.2, "A"),   # 0  hook: walking out with Dad, gown + scroll
    ("20260721_113126", 3.0, 10.0, 2.4, "B"),   # 1  family on the plane
    ("20260721_172528", 60.0, 72.0, 2.2, "B"),  # 2  flight map KL -> Abu Dhabi
    ("20260721_182414", 88.0, 112.0, 2.2, "B"),  # 3  wing above the clouds
    ("20260721_190652", 205.0, 244.0, 2.4, "B"),# 4  Heathrow walkway
    ("20260723_184934", 8.0, 27.0, 2.4, "B"),   # 5  Swansea street
    ("20260723_190644", 55.0, 82.0, 2.4, "B"),  # 6  shopping in town
    ("20260724_142448", 1.0, 3.6, 2.0, "B"),    # 7  Mum, morning of
    ("20260724_142448", 5.0, 9.2, 1.8, "B"),    # 8  Dad, morning of
    ("20260724_142536", 16.0, 26.5, 3.0, "B"),  # 9  Azrahein suited up
    ("20260724_145806", 12.0, 32.0, 2.6, "B"),  # 10 gold bridge profile
    ("20260724_145806", 35.0, 60.0, 2.6, "B"),  # 11 walking to Swansea Arena
    ("20260724_151852", 8.0, 40.0, 2.4, "B"),   # 12 collecting the gown
    ("20260724_152744", 0.0, 20.0, 2.2, "B"),   # 13 signing
    ("20260724_152744", 44.0, 56.0, 3.6, "B"),  # 14 the certificate
    ("20260724_152812", 4.0, 17.0, 3.0, "B"),   # 15 portrait in cap
    ("20260724_154234", 0.0, 10.0, 2.2, "B"),   # 16 walking, hood
    ("20260724_155204", 0.0, 12.0, 2.2, "B"),   # 17 walking to line-up
    ("20260724_170920", 20.0, 60.0, 2.6, "B"),  # 18 the arena
    ("20260724_171026", 8.0, 30.0, 2.2, "B"),   # 19 big screen
    ("20260724_174026", 9.6, 9.6, 12.4, "A"),   # 20 NAME CALLED (10.7s in clip)
    ("20260724_182836", 98.8, 98.8, 7.5, "A"),  # 21 "Graduates, please turn around..."
    ("20260724_182836", 109.8, 109.8, 5.6, "A"),# 22 ...applause for the families
    ("20260724_183856", 0.0, 30.0, 2.8, "A"),   # 23 recessional, "Celebration"
    ("20260724_185516", 26.3, 26.3, 2.6, "B"),  # 24 outside, sunglasses
    ("20260724_185516", 47.0, 47.0, 1.8, "B"),  # 25 outside, gown
    ("20260724_185516", 143.0, 154.0, 2.4, "B"),# 26 Mum waving
    ("20260724_185516", 155.0, 167.0, 2.4, "B"),# 27 Dad selfie
    ("20260724_145806", 82.0, 92.0, 5.5, "B"),  # 28 end card: standing before the arena
]

GRADE = "eq=contrast=1.06:saturation=1.12:gamma=0.98,unsharp=5:5:0.6:5:5:0.0"

def src(key):
    return glob.glob(f"{D}/dji_mimo_{key}_*_video.mp4")[0]

def render(i, key, a, b, L, role):
    t0 = a if a == b else best(key, a, b, L)
    out = f"{SEG}/{i:02d}.mp4"
    vf = f"scale=1080:1920:flags=lanczos,fps=30,{GRADE},format=yuv420p"
    if i == 20:
        # gentle push-in toward the stage / big screen while his name is called
        vf = ("scale=1080:1920:flags=lanczos,fps=30,"
              "zoompan=z='min(1+0.0009*on,1.28)':x='iw/2-(iw/zoom/2)':y='ih*0.38-(ih/zoom/2)':d=1:s=1080x1920:fps=30,"
              f"{GRADE},format=yuv420p")
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(t0), "-i", src(key), "-t", str(L),
           "-vf", vf, "-af", "aresample=48000,aformat=channel_layouts=stereo",
           "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-c:a", "pcm_s16le", out]
    if not os.path.exists(out):
        subprocess.run(cmd, check=True)
    return t0

if __name__ == "__main__":
    info = []
    t = 0.0
    for i, (k, a, b, L, role) in enumerate(EDL):
        t0 = render(i, k, a, b, L, role)
        info.append(dict(i=i, key=k, src_in=t0, dur=L, role=role, start=round(t, 3)))
        print(i, k, t0, L, role, round(t, 2), flush=True)
        t += L
    json.dump(info, open(f"{S}/timeline.json", "w"), indent=1)
    print("total", t)
