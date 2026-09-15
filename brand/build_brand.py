# -*- coding: utf-8 -*-
"""YSG Audio Labs 브랜드 산출물 생성기 — 확정 기하 하나에서 전부 만든다.

═══ 확정안 : SPLIT NODE ══════════════════════════════════════════════════════
중심에서 세 방향으로 뻗으며 끝으로 갈수록 얇아지는 획.

  · Y 스플리터  한 소스가 갈라진다 — 오디오의 실제 개념. 동시에 YSG 의 Y
  · taper       끝으로 갈수록 얇아짐 = 거리에 따른 감쇠(attenuation)
  · 평평 마감    계측기의 마감. 좌우 **대칭**이다. 둥근 끝은 '뿔' 로 보여 기각했고,
                한쪽만 사선으로 깎았을 때는 마크 전체가 돌아 보여 기각했다
  · 세 획 같은 길이  아래 획만 늘렸다가 "대충 봐도 비대칭" 지적을 받았다.
                위 두 획이 벌어진 배치만으로 이미 Y 다 (2026-09-09)
  · 세로 중심 보정  잉크 중심이 칸 중심에 오도록 노드 원점만 올린다 (아래 CY 주석)

파형도 헤드폰도 쓰지 않는다. 획 3개뿐이라 16px 에서도 형태가 남는다.

기각한 방향과 이유는 explore*.py 주석에 남겼다 — 같은 길을 다시 걷지 않기 위해.

═══ 산출물 ═══════════════════════════════════════════════════════════════════
  ysg-mark-mono.svg      흑백 마크        앱 타이틀바·파비콘 (currentColor)
  YsgMark.tsx            앱용 컴포넌트    SoundField 에 그대로 넣는다
  ysg-mark-color.svg     컬러 고도화      웹·문서·발표
  ysg-icon-color.svg     앱 아이콘        스퀘어 프레임 + 마크
  ysg-logotype.svg       가로 조합        마크 + 워드마크
  ysg-mark-motion.svg    모션 (2.2초)     소개 페이지 — img 태그로도 재생된다
  brand.html             브랜드 시트      전부 한 장에서 검토
"""
import io
import math
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ── 확정 파라미터 (8차 — 대칭 교정) ────────────────────────────────────────
#  ⚠ 세 획의 길이는 **반드시 같게** 둔다. 예전에는 Y 로 읽히게 하려고 아래 획만
#    10.6 으로 늘렸는데, 그 대가로 3중 회전 대칭이 깨져 "대충 봐도 비대칭" 이라는
#    지적을 받았다 (2026-09-09). 아래 획을 늘리지 말 것 — 위 두 획이 벌어진
#    배치만으로 이미 Y 로 읽힌다.
CX = 12.0
REACH = 9.9        # 세 획 **공통** 길이
W0 = 5.2           # 중심 쪽 폭
W1 = 1.2           # 끝 폭 (감쇠) — 날카롭게. 이보다 줄이면 16px 에서 끝이 사라진다
SPREAD = 60.0      # 위 두 획이 수직에서 벌어진 각도 → 정확한 120° 3중 대칭
SOFTEN = 0.45      # 같은 색 얇은 stroke 로 모서리만 살짝 둥글린다

# ── 세로 중심 보정 (9차) ───────────────────────────────────────────────────
#  ⚠ 노드 원점(CY)은 24 칸의 중심이 **아니다.** 세 획은 120° 대칭이지만 아래 획만
#    곧게 내려가고 위 두 획은 60° 로 누워 있어서, 원점을 12 에 두면 잉크가 아래로
#    +2.215 쏠린다 (26px 렌더에서 2.4px). 가로는 정확히 12 인데 세로만 어긋나서
#    타이틀바에서 "글자와 세로 중앙이 안 맞는다" 는 지적을 받았다 (2026-09-09).
#    그래서 잉크의 위아래 끝 중간이 정확히 12 가 되도록 원점을 그만큼 올린다.
#  ⚠ 보정값을 손으로 박지 말 것 — REACH·W1·SPREAD 를 고치면 여기서 다시 계산된다.
_INK_TOP = (12.0 - REACH * math.cos(math.radians(SPREAD))
            - (W1 / 2) * math.sin(math.radians(SPREAD)))   # 위 획 끝 모서리
