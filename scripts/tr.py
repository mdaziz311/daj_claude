import sys,glob,os
from faster_whisper import WhisperModel
m=WhisperModel("small",device="cpu",compute_type="int8",cpu_threads=os.cpu_count())
for f in sys.argv[1:]:
    import wave,numpy as np; w=wave.open(f); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768; segs,_=m.transcribe(a,language="en",vad_filter=False,initial_prompt=None)
    with open(f[:-4]+".txt","w") as o:
        for s in segs: o.write(f"{s.start:7.1f}-{s.end:7.1f} {s.text}\n")
    print("done",f,flush=True)
