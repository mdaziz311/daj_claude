"""Pick the sharpest/steadiest window of length L inside [a,b] for a clip.
Score per 0.5s sample: sharpness (Laplacian var) penalised by motion."""
import json, os, sys
S = os.path.dirname(os.path.abspath(__file__))

def best(key, a, b, L, step=0.5):
    p = f"{S}/sharp/{key}.json"
    if not os.path.exists(p):
        return a
    v = json.load(open(p))  # 2 samples per second
    fps = 2
    n = int(L * fps)
    best_t, best_s = a, -1e18
    t = a
    while t + L <= b + 1e-6:
        i0 = int(t * fps)
        win = v[i0:i0 + n]
        if len(win) < max(1, n - 1):
            break
        sh = sorted(x[0] for x in win)
        # use lower quartile so one blurry moment drags the window down
        q = sh[len(sh) // 4]
        mo = sum(x[1] for x in win) / len(win)
        sc = q - 25 * max(0, mo - 6)
        if sc > best_s:
            best_s, best_t = sc, t
        t += step
    return round(best_t, 2)

if __name__ == "__main__":
    k, a, b, L = sys.argv[1], *map(float, sys.argv[2:5])
    print(best(k, a, b, L))