_INK_BOTTOM = 12.0 + REACH                                 # 아래 획 끝
CY = 12.0 - ((_INK_TOP + _INK_BOTTOM) / 2 - 12.0)

STROKES = [("down", 90.0, REACH), ("upleft", 270.0 - SPREAD, REACH),
           ("upright", 270.0 + SPREAD, REACH)]

# ── 브랜드 색 ──────────────────────────────────────────────────────────────
#   차갑고 정밀한 계열로 고정한다. 소개 페이지의 시안·블루와 이어지도록 맞췄다.
CYAN = "#34E0E8"       # 신호 — 가장 밝은 지점
BLUE = "#2C6BE0"       # 공간
INDIGO = "#1B2A6B"     # 깊이
DEEP = "#0B1230"       # 가장 먼 곳
INK = "#070A0F"        # 배경 잉크
AMBER = "#FFB454"      # 강조 한 점 (절제해서 쓴다)


def unit(deg):
    r = math.radians(deg)
    return (math.cos(r), math.sin(r))


def stroke_path(deg, end, w0=W0, w1=W1, start=0.0):
    """중심(또는 start)에서 end 까지, 폭 w0→w1 로 좁아지는 획.

    ⚠ 끝 마감은 진행 방향에 **수직인 평평한 면**이다 (좌우 대칭).
      예전에는 한쪽 모서리(b1)만 사선으로 깎았는데, 세 획이 모두 같은 방향으로
      기울어 마크 전체가 돌아간 것처럼 보였다 — "비대칭" 지적의 절반이 이것이다.
      한쪽만 깎는 방식으로 되돌리지 말 것."""
    d = unit(deg)
    p = (-d[1], d[0])
    a = (CX + d[0] * start, CY + d[1] * start)
    b = (CX + d[0] * end, CY + d[1] * end)
    a1 = (a[0] + p[0] * w0 / 2, a[1] + p[1] * w0 / 2)
    a2 = (a[0] - p[0] * w0 / 2, a[1] - p[1] * w0 / 2)
    b1 = (b[0] + p[0] * w1 / 2, b[1] + p[1] * w1 / 2)
    b2 = (b[0] - p[0] * w1 / 2, b[1] - p[1] * w1 / 2)
    return ("M %.3f %.3f L %.3f %.3f L %.3f %.3f L %.3f %.3f Z"
            % (a1[0], a1[1], b1[0], b1[1], b2[0], b2[1], a2[0], a2[1]))


PATHS = {name: stroke_path(deg, end) for name, deg, end in STROKES}
TIPS = {name: (CX + unit(deg)[0] * end, CY + unit(deg)[1] * end)
        for name, deg, end in STROKES}


# ── 1) 흑백 마크 ───────────────────────────────────────────────────────────
def mono_body(indent="  "):
    return "\n".join(
        '%s<path d="%s" fill="currentColor" stroke="currentColor"'
        ' stroke-width="%.2f" stroke-linejoin="round"/>' % (indent, PATHS[n], SOFTEN)
        for n, _, _ in STROKES)


def write_mono():
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"'
           ' role="img" aria-label="YSG Audio Labs">\n%s\n</svg>\n' % mono_body())
    io.open(os.path.join(OUT, "ysg-mark-mono.svg"), "w", encoding="utf-8").write(svg)
    return svg


# ── 2) 앱용 React 컴포넌트 ─────────────────────────────────────────────────
def write_tsx():
    rows = "\n".join(
        '      <path d="%s"\n'
        '            fill="currentColor" stroke="currentColor"\n'
        '            strokeWidth={%.2f} strokeLinejoin="round" />' % (PATHS[n], SOFTEN)
        for n, _, _ in STROKES)
    tsx = '''/* YSG Audio Labs 마크 — brand/build_brand.py 가 계산한 기하를 그대로 옮긴 것.
   ⚠ 좌표를 손으로 고치지 말 것. brand/build_brand.py 를 고쳐 다시 생성한다
     (흑백·컬러·아이콘·모션이 모두 같은 기하를 공유한다).

   컨셉: 중심에서 세 방향으로 뻗으며 끝으로 갈수록 얇아지는 획.
     · Y 스플리터 = 한 소스가 갈라진다 (오디오의 실제 개념) + YSG 의 Y
     · 얇아지는 굵기 = 거리에 따른 감쇠
     · 좌우 대칭 평평 마감 = 계측기의 마감 (둥근 끝은 '뿔' 로 보여 기각했다)
     · 세로로는 잉크 중심이 칸 중심에 오도록 원점을 올려 두었다 — 그래서
       세 획의 만나는 점은 12 가 아니다. 글자와 세로 중앙을 맞추기 위한 것이다

   색을 박지 않고 currentColor 만 쓴다 — 무채색·네온·라이트 세 테마에서
   글자색을 그대로 따라간다. */
export function YsgMark({ size = 26 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
%s
    </svg>
  );
}
''' % rows
    io.open(os.path.join(OUT, "YsgMark.tsx"), "w", encoding="utf-8").write(tsx)


