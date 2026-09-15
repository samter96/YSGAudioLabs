"""제품 박스 정면의 구 로고 락업을 2026 마크 + YSG AUDIO LABS 로 교체한다.

지우기는 '사각 확산 + 같은 면 텍스처 복제' 2단계다. 확산만 쓰면 결이 날아가
판을 덧댄 것처럼 보이고, 로고 픽셀만 마스크로 지우면 글자의 소프트 글로우가
남아 유령이 보인다. 확산으로 그라디언트를 맞춘 뒤 깨끗한 부분의 고주파만
얹으면 둘 다 해결된다.
"""
import sys; sys.path.insert(0, 'tools')
from relogo import *
from PIL import Image

OUT = "C:/Users/samter96/AppData/Local/Temp/claude/C--Users-samter96-Desktop-YSGAudioTools/6e7ff0ac-8202-472a-9f56-373bc7d9a82b/scratchpad"

JOBS = {
 # 경로, 지울 사각형, 텍스처 원본, 결강도, 삼지창 bbox, 텍스트시작x, 세로중심,
 # 기울기, 마크px, cappx, 글자색, 굵기
 # 라벨은 무광 검정이라 결이 없다 — 텍스처 복제는 끄고 확산만 쓴다.
 "spatial": ("spatial-renderer/assets/v2/product-box.png",
             (620,730,905,792), (660,848,880,876), 0.0,
             (627,736,671,786), 690, 760,  1.93, 58, 14.5, (206,219,233), "Regular"),
 "stereo":  ("stereo-auditor/assets/v2/product-box.png",
             (526,322,876,408), (430,322,520,408), 1.00,
             (540,336,597,397), 616, 370,  3.01, 71, 15.3, (250,251,253), "Regular"),
 "bus":     ("bus-routing-auditor/assets/v2/product-box.png",
             (496,728,892,800), (418,728,494,800), 1.00,
             (505,735,565,804), 588, 766, -0.64, 80, 14.5, (237,242,246), "Regular"),
 "atten":   ("attenuation-auditor/assets/v2/product-box.png",
             (478,814,860,880), (414,814,476,880), 1.00,
             (487,824,531,871), 563, 847,  0.08, 55, 16.8, (214,206,218), "Semibold Text"),
}


# 삼지창 꼬리가 본 사각형 아래로 삐져나오는 경우의 추가 지우기
# 삼지창 꼬리는 y797 에서 끝나고 제목은 y809 부터다 — 본 사각형(→800)으로 충분하다.
EXTRA = {}


def run(key, dst=None):
    (path, erase, src, tstr, tri, tx0, cy, ang,
     mk, cap, col, weight) = JOBS[key]
    img = load(path)
    img = inpaint(img, erase, iters=900)
    if tstr:
        img = retexture(img, erase, src, strength=tstr, radius=5.0, feather=10)
    extra = EXTRA.get(key)
    if extra:
        box, sbox = extra
        img = inpaint(img, box, iters=900)
        img = retexture(img, box, sbox, strength=tstr, radius=5.0, feather=8)
    tri_cx = (tri[0]+tri[2])/2
    gap = int(round(tx0 - (tri_cx + mk/2)))
    lay = lockup_layer(mark_px=mk, text="YSG AUDIO LABS", cap_px=cap,
                       tracking=0.26, color=col, gap=max(gap, 6), weight=weight)
    img = place(img, lay, cx=tri_cx - mk/2 + lay.width/2, cy=cy, angle=ang, blur=0.45)
    save(img, dst or f"{OUT}/front_{key}.png")


if __name__ == "__main__":
    for k in JOBS:
        run(k); print(k, "ok")
