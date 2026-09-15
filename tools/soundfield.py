"""SoundField 원판의 구 로고 교체.

원판이 -26.7° 기울어 있어 다른 박스처럼 축정렬 사각형으로 지울 수 없다.
로고 주변 패치만 떼어 수평이 되게 돌린 뒤 거기서 지우고 새로 얹고, 다시
돌려 되붙인다. 되붙일 때는 실제로 바뀐 영역만 마스크로 합성한다 — 패치
전체를 덮으면 두 번의 회전 보간으로 주변까지 뭉개진다.
"""
import sys; sys.path.insert(0, 'tools')
from relogo import *
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

OUT = "C:/Users/samter96/AppData/Local/Temp/claude/C--Users-samter96-Desktop-YSGAudioTools/6e7ff0ac-8202-472a-9f56-373bc7d9a82b/scratchpad"
SRC = "soundfield/assets/v2/product-disk.png"
ANG = -26.7
PATCH = (290, 390, 580, 570)
# 회전하면 네 귀퉁이가 빈다. 지울 사각형과 텍스처 원본이 그 빈 곳에
# 걸치면 검정이 번져 들어와 되돌린 뒤 검은 얼룩으로 남는다.
ERASE = (55, 114, 288, 152)        # 회전 좌표계
TEX   = (60, 90, 270, 112)


def run(dst):
    im = Image.open(SRC).convert("RGB")
    patch = im.crop(PATCH)
    rot = patch.rotate(ANG, Image.BICUBIC, expand=True)

    r = np.asarray(rot).astype(np.float32)/255.0
    r = inpaint(r, ERASE, iters=900)
    r = retexture(r, ERASE, TEX, strength=1.0, radius=4.0, feather=6)

    # 마크와 글자는 따로 얹는다. 한 덩어리로 만들면 마크 크기를 바꿀 때마다
    # 글자 시작 위치가 같이 밀려서 원본 자리와 어긋난다.
    CAP, X0, X1 = 9.6, 117, 275
    lo, hi = 0.0, 1.2
    for _ in range(24):
        t = (lo+hi)/2
        w = lockup_layer(1, "YSG AUDIO LABS", CAP, t, (246,248,250), 0).width
        if w < X1-X0: lo = t
        else: hi = t
    txt = lockup_layer(1, "YSG AUDIO LABS", CAP, lo, (246,248,250), 0, weight="Regular")
    r = place(r, txt, cx=X0 + txt.width/2, cy=131, angle=0.0, blur=0.3)

    mk = Image.open(MARK).resize((42, 42), Image.LANCZOS)
    r = place(r, mk, cx=75, cy=131, angle=0.0, blur=0.3, gain=1.35)

    rot2 = Image.fromarray((np.clip(r, 0, 1)*255).astype(np.uint8))

    # 바뀐 영역만 표시한 마스크도 같이 되돌린다
    mk = Image.new("L", rot.size, 0)
    ImageDraw.Draw(mk).rectangle([ERASE[0]-3, ERASE[1]-3, ERASE[2]+3, ERASE[3]+3], fill=255)
    back  = rot2.rotate(-ANG, Image.BICUBIC, expand=False)
    backm = mk.rotate(-ANG, Image.BICUBIC, expand=False).filter(ImageFilter.GaussianBlur(1.6))
    ox, oy = (back.width-patch.width)//2, (back.height-patch.height)//2
    back  = back.crop((ox, oy, ox+patch.width, oy+patch.height))
    backm = backm.crop((ox, oy, ox+patch.width, oy+patch.height))

    merged = Image.composite(back, patch, backm)
    out = im.copy(); out.paste(merged, PATCH[:2])
    out.save(dst, optimize=True)


if __name__ == "__main__":
    run(OUT + "/sf_done.png")
    a = Image.open(SRC).crop((300, 400, 620, 560))
    b = Image.open(OUT + "/sf_done.png").crop((300, 400, 620, 560))
    s = Image.new("RGB", (320*3, 160*3*2+12), (34, 34, 38))
    s.paste(a.resize((960, 480), Image.LANCZOS), (0, 0))
    s.paste(b.resize((960, 480), Image.LANCZOS), (0, 492))
    s.save(OUT + "/sf_ba.png"); print("ok")