# ── 3) 컬러 고도화 ─────────────────────────────────────────────────────────
def color_defs(prefix):
    """세 획에 각각 다른 그라디언트. 중심이 밝고 끝이 깊어진다 = 감쇠를 색으로도.
    tick(눈금)과 중심 발광은 계측 도구 정체성을 담는 장치다."""
    grads = []
    #  ⚠ 끝 색을 DEEP(#0B1230) 까지 내리면 배경 잉크(#070A0F)와 붙어 **획이 사라진다.**
    #    실제로 왼쪽 위 획이 검은 배경에서 안 보였다. INDIGO 까지만 내린다.
    ramps = {
        "down":    (CYAN, BLUE),
        "upleft":  (BLUE, INDIGO),
        "upright": (CYAN, BLUE),
    }
    for name, deg, end in STROKES:
        d = unit(deg)
        x1, y1 = CX, CY
        x2, y2 = CX + d[0] * end, CY + d[1] * end
        a, b = ramps[name]
        grads.append(
            '    <linearGradient id="%s-%s" gradientUnits="userSpaceOnUse"'
            ' x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f">'
            '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/>'
            '</linearGradient>' % (prefix, name, x1, y1, x2, y2, a, b))
    grads.append(
        '    <radialGradient id="%s-core" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="%s" stop-opacity="0.95"/>'
        '<stop offset="0.55" stop-color="%s" stop-opacity="0.35"/>'
        '<stop offset="1" stop-color="%s" stop-opacity="0"/>'
        '</radialGradient>' % (prefix, CYAN, CYAN, CYAN))
    return "\n".join(grads)


def color_body(prefix, ticks=True, glow=True):
    body = []
    if glow:
        body.append('    <circle cx="%.3f" cy="%.3f" r="7.4" fill="url(#%s-core)"/>'
                    % (CX, CY, prefix))
    for name, _, _ in STROKES:
        #  윤곽은 그라디언트가 아니라 **시안 고정**이다. 끝이 어두워져도 형태가
        #  남아야 한다 — fill 만 쓰면 감쇠 끝이 배경에 녹아 획이 잘려 보였다.
        body.append('    <path d="%s" fill="url(#%s-%s)"'
                    ' stroke="%s" stroke-opacity="0.42" stroke-width="0.38"'
                    ' stroke-linejoin="round"/>'
                    % (PATHS[name], prefix, name, CYAN))
    # 상단 엣지 하이라이트 — 획이 평면이 아니라 면처럼 보이게
    body.append('    <path d="%s" fill="none" stroke="#ffffff" stroke-opacity="0.20"'
                ' stroke-width="0.4" stroke-linejoin="round"/>' % PATHS["upright"])
    if ticks:
        # 획 끝 바로 밖에 아주 짧은 눈금 — 계측 도구의 표식. 대형에서만 읽힌다
        for name, deg, end in STROKES:
            d = unit(deg)
            p = (-d[1], d[0])
            base = (CX + d[0] * (end + 0.72), CY + d[1] * (end + 0.72))
            body.append('    <line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"'
                        ' stroke="%s" stroke-opacity="0.55" stroke-width="0.42"'
                        ' stroke-linecap="round"/>'
                        % (base[0] + p[0] * 0.72, base[1] + p[1] * 0.72,
                           base[0] - p[0] * 0.72, base[1] - p[1] * 0.72, CYAN))
        # 중심의 강조 한 점 — 소스. 앰버는 여기 한 곳에만 쓴다
        body.append('    <circle cx="%.3f" cy="%.3f" r="0.72" fill="%s"/>'
                    % (CX, CY, AMBER))
    return "\n".join(body)


