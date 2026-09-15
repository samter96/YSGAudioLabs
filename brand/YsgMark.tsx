/* YSG Audio Labs 마크 — brand/build_brand.py 가 계산한 기하를 그대로 옮긴 것.
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
      <path d="M 9.400 9.785 L 11.400 19.685 L 12.600 19.685 L 14.600 9.785 Z"
            fill="currentColor" stroke="currentColor"
            strokeWidth={0.45} strokeLinejoin="round" />
      <path d="M 13.300 7.533 L 3.726 4.315 L 3.126 5.354 L 10.700 12.036 Z"
            fill="currentColor" stroke="currentColor"
            strokeWidth={0.45} strokeLinejoin="round" />
      <path d="M 13.300 12.036 L 20.874 5.354 L 20.274 4.315 L 10.700 7.533 Z"
            fill="currentColor" stroke="currentColor"
            strokeWidth={0.45} strokeLinejoin="round" />
    </svg>
  );
}
