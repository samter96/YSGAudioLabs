"""제품 렌더 안의 구 삼지창 로고를 2026 마크로 갈아끼운다.

구 로고를 지울 때는 확산(diffusion) 인페인팅을 쓴다. 박스 면은 매끄러운
그라디언트라, 지울 사각형의 테두리 색을 경계조건으로 두고 안쪽을 반복
평균내면 네 변의 색이 자연스럽게 이어진다. 패치를 복사해 붙이는 방식은
가로/세로 그라디언트가 어긋나 자국이 남는다.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

MARK = "brand/ysg-mark-2026.png"
FONT = "C:/Windows/Fonts/SegUIVar.ttf"


def inpaint(img, box, iters=600, grain=0.0):
    """box 안을 테두리 색으로부터 확산시켜 메운다. img 는 float32 (H,W,3) 0..1."""
    x0, y0, x1, y1 = box
    pad = 2
    sub = img[y0-pad:y1+pad, x0-pad:x1+pad].copy()
    h, w, _ = sub.shape
    mask = np.zeros((h, w), bool)
    mask[pad:h-pad, pad:w-pad] = True
    cur = sub.copy()
    # 초기값: 테두리 평균
    cur[mask] = sub[~mask].mean(axis=0)
    for _ in range(iters):
        nb = (np.roll(cur, 1, 0) + np.roll(cur, -1, 0) +
              np.roll(cur, 1, 1) + np.roll(cur, -1, 1)) / 4.0
        cur[mask] = nb[mask]
        cur[~mask] = sub[~mask]
    if grain:
        rng = np.random.default_rng(7)
        cur[mask] += rng.normal(0, grain, cur[mask].shape)
    img[y0-pad:y1+pad, x0-pad:x1+pad] = np.clip(cur, 0, 1)
    return img


def lockup_layer(mark_px, text, cap_px, tracking, color, gap, ss=4, weight="Semilight Text"):
    """마크 + 자간 넓은 대문자 텍스트를 한 장의 RGBA 로 그린다 (ss 배 수퍼샘플)."""
    mk = Image.open(MARK).resize((mark_px*ss, mark_px*ss), Image.LANCZOS)
    f = ImageFont.truetype(FONT, int(cap_px*ss*1.36))
    if weight:
        try: f.set_variation_by_name(weight)
        except Exception: pass
    tr = int(tracking*cap_px*ss)
    widths = [int(f.getlength(c)) for c in text]
    tw = sum(widths) + tr*(len(text)-1)
    W = mark_px*ss + gap*ss + tw
    H = max(mark_px*ss, int(cap_px*ss*2.0))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lay.paste(mk, (0, (H-mark_px*ss)//2), mk)
    d = ImageDraw.Draw(lay)
    x = mark_px*ss + gap*ss
    asc, desc = f.getmetrics()
    ty = (H - (asc+desc))//2
    for c, cw in zip(text, widths):
        d.text((x, ty), c, font=f, fill=color+(255,))
        x += cw + tr
    return lay.resize((W//ss, H//ss), Image.LANCZOS)


def place(img, lay, cx, cy, angle, blur=0.5, gain=1.0):
    """lay 를 angle 만큼 돌려 (cx,cy) 중심에 가산 합성한다."""
    lay = lay.rotate(-angle, Image.BICUBIC, expand=True)
    if blur:
        lay = lay.filter(ImageFilter.GaussianBlur(blur))
    l = np.asarray(lay).astype(np.float32)/255.0
    H, W, _ = img.shape
    lh, lw, _ = l.shape
    x0, y0 = int(cx-lw/2), int(cy-lh/2)
    sx0, sy0 = max(0, x0), max(0, y0)
    sx1, sy1 = min(W, x0+lw), min(H, y0+lh)
    c = l[sy0-y0:sy1-y0, sx0-x0:sx1-x0]
    img[sy0:sy1, sx0:sx1] = np.clip(
        img[sy0:sy1, sx0:sx1] + c[..., :3]*c[..., 3:4]*gain, 0, 1)
    return img


def load(p):
    return np.asarray(Image.open(p).convert("RGB")).astype(np.float32)/255.0


def save(img, p):
    Image.fromarray((np.clip(img, 0, 1)*255).astype(np.uint8)).save(p, optimize=True)


# ── 마스크 기반 인페인팅 ────────────────────────────────────────────────
# 사각형을 통째로 지우면 박스 표면의 결과 그라디언트가 같이 날아가 판을
# 덧댄 것처럼 보인다. 구 로고 픽셀만 골라내 그 자리만 메우면 주변 텍스처가
# 그대로 남는다. 확산은 해상도 피라미드로 돌린다 — 원해상도에서 바로
# 돌리면 삼지창 폭(60px)을 메우는 데 수천 번 반복해야 한다.

def _dilate(mask, r):
    m = mask.copy()
    for _ in range(r):
        m = (m | np.roll(m, 1, 0) | np.roll(m, -1, 0)
               | np.roll(m, 1, 1) | np.roll(m, -1, 1))
    return m


def logo_mask(img, box, lum_pct=88, sat_pct=92, sat_margin=0.05, dilate=5):
    """box 안에서 구 로고(밝은 글자 + 채도 높은 삼지창) 픽셀을 고른다.

    절대 임계값은 못 쓴다 — 박스마다 면 색이 달라서(검정/네이비/자주) 채도
    바닥이 제각각이다. 영역 자체의 분위수로 잡아야 면 색에 끌려가지 않는다.
    """
    x0, y0, x1, y1 = box
    sub = img[y0:y1, x0:x1]
    lum = sub.max(axis=2)
    sat = sub.max(axis=2) - sub.min(axis=2)
    m = (lum > np.percentile(lum, lum_pct)) | (sat > np.percentile(sat, sat_pct) + sat_margin)
    return _dilate(m, dilate)


def inpaint_mask(img, box, mask, iters=60, levels=5, grain=0.0):
    x0, y0, x1, y1 = box
    pad = 8
    X0, Y0 = max(0, x0-pad), max(0, y0-pad)
    X1, Y1 = min(img.shape[1], x1+pad), min(img.shape[0], y1+pad)
    sub = img[Y0:Y1, X0:X1].copy()
    m = np.zeros(sub.shape[:2], bool)
    m[y0-Y0:y1-Y0, x0-X0:x1-X0] = mask

    def fill(a, mk, it):
        cur = a.copy()
        known = ~mk
        if known.sum() == 0:
            return cur
        cur[mk] = a[known].mean(axis=0)
        for _ in range(it):
            nb = (np.roll(cur, 1, 0) + np.roll(cur, -1, 0) +
                  np.roll(cur, 1, 1) + np.roll(cur, -1, 1)) / 4.0
            cur[mk] = nb[mk]
            cur[known] = a[known]
        return cur

    # 거친 해상도에서 큰 구멍을 먼저 메우고, 올라오면서 다듬는다
    pyr = [(sub, m)]
    for _ in range(levels-1):
        s, k = pyr[-1]
        h, w = s.shape[0]//2, s.shape[1]//2
        if h < 4 or w < 4:
            break
        pyr.append((np.asarray(Image.fromarray((s*255).astype(np.uint8)).resize((w, h), Image.BOX)).astype(np.float32)/255.0,
                    np.asarray(Image.fromarray(k.astype(np.uint8)*255).resize((w, h), Image.BOX)) > 40))
    cur = None
    for s, k in reversed(pyr):
        if cur is not None:
            up = np.asarray(Image.fromarray((cur*255).astype(np.uint8)).resize((s.shape[1], s.shape[0]), Image.BILINEAR)).astype(np.float32)/255.0
            s = np.where(k[..., None], up, s)
        cur = fill(s, k, iters)
    if grain:
        rng = np.random.default_rng(11)
        cur[m] += rng.normal(0, grain, cur[m].shape)
    img[Y0:Y1, X0:X1] = np.clip(cur, 0, 1)
    return img


def _tile_mirror(patch, W, H):
    """patch 를 좌우/상하 미러로 이어붙여 (H,W) 를 채운다. 무늬가 불규칙해
    미러 이음매가 눈에 띄지 않는다."""
    ph, pw, _ = patch.shape
    cols = []
    for i in range((W+pw-1)//pw):
        cols.append(patch if i % 2 == 0 else patch[:, ::-1])
    band = np.concatenate(cols, axis=1)[:, :W]
    rows = []
    for j in range((H+ph-1)//ph):
        rows.append(band if j % 2 == 0 else band[::-1])
    return np.concatenate(rows, axis=0)[:H]


def _blur(a, r):
    im = Image.fromarray((np.clip(a, 0, 1)*255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r))).astype(np.float32)/255.0


def retexture(img, box, src_box, strength=1.0, radius=6.0, feather=6):
    """box 안(확산으로 이미 매끈해진 곳)에 src_box 의 고주파 결을 되살린다."""
    x0, y0, x1, y1 = box
    W, H = x1-x0, y1-y0
    sp = img[src_box[1]:src_box[3], src_box[0]:src_box[2]]
    tex = _tile_mirror(sp, W, H)
    high = tex - _blur(tex, radius)
    dst = img[y0:y1, x0:x1]
    w = np.ones((H, W), np.float32)
    for i in range(feather):
        k = i/feather
        w[i, :] = np.minimum(w[i, :], k); w[H-1-i, :] = np.minimum(w[H-1-i, :], k)
        w[:, i] = np.minimum(w[:, i], k); w[:, W-1-i] = np.minimum(w[:, W-1-i], k)
    img[y0:y1, x0:x1] = np.clip(dst + high*strength*w[..., None], 0, 1)
    return img
