# -*- coding: utf-8 -*-
"""YSG Audio Labs (2026 리뉴얼) — 인앱 상단바용 흑백 마크 생성기.

    python build_ysg_mark.py        → ysg-mark-2026-mono.svg · YsgMark.tsx.txt

⚠ 구 기하학 마크(Y 스플리터)의 생성기는 build_brand.py 다. 그쪽은 _retired/ 로
  물러난 SVG 들을 만든다 — 이 파일과 무관하고, 돌리면 은퇴한 자산이 되살아난다.

═══ 왜 수식으로 다시 세우는가 ════════════════════════════════════════════════
리뉴얼 로고 원본(brand/리뉴얼로고.png)은 **래스터뿐이고 벡터 원본이 없다.**
그 그림이 읽히는 핵심은 세 번 엮인 매듭 — 수학으로는 세잎매듭(trefoil)이다.
픽셀을 트레이스하면 반투명하게 겹친 띠들이 22px 에서 덩어리로 뭉개지므로,
같은 위상의 매듭을 수식으로 다시 세워 작은 크기에서 살아남게 단순화했다.

    x(t) = sin t + 2 sin 2t
    y(t) = cos t − 2 cos 2t
    z(t) = −sin 3t          ← 화면에는 안 그린다. 어느 획이 아래로 지나가는지만 정한다

═══ 규칙 (SoundField YsgMark 와 동일) ════════════════════════════════════════
  · 색을 박지 않는다 — currentColor. 무채색·네온·라이트 어느 테마든 글자색을 따라간다
  · 끊긴 자리는 마스크로 **실제로 뚫는다.** 배경색으로 덧칠하면 배경이 바뀌는 순간
    네모난 자국이 드러난다
  · 교차마다 아래 획을 지운 뒤 **위 획을 다시 그린다.** 지우기만 하면 두 획이 같이
    잘려서 엮인 게 아니라 부서진 매듭으로 보인다 (첫 시안에서 실제로 그랬다)

═══ 확정 파라미터 (사용자 선택 2026-09-15) ═══════════════════════════════════
  형태 A · 선 매듭 (가늘게, 획 2.10) · 바깥 궤도 원 없음
  기울이지 않은 정대칭 — 상단바에서 기울어 보이지 않게

⚠ 좌표를 손으로 고치지 말 것. 아래 수식과 파라미터가 기하의 유일한 출처다.
"""
import math

# ── 확정 파라미터 ────────────────────────────────────────────────────────────
VB = 24.0        # viewBox 한 변
STROKE = 2.10    # 획 두께
GAP = 0.85       # 아래로 지나가는 자리의 한쪽 여백
SEGS = 24        # 곡선을 나눌 3차 베지에 조각 수 (오차는 아래에서 실측한다)


def p(t):
    return (math.sin(t) + 2 * math.sin(2 * t),
            math.cos(t) - 2 * math.cos(2 * t))


def dp(t):
    return (math.cos(t) + 4 * math.cos(2 * t),
            -math.sin(t) + 4 * math.sin(2 * t))


def z(t):
    return -math.sin(3 * t)


# ── viewBox 맞춤 (획 두께까지 넣어 꽉 채운다) ────────────────────────────────
_S = [p(2 * math.pi * i / 4000) for i in range(4000)]
_xs, _ys = [q[0] for q in _S], [q[1] for q in _S]
SCALE = (VB - STROKE) / max(max(_xs) - min(_xs), max(_ys) - min(_ys))
_CX, _CY = (max(_xs) + min(_xs)) / 2, (max(_ys) + min(_ys)) / 2


def P(t):
    x, y = p(t)
    return ((x - _CX) * SCALE + VB / 2, (y - _CY) * SCALE + VB / 2)


def DP(t):
    dx, dy = dp(t)
    return (dx * SCALE, dy * SCALE)


# 3중 회전 대칭의 중심. 곡선 원점(0,0)이 옮겨간 자리 — **칸 중심(12,12)이 아니다.**
# 위아래 모양이 달라 경계상자 중심과 대칭 중심이 어긋난다. 배치는 경계상자 기준이
# 맞고(눈에 그렇게 보인다), 대칭 검사만 이 점을 축으로 해야 한다.
SYM = ((0 - _CX) * SCALE + VB / 2, (0 - _CY) * SCALE + VB / 2)


