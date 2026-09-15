"""제품 렌더 5장의 구 로고를 2026 로고로 교체해 제자리에 쓴다.

원본은 항상 Git HEAD 에서 읽는다. 결과 파일을 다시 입력으로 삼으면 두 번
돌릴 때 지우기와 얹기가 겹쳐 쌓인다.
"""
import sys, subprocess, os; sys.path.insert(0, 'tools')
from relogo import *
import fronts, spines, soundfield
from PIL import Image

TMP = "C:/Users/samter96/AppData/Local/Temp/claude/C--Users-samter96-Desktop-YSGAudioTools/6e7ff0ac-8202-472a-9f56-373bc7d9a82b/scratchpad/build"
os.makedirs(TMP, exist_ok=True)


def head(path):
    dst = f"{TMP}/{path.replace('/', '_')}"
    with open(dst, "wb") as f:
        subprocess.run(["git", "show", f"HEAD:{path}"], stdout=f, check=True)
    return dst


for key, (path, *_rest) in fronts.JOBS.items():
    orig = head(path)
    fronts.JOBS[key] = (orig,) + tuple(_rest)
    fronts.run(key, dst=f"{TMP}/f_{key}.png")

    sp = spines.JOBS[key]
    spines.JOBS[key] = (f"{TMP}/f_{key}.png",) + sp[1:]
    spines.run(key, dst=f"{TMP}/s_{key}.png")

    img = load(f"{TMP}/s_{key}.png")
    if key == "spatial":
        # 제품명 앞의 러프한 (o) 아이콘을 새 제품 아이콘으로
        img = inpaint(img, (620, 796, 674, 846), iters=900)
        ic = Image.open("brand/icon-spatial-renderer-2026.png").resize((50, 50), Image.LANCZOS)
        img = place(img, ic, cx=646, cy=821, angle=1.93, blur=0.35, gain=1.15)
    save(img, path)
    print("wrote", path)

soundfield.SRC = head(soundfield.SRC)
soundfield.run("soundfield/assets/v2/product-disk.png")
print("wrote soundfield/assets/v2/product-disk.png")
