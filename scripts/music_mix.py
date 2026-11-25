"""Music version v2: per-segment loudness levelling + happy music bed that stays
audible throughout (gently ducked under speech/key moments, never muted)."""
import json, subprocess, sys
from finish import S, OUT, TL, st, en, TOTAL   # importing also rewrites captions.ass

LUFS = json.load(open(f"{S}/seg_lufs.json"))
MUSIC = f"{S}/music/{sys.argv[1] if len(sys.argv) > 1 else 'Carefree.mp3'}"
MUSIC_LUFS = float(sys.argv[2]) if len(sys.argv) > 2 else -19.7

# target loudness of the natural sound per segment (LUFS)
TARGET_A = {0: -27, 20: -20, 21: -18, 22: -21, 23: -23}   # A-roll
TARGET_B = -36                                            # B-roll ambience, just a hint
# music level per A-roll segment (1.0 = full bed)
MUSIC_A = {0: 0.9, 20: 0.55, 21: 0.33, 22: 0.6, 23: 0.55}
MUSIC_BED = -17.5   # bed loudness in LUFS before final normalisation

def db(x): return 10 ** (x / 20)

inputs, fc = [], []
for x in TL:
    inputs += ["-i", f"{S}/seg/{x['i']:02d}.mp4"]
n = len(TL)
for x in TL:
    i, L = x["i"], x["dur"]
    tgt = TARGET_A.get(i, TARGET_B) if x["role"] == "A" else TARGET_B
    gain_db = tgt - LUFS[f"{i:02d}"]
    gain_db = min(gain_db, 12 if x["role"] == "A" else 4)   # don't pump up hiss
    fc.append(f"[{i}:a]afade=t=in:d=0.06,afade=t=out:st={L-0.08:.3f}:d=0.08,"
              f"volume={db(gain_db):.4f}"
              + (",volume='if(between(t,0.7,3.9),2.24,1)':eval=frame" if i == 20 else "")
              + f"[a{i}]")
fc.append("".join(f"[{i}:v][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
fc.append(f"[vc]ass={S}/captions.ass,fade=t=in:st=0:d=0.4,fade=t=out:st={TOTAL-1.2:.2f}:d=1.2[v]")

# music envelope: 1.0 on B-roll, MUSIC_A level on A-roll, 0.4 s ramps
expr = "1"
for x in TL:
    i = x["i"]
    if x["role"] != "A" or i not in MUSIC_A: continue
    a, b, lv = st[i], en[i], MUSIC_A[i]
    w = f"min(1,max(0,min((t-{a-0.4:.2f})/0.4,({b+0.4:.2f}-t)/0.4)))"
    expr = f"({expr})*(1-{1-lv:.2f}*{w})"
# extra dip while the name is read out
na, nb = st[20] + 0.7, st[20] + 3.9
w = f"min(1,max(0,min((t-{na-0.3:.2f})/0.3,({nb+0.3:.2f}-t)/0.3)))"
expr = f"({expr})*(1-0.60*{w})"
pre = db(MUSIC_BED - MUSIC_LUFS)
fc.append(f"[{n}:a]atrim=0:{TOTAL:.2f},asetpts=PTS-STARTPTS,volume={pre:.4f},"
          f"volume='{expr}':eval=frame,"
          f"afade=t=in:d=0.5,afade=t=out:st={TOTAL-3.5:.2f}:d=3.5[m]")
fc.append("[ac][m]amix=inputs=2:normalize=0,alimiter=limit=0.89:level=false,"
          "loudnorm=I=-14:TP=-1.5:LRA=11[a]")
inputs += ["-i", MUSIC]
out = f"{OUT}/Azrahein_Graduation_Swansea_2026_WITH_MUSIC.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc),
                "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "19",
                "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac",
                "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out], check=True)
print("done", out)