# ── 교차점 찾기 ──────────────────────────────────────────────────────────────
def find_crossings():
    """투영면에서 자기 자신과 만나는 (t_아래, t_위, 교차각) 3쌍."""
    N = 1200
    ts = [2 * math.pi * i / N for i in range(N)]
    pts = [P(t) for t in ts]
    seen, raw = [], []
    for i in range(N):
        for j in range(i + 40, N - (40 if i < 40 else 0)):
            if (pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2 > 0.25:
                continue
            mid = ((pts[i][0] + pts[j][0]) / 2, (pts[i][1] + pts[j][1]) / 2)
            if any((mid[0] - u) ** 2 + (mid[1] - v) ** 2 < 2.0 for u, v in seen):
                continue
            seen.append(mid)
            raw.append((ts[i], ts[j]))

    out = []
    for t1, t2 in raw:
        # 창을 반씩 좁혀 가며 두 점이 정확히 겹치는 매개변수를 찾는다
        w = 2 * math.pi / N
        for _ in range(60):
            best, bd = (t1, t2), 1e9
            for a in (t1 - w, t1, t1 + w):
                for b in (t2 - w, t2, t2 + w):
                    pa, pb = P(a), P(b)
                    d = (pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2
                    if d < bd:
                        bd, best = d, (a, b)
            t1, t2 = best
            w *= 0.6
        lo, hi = (t1, t2) if z(t1) < z(t2) else (t2, t1)
        d1, d2 = DP(lo), DP(hi)
        n1 = math.hypot(*d1)
        n2 = math.hypot(*d2)
        sin_th = abs(d1[0] * d2[1] - d1[1] * d2[0]) / (n1 * n2)
        out.append((lo, hi, sin_th))
    return out


CROSS = find_crossings()


def arc_delta(t, length):
    """t 근방에서 곡선 길이 length 에 해당하는 매개변수 폭."""
    return length / math.hypot(*DP(t))


def dist_to(t, s0, span=0.9):
    """P(t) 에서 s0 근방 획까지의 최단 거리."""
    best = 1e9
    for i in range(241):
        s = s0 - span + 2 * span * i / 240
        q = P(s)
        r = P(t)
        best = min(best, math.hypot(q[0] - r[0], q[1] - r[1]))
    return best


def clear_range(t_center, t_other, clearance):
    """t_center 쪽 획에서 상대 획과의 거리가 clearance 미만인 매개변수 구간.

    ⚠ 교차각으로 나누는 근사식을 쓰지 말 것. 곡률 때문에 교차점 양쪽 틈이
      다르게 남는다 (실측 1.04px vs 0.59px). 실제 거리로 경계를 찾으면 양쪽이
      같아진다."""
    step = arc_delta(t_center, 0.01)
    lo = hi = t_center
    while dist_to(lo - step, t_other) < clearance:
        lo -= step
    while dist_to(hi + step, t_other) < clearance:
        hi += step
    return lo, hi


# ── 경로 만들기 ──────────────────────────────────────────────────────────────
def bez(t0, t1, n, close=False, prec=2):
    """[t0,t1] 을 n 조각 3차 베지에로. 에르미트→베지에 정공법."""
    h = (t1 - t0) / n
    x, y = P(t0)
    d = f"M{x:.{prec}f} {y:.{prec}f}"
    for k in range(n):
        a, b = t0 + k * h, t0 + (k + 1) * h
        pa, pb, da, db = P(a), P(b), DP(a), DP(b)
        c1 = (pa[0] + da[0] * h / 3, pa[1] + da[1] * h / 3)
        c2 = (pb[0] - db[0] * h / 3, pb[1] - db[1] * h / 3)
        d += (f"C{c1[0]:.{prec}f} {c1[1]:.{prec}f} {c2[0]:.{prec}f} {c2[1]:.{prec}f}"
              f" {pb[0]:.{prec}f} {pb[1]:.{prec}f}")
    return d + ("Z" if close else "")


KNOT = bez(0, 2 * math.pi, SEGS, close=True)

# 자르는 붓은 아래 획을 딱 덮을 만큼만. 넓게 잡으면 틈이 아니라 구멍이 된다.
CUT_W = STROKE + 0.04
CUTS, OVERS = [], []
for lo, hi, _ in CROSS:
    # 아래 획에서 위 획 **띠 가장자리로부터 GAP** 만큼 떨어질 때까지를 지운다
    a, b = clear_range(lo, hi, STROKE / 2 + GAP)
    CUTS.append(bez(a, b, 3))
    # 지운 자리에 걸린 위 획을 되살린다 — 넉넉히 잡아도 경로 위라 해롭지 않다
    c, d = clear_range(hi, lo, STROKE + GAP)
    OVERS.append(bez(c, d, 3))


def svg(size=24, mask_id="ysg-mark"):
    cuts = "".join(f'\n      <path d="{c}" stroke="#000" stroke-width="{CUT_W:.2f}"/>'
                   for c in CUTS)
    overs = "".join(f'\n      <path d="{o}" stroke="#fff" stroke-width="{STROKE:.2f}"/>'
                    for o in OVERS)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{size}" height="{size}" aria-hidden="true">
  <defs>
    <mask id="{mask_id}" maskUnits="userSpaceOnUse" x="0" y="0" width="24" height="24">
      <rect width="24" height="24" fill="#000"/>
      <g fill="none" stroke-linecap="butt" stroke-linejoin="round">
      <path d="{KNOT}" stroke="#fff" stroke-width="{STROKE:.2f}"/>{cuts}{overs}
      </g>
    </mask>
  </defs>
  <rect width="24" height="24" fill="currentColor" mask="url(#{mask_id})"/>
</svg>'''


def tsx(component="YsgMark", default_size=19):
    """Stereo Auditor / SoundField 에 그대로 붙일 수 있는 컴포넌트."""
    def path(d, color, w):
        return ('          <path\n'
                f'            d="{d}"\n'
                f'            stroke="{color}"\n'
                f'            strokeWidth="{w:.2f}"\n'
                '          />')
    body = "\n".join(
        [path(KNOT, "white", STROKE)]
        + [path(c, "black", CUT_W) for c in CUTS]
        + [path(o, "white", STROKE) for o in OVERS])
    return f'''function {component}({{ size = {default_size} }}: {{ size?: number }}) {{
  return (
    <svg aria-hidden="true" width={{size}} height={{size}} viewBox="0 0 24 24">
      <mask id="ysg-mark" maskUnits="userSpaceOnUse" x="0" y="0" width="24" height="24">
        <rect width="24" height="24" fill="black" />
        <g fill="none" strokeLinecap="butt" strokeLinejoin="round">
{body}
        </g>
      </mask>
      <rect width="24" height="24" fill="currentColor" mask="url(#ysg-mark)" />
    </svg>
  );
}}
'''


if __name__ == "__main__":
    import os
    # 베지에 근사 오차 실측 — 24 조각으로 충분한지 숫자로 확인한다
    worst = 0.0
    for i in range(SEGS * 40):
        t = 2 * math.pi * i / (SEGS * 40)
        k = int(i / 40)
        h = 2 * math.pi / SEGS
        a, b = k * h, (k + 1) * h
        u = (t - a) / h
        pa, pb, da, db = P(a), P(b), DP(a), DP(b)
        c1 = (pa[0] + da[0] * h / 3, pa[1] + da[1] * h / 3)
        c2 = (pb[0] - db[0] * h / 3, pb[1] - db[1] * h / 3)
        m = 1 - u
        bx = m**3 * pa[0] + 3*m*m*u*c1[0] + 3*m*u*u*c2[0] + u**3 * pb[0]
        by = m**3 * pa[1] + 3*m*m*u*c1[1] + 3*m*u*u*c2[1] + u**3 * pb[1]
        ex, ey = P(t)
        worst = max(worst, math.hypot(bx - ex, by - ey))
    print(f"교차 {len(CROSS)}개, 교차각 sin = "
          + ", ".join(f"{s:.3f}" for *_, s in CROSS))
    print(f"베지에 근사 최대 오차 {worst:.5f} (viewBox 24 기준) "
          f"= 22px 렌더에서 {worst * 22 / 24:.5f}px")
    out = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(out, "ysg-mark-2026-mono.svg"), "w", encoding="utf-8") as f:
        f.write(svg())
    with open(os.path.join(out, "YsgMark.tsx.txt"), "w", encoding="utf-8") as f:
        f.write(tsx())
    print("매듭 경로", len(KNOT), "바이트 — ysg-mark-2026-mono.svg · YsgMark.tsx.txt 생성")