def write_color():
    prefix = "ysgc"
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"'
           ' role="img" aria-label="YSG Audio Labs">\n'
           '  <defs>\n%s\n  </defs>\n%s\n</svg>\n'
           % (color_defs(prefix), color_body(prefix)))
    io.open(os.path.join(OUT, "ysg-mark-color.svg"), "w", encoding="utf-8").write(svg)


# ── 4) 앱 아이콘 (스퀘어 프레임) ───────────────────────────────────────────
def squircle(pad=0.0, r=6.4):
    x0, x1 = pad, 24 - pad
    return ('M %.2f %.2f L %.2f %.2f Q %.2f %.2f %.2f %.2f L %.2f %.2f'
            ' Q %.2f %.2f %.2f %.2f L %.2f %.2f Q %.2f %.2f %.2f %.2f'
            ' L %.2f %.2f Q %.2f %.2f %.2f %.2f Z'
            % (x0 + r, x0, x1 - r, x0, x1, x0, x1, x0 + r,
               x1, x1 - r, x1, x1, x1 - r, x1,
               x0 + r, x1, x0, x1, x0, x1 - r,
               x0, x0 + r, x0, x0, x0 + r, x0))


def write_icon():
    prefix = "ysgi"
    # 프레임 안에 들어가므로 마크를 조금 줄여 여백을 준다
    scale = 0.78
    #  축소 기준점은 **칸의 중심(12,12)** 이다 — 노드 원점(CX,CY)이 아니다.
    #  세로 중심 보정으로 잉크 중심이 이미 12 에 와 있으므로, 여기서 노드 원점을
    #  기준으로 줄이면 프레임 안에서 다시 아래로 밀린다.
    inner = ('<g transform="translate(%.3f %.3f) scale(%.3f)">\n%s\n    </g>'
             % (12.0 * (1 - scale), 12.0 * (1 - scale), scale,
                color_body(prefix, ticks=False, glow=True)))
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"'
           ' role="img" aria-label="YSG Audio Labs">\n'
           '  <defs>\n%s\n'
           '    <linearGradient id="%s-bg" x1="0" y1="0" x2="0" y2="1">'
           '<stop offset="0" stop-color="#101827"/><stop offset="1" stop-color="%s"/>'
           '</linearGradient>\n'
           '  </defs>\n'
           '  <path d="%s" fill="url(#%s-bg)"/>\n'
           '  <path d="%s" fill="none" stroke="%s" stroke-opacity="0.30"'
           ' stroke-width="0.5"/>\n'
           '  %s\n</svg>\n'
           % (color_defs(prefix), prefix, INK, squircle(0.6), prefix,
              squircle(0.85), CYAN, inner))
    io.open(os.path.join(OUT, "ysg-icon-color.svg"), "w", encoding="utf-8").write(svg)


# ── 5) 가로 조합 (마크 + 워드마크) ─────────────────────────────────────────
def write_logotype():
    prefix = "ysgl"
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 210 44"'
           ' role="img" aria-label="YSG Audio Labs">\n'
           '  <defs>\n%s\n  </defs>\n'
           '  <g transform="translate(2 10) scale(1.0)">\n%s\n  </g>\n'
           '  <text x="34" y="21" font-family="Inter, \'Segoe UI\', system-ui, sans-serif"'
           ' font-size="15" font-weight="700" letter-spacing="1.1" fill="#EAF2F6">YSG</text>\n'
           '  <text x="34" y="34" font-family="Inter, \'Segoe UI\', system-ui, sans-serif"'
           ' font-size="9.2" font-weight="600" letter-spacing="3.05" fill="#7E93A6">AUDIO TOOLS</text>\n'
           '</svg>\n' % (color_defs(prefix), color_body(prefix, ticks=False)))
    io.open(os.path.join(OUT, "ysg-logotype.svg"), "w", encoding="utf-8").write(svg)


