import json, os, subprocess
S = os.path.dirname(os.path.abspath(__file__))
OUT = "/home/user/daj_claude/output"
TL = json.load(open(f"{S}/timeline.json"))
st = {x["i"]: x["start"] for x in TL}
en = {x["i"]: x["start"] + x["dur"] for x in TL}
TOTAL = en[len(TL) - 1]

def ts(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

GOLD = "&H004CC8E8"   # BGR of #E8C84C
WHITE = "&H00FFFFFF"
HDR = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter SemiBold,60,{WHITE},{WHITE},&H18000000,&H60000000,0,0,0,0,100,100,0,0,1,3.2,4,2,80,80,430,1
Style: Gold,Playfair Display,70,{GOLD},{GOLD},&H18000000,&H60000000,1,0,0,0,100,100,0.5,0,1,3.6,4,2,70,70,430,1
Style: Kicker,Inter SemiBold,34,{WHITE},{WHITE},&H18000000,&H60000000,0,0,0,0,100,100,6,0,1,2.4,3,8,60,60,170,1
Style: Script,Great Vibes,150,{WHITE},{WHITE},&H18000000,&H60000000,0,0,0,0,100,100,0,0,1,3.2,4,8,50,50,220,1
Style: Title,Playfair Display,64,{GOLD},{GOLD},&H18000000,&H60000000,1,0,0,0,100,100,10,0,1,3.2,4,8,50,50,420,1
Style: Quote,Playfair Display Medium,50,{WHITE},{WHITE},&H18000000,&H60000000,0,1,0,0,100,100,0,0,1,3.2,4,2,80,80,430,1
Style: Name,Playfair Display,66,{WHITE},{WHITE},&H18000000,&H60000000,1,0,0,0,100,100,1,0,1,3.4,4,2,60,60,560,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev = []
def add(a, b, style, text, fade=(250, 250), layer=0, mv=None):
    tag = "{\\fad(%d,%d)}" % fade
    ev.append(f"Dialogue: {layer},{ts(a)},{ts(b)},{style},,0,0,{mv if mv is not None else 0},,{tag}{text}")

# 0  hook / title
add(0.25, en[0] - 0.1, "Kicker", "SWANSEA UNIVERSITY  ·  24 JULY 2026")
add(0.45, en[0] - 0.1, "Script", "Azrahein Azran", (500, 250))
add(0.9, en[0] - 0.1, "Title", "GRADUATION DAY", (400, 250))
# journey
add(st[1] + .1, en[2] - .05, "Cap", "It all started 11,000 km from home…")
add(st[3] + .1, en[4] - .05, "Cap", "{\\fs52}Kuala Lumpur ✈ Abu Dhabi ✈ London")
add(st[5] + .1, en[6] - .05, "Cap", "…all the way to Swansea, Wales.")
# morning
add(st[7] + .1, en[8] - .05, "Gold", "24 July 2026")
add(st[9] + .05, en[9] - .05, "Cap", "The day we had all been waiting for.")
add(st[10] + .1, en[11] - .05, "Cap", "Suited up. Swansea Arena awaits.")
add(st[12] + .1, en[13] - .05, "Cap", "Gown on. Cap ready.")
# certificate
add(st[14] + .15, en[14] - .05, "Gold", "BSc Computer Science\\N{\\fs54}First Class Honours")
add(st[15] + .1, en[15] - .05, "Cap", "All those late nights…\\Nfor this one moment.")
add(st[16] + .1, en[17] - .05, "Cap", "One last walk as a student.")
# ceremony
add(st[18] + .1, en[19] - .05, "Gold", "Class of 2026")
name_t = st[20] + (10.7 - TL[20]["src_in"])
add(name_t, name_t + 4.6, "Name", "“Azrahein Azran Mohd Azis”", (200, 300))
add(name_t + 5.0, en[20] - .1, "Cap", "Mum, Dad… I made it.", (300, 300))
# tribute
add(st[21] + .2, st[21] + 4.0, "Quote", "“Graduates, please turn around\\Nand join us in a round of applause…”", (150, 150))
add(st[21] + 4.0, en[21] + .3, "Quote", "“…for those who’ve made\\Nthis day possible for you.”", (150, 200))
add(st[22] + .6, en[22] - .05, "Gold", "Mum & Dad,\\Nthis one is for you.", (300, 300))
add(st[23] + .1, en[23] - .05, "Cap", "Time to celebrate!")
add(st[24] + .1, en[25] - .05, "Cap", "Every sacrifice. Every prayer.\\NEvery call home.")
add(st[26] + .1, en[27] - .05, "Cap", "It was all worth it.")
# end card
e0 = st[28]
add(e0 + .2, TOTAL - .1, "Script", "Congratulations", (600, 500))
add(e0 + .8, TOTAL - .1, "Title", "AZRAHEIN AZRAN MOHD AZIS", (500, 500))
add(e0 + 1.3, TOTAL - .1, "Kicker", "BSc COMPUTER SCIENCE · FIRST CLASS HONOURS", (500, 500), mv=640)
add(e0 + 1.8, TOTAL - .1, "Cap", "Swansea University · Class of 2026\\N{\\fs44\\c" + GOLD + "}With love & pride, Mum and Dad", (500, 500))

open(f"{S}/captions.ass", "w").write(HDR + "\n".join(ev) + "\n")

# ---------- audio / video assembly ----------
A_SEGS = [x["i"] for x in TL if x["role"] == "A"]

def build(with_music, out):
    inputs, fc = [], []
    for x in TL:
        inputs += ["-i", f"{S}/seg/{x['i']:02d}.mp4"]
    n = len(TL)
    for x in TL:
        i, L = x["i"], x["dur"]
        if with_music:
            g = 1.0 if x["role"] == "A" else 0.10
            if i == 23: g = 0.45
        else:
            g = 1.15 if x["role"] == "A" else 0.6
        fc.append(f"[{i}:a]afade=t=in:d=0.06,afade=t=out:st={L-0.08:.3f}:d=0.08,volume={g}[a{i}]")
    fc.append("".join(f"[{i}:v][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
    fc.append(f"[vc]ass={S}/captions.ass,fade=t=in:st=0:d=0.4,fade=t=out:st={TOTAL-1.2:.2f}:d=1.2[v]")
    if with_music:
        inputs += ["-i", f"{S}/music/Wholesome.mp3"]
        # duck music under A-roll (with 0.35s ramps)
        parts = []
        for i in A_SEGS:
            a, b = st[i], en[i]
            lvl = 0.55 if i == 23 else 0.82
            parts.append(f"{lvl}*min(1,max(0,min((t-{a-0.35:.2f})/0.35,({b+0.35:.2f}-t)/0.35)))")
        duck = "max(" + ",".join(parts) + ")" if len(parts) > 1 else parts[0]
        # nested max needs pairs
        expr = parts[0]
        for p in parts[1:]:
            expr = f"max({expr},{p})"
        fc.append(f"[{n}:a]atrim=0:{TOTAL:.2f},asetpts=PTS-STARTPTS,"
                  f"volume='0.85*(1-({expr}))':eval=frame,"
                  f"afade=t=in:d=0.6,afade=t=out:st={TOTAL-3.5:.2f}:d=3.5[m]")
        fc.append("[ac][m]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    else:
        fc.append(f"[ac]highpass=f=70,afade=t=out:st={TOTAL-1.5:.2f}:d=1.5,loudnorm=I=-15:TP=-1.5:LRA=11[a]")
    cmd = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc),
           "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "19",
           "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "192k",
           "-ar", "48000", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    import sys
    which = sys.argv[1:] or ["music", "nomusic"]
    if "music" in which:
        build(True, f"{OUT}/Azrahein_Graduation_Swansea_2026_WITH_MUSIC.mp4")
    if "nomusic" in which:
        build(False, f"{OUT}/Azrahein_Graduation_Swansea_2026_NO_MUSIC.mp4")
    print("TOTAL", TOTAL)
