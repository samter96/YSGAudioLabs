"""박스 책등(옆면)의 구 삼지창을 2026 마크로 교체한다.

책등은 시선에서 비스듬해 가로로 눌려 보인다. 마크를 정사각으로 얹으면
그 면만 정면을 향한 것처럼 붕 뜬다 — 정면 삼지창과 책등 삼지창의 가로/세로
비를 재서 같은 비율로 눌러 얹는다.
"""
import sys; sys.path.insert(0, 'tools')
from relogo import *
from PIL import Image
import numpy as np

OUT = "C:/Users/samter96/AppData/Local/Temp/claude/C--Users-samter96-Desktop-YSGAudioTools/6e7ff0ac-8202-472a-9f56-373bc7d9a82b/scratchpad"

# 경로, 삼지창 bbox, 텍스처 원본, 기울기
JOBS = {
 # 삼지창은 아래로 가늘고 긴 꼬리가 있다. 꼬리 끝까지 재서 넉넉히 잡지
 # 않으면 마크 아래에 실선 한 줄이 남는다.
 "spatial": ("spatial-renderer/assets/v2/product-box.png",   (236,858,282,964), (236,968,282,1046), 0.0),
 "stereo":  ("stereo-auditor/assets/v2/product-box.png",     (314,803,362,896), (314,900,362,978),  0.0),
 "bus":     ("bus-routing-auditor/assets/v2/product-box.png",(294,852,346,956), (294,762,346,850),  0.0),
 "atten":   ("attenuation-auditor/assets/v2/product-box.png",(313,916,360,1016),(313,800,360,900),  0.0),
}


def clean(img, box):
    s = img[box[1]:box[3], box[0]:box[2]]
    sat = s.max(axis=2) - s.min(axis=2)
    return float(np.percentile(sat, 99)), float(np.percentile(s.max(axis=2), 99))


def run(key, src_png=None, dst=None):
    path, box, src, ang = JOBS[key]
    img = load(src_png or path)
    print(f"  {key} 텍스처원본 sat/lum p99 = %.3f / %.3f" % clean(img, src))
    img = inpaint(img, box, iters=900)
    img = retexture(img, box, src, strength=1.0, radius=5.0, feather=8)
    h = box[3]-box[1]
    w = box[2]-box[0]
    mk = Image.open(MARK).resize((max(8, int(h*(w/h)*1.15)), int(h*0.92)), Image.LANCZOS)
    lay = Image.new("RGBA", mk.size, (0, 0, 0, 0)); lay.paste(mk, (0, 0), mk)
    img = place(img, lay, cx=(box[0]+box[2])/2, cy=(box[1]+box[3])/2, angle=ang, blur=0.4)
    save(img, dst or f"{OUT}/spine_{key}.png")


if __name__ == "__main__":
    for k in JOBS:
        run(k, src_png=f"{OUT}/front_{k}.png"); print(k, "ok")
