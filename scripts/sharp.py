import sys,subprocess,numpy as np,cv2,glob,json,os
D=sys.argv[1]; out={}
for key in sys.argv[2:]:
    import os
    if os.path.exists(f"/tmp/claude-0/-home-user-daj-claude/ea76f2dd-48b3-5929-a865-0b328a91da8d/scratchpad/sharp/{key}.json"): continue
    f=glob.glob(f"{D}/dji_mimo_{key}_*_video.mp4")[0]
    W,H=270,480
    p=subprocess.Popen(["ffmpeg","-v","error","-i",f,"-vf",f"fps=2,scale={W}:{H}","-f","rawvideo","-pix_fmt","gray","-"],stdout=subprocess.PIPE)
    vals=[];prev=None
    while True:
        b=p.stdout.read(W*H)
        if len(b)<W*H: break
        g=np.frombuffer(b,np.uint8).reshape(H,W)
        s=cv2.Laplacian(g,cv2.CV_64F).var()
        mo=0 if prev is None else float(np.abs(g.astype(int)-prev).mean())
        prev=g.astype(int); vals.append((round(s),round(mo,1)))
    json.dump(vals,open(f"/tmp/claude-0/-home-user-daj-claude/ea76f2dd-48b3-5929-a865-0b328a91da8d/scratchpad/sharp/{key}.json","w")); print(key,len(vals),flush=True)
json.dump(out,open(sys.argv[0].replace("sharp.py","sharp.json"),"w"))