# ── 6) 모션 (2.2초) ───────────────────────────────────────────────────────
def write_motion():
    """소개 페이지용 짧은 모션. GIF 가 아니라 SVG 안의 CSS 애니메이션이다 —
    `<img src="ysg-mark-motion.svg">` 로 넣어도 재생되고, 용량은 수 KB 다
    (지금 소개 페이지의 GIF 두 개가 23MB 인 것과 대비된다).

    연출 순서
      0.0s  중심 발광이 켜진다            — 소스가 살아난다
      0.25s 세 획이 중심에서 밖으로 자란다 — 신호가 공간으로 나간다 (0.12s 씩 시차)
      1.05s 획 끝 눈금이 순차 점등        — 도달·측정
      1.35s 중심 앰버 점이 한 번 맥동      — 확인
      2.2s  정지 상태로 유지 후 반복
    획이 '자라는' 것은 중심에서 퍼지는 원형 clip 으로 만든다 — 획 모양을 그대로
    쓰면서 성장만 표현할 수 있어 path 를 두 벌 관리하지 않는다. """
    prefix = "ysgm"
    tick_lines = []
    for i, (name, deg, end) in enumerate(STROKES):
        d = unit(deg)
        p = (-d[1], d[0])
        base = (CX + d[0] * (end + 0.72), CY + d[1] * (end + 0.72))
        tick_lines.append(
            '    <line class="tick t%d" x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"'
            ' stroke="%s" stroke-width="0.42" stroke-linecap="round"/>'
            % (i, base[0] + p[0] * 0.9, base[1] + p[1] * 0.9,
               base[0] - p[0] * 0.9, base[1] - p[1] * 0.9, CYAN))
    wedges = "\n".join(
        '      <path class="w w%d" d="%s" fill="url(#%s-%s)"/>'
        % (i, PATHS[name], prefix, name)
        for i, (name, _, _) in enumerate(STROKES))

    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
     role="img" aria-label="YSG Audio Labs">
  <defs>
%s
    <clipPath id="%s-grow"><circle cx="12" cy="12" r="12" class="grow"/></clipPath>
  </defs>
  <style>
    /* ⚠ 모든 keyframes 의 **0%% 를 완성 상태**로 둔다. 조금 뒤(4%%)에서 시작 상태로
       점프한 다음 다시 완성으로 간다.

       왜 이 순서인가: 애니메이션이 등록된 뒤 렌더가 진행되지 않는 상황(창이 가려짐,
       썸네일 캡처, 정적 렌더러)에서는 화면이 **첫 프레임에 멈춘다.** 처음에
       'r:0 / opacity:0' 같은 시작 상태를 두면 그 환경에서 로고가 아예 사라진다 —
       실제로 그렇게 만들어 두 번 빈 화면을 봤다. 0%% 를 완성으로 두면 멈춰도
       정지 로고가 남는다. 이 구조를 뒤집지 말 것. */
    @media (prefers-reduced-motion: reduce) {
      .grow, .core, .w, .tick, .dot { animation: none !important; }
    }

    .grow { animation: grow 2.4s cubic-bezier(.22,.9,.24,1) infinite; }
    @keyframes grow { 0%% { r: 13 } 4%% { r: 0 } 48%%,100%% { r: 13 } }

    .core { opacity: .8; transform-origin: 12px 12px;
            animation: core 2.4s ease-out infinite; }
    @keyframes core { 0%% { opacity:.8; transform:scale(1) }
                      4%% { opacity:0; transform:scale(.4) }
                      20%% { opacity:.95; transform:scale(1.06) }
                      36%%,100%% { opacity:.8; transform:scale(1) } }

    .w { opacity: 1; animation: fade 2.4s ease-out infinite; }
    .w0 { animation-delay: .10s } .w1 { animation-delay: .21s } .w2 { animation-delay: .32s }
    @keyframes fade { 0%% { opacity:1 } 4%% { opacity:0 } 26%%,100%% { opacity:1 } }

    .tick { opacity: .55; animation: tick 2.4s ease-out infinite; }
    .t0 { animation-delay: .88s } .t1 { animation-delay: .99s } .t2 { animation-delay: 1.10s }
    @keyframes tick { 0%% { opacity:.55 } 4%% { opacity:0 }
                      10%% { opacity:1 } 20%%,100%% { opacity:.55 } }

    .dot { opacity: 1; transform-origin: 12px 12px;
           animation: dot 2.4s ease-out infinite; animation-delay: 1.22s; }
    @keyframes dot { 0%% { opacity:1; transform:scale(1) }
                     4%% { opacity:0; transform:scale(.2) }
                     12%% { opacity:1; transform:scale(1.9) }
                     24%%,100%% { opacity:1; transform:scale(1) } }
  </style>

  <circle class="core" cx="12" cy="12" r="7.4" fill="url(#%s-core)"
          style="transform-origin:12px 12px"/>
  <g clip-path="url(#%s-grow)">
%s
  </g>
%s
  <circle class="dot" cx="12" cy="12" r="0.72" fill="%s"/>
</svg>
''' % (color_defs(prefix), prefix, prefix, prefix, wedges,
       "\n".join(tick_lines), AMBER)

    #  위 템플릿에는 중심 좌표가 `12` 로 박혀 있다 (발광·앰버점의 cx/cy, 성장 clip
    #  의 원, 그리고 CSS transform-origin). 세로 중심 보정 뒤로는 이것들이 모두
    #  **노드 원점(CX,CY)** 을 따라가야 한다 — 안 그러면 발광과 점만 아래에 남아
    #  획과 어긋난다. 개수를 확인해서 조용히 빗나가는 일이 없게 한다.
    center_attr = 'cx="12" cy="12"'
    origin_css = "12px 12px"
    assert svg.count(center_attr) == 3, svg.count(center_attr)   # 발광 · 성장clip · 점
    assert svg.count(origin_css) == 3, svg.count(origin_css)     # core · dot · style
    svg = svg.replace(center_attr, 'cx="%.3f" cy="%.3f"' % (CX, CY))
    svg = svg.replace(origin_css, "%.3fpx %.3fpx" % (CX, CY))

    io.open(os.path.join(OUT, "ysg-mark-motion.svg"), "w", encoding="utf-8").write(svg)


write_mono()
write_tsx()
write_color()
write_icon()
write_logotype()
write_motion()


# ── 7) 웹용 — 파비콘 · 작은 단색 마크 ─────────────────────────────────────
def write_web():
    """파비콘과 허브 상단바용.

    파비콘은 **배경을 넣는다.** 브라우저 탭 색은 사용자 테마에 따라 밝을 수도
    어두울 수도 있어서, 투명 배경에 currentColor 를 쓰면 한쪽에서 사라진다.

    상단바 마크는 18px 로 아주 작게 들어가므로 발광·눈금을 뺀 **단색**이다 —
    그 크기에서 그라디언트는 뭉쳐 보이고 눈금은 사라진다."""
    prefix = "ysgf"
    scale = 128 / 24.0
    inner = ('<g transform="scale(%.4f)">\n%s\n  </g>'
             % (scale, color_body(prefix, ticks=False, glow=True)))
    favicon = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128"'
               ' role="img" aria-label="YSG Audio Labs">\n'
               '  <defs>\n%s\n'
               '    <linearGradient id="%s-bg" x1="0" y1="0" x2="0" y2="1">'
               '<stop offset="0" stop-color="#141C2B"/>'
               '<stop offset="1" stop-color="%s"/></linearGradient>\n'
               '  </defs>\n'
               '  <rect width="128" height="128" rx="28" fill="url(#%s-bg)"/>\n'
               '  %s\n</svg>\n'
               % (color_defs(prefix), prefix, INK, prefix, inner))
    io.open(os.path.join(OUT, "ysg-favicon.svg"), "w", encoding="utf-8").write(favicon)

    web = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"'
           ' role="img" aria-label="YSG Audio Labs">\n%s\n</svg>\n' % mono_body())
    io.open(os.path.join(OUT, "ysg-mark-web.svg"), "w", encoding="utf-8").write(web)


write_web()

made = ["ysg-mark-mono.svg", "YsgMark.tsx", "ysg-mark-color.svg",
        "ysg-icon-color.svg", "ysg-logotype.svg", "ysg-mark-motion.svg",
        "ysg-favicon.svg", "ysg-mark-web.svg"]
print("확정 파라미터: reach=%.1f(공통) w0=%.1f w1=%.1f spread=%.0f° 대칭평평"
      % (REACH, W0, W1, SPREAD))
for f in made:
    size = os.path.getsize(os.path.join(OUT, f))
    print("  %-24s %6d bytes" % (f, size))
