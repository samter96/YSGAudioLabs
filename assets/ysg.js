/* ============================================================
   YSG Audio Labs — 공용 스크립트

   허브와 제품 페이지가 함께 쓴다. 페이지마다 복사하지 말 것.

   하는 일
     1. 등장 효과 (`.rise`) — JS 가 살아 있을 때만 켠다. 반대로 만들면
        스크립트가 죽는 순간 본문이 통째로 사라진다
     2. 안전망 — 관찰자 콜백이 안 뛰는 환경(렌더가 진행되지 않는 창)에서도
        1.2초 뒤엔 무조건 드러낸다. 실제로 빈 화면을 본 적이 있다
     3. 파형 막대 개수 — 컨테이너 폭에서 정한다. 고정하면 좁은 화면에서
        막대의 최소폭이 문서를 가로로 넘치게 만든다 (실측으로 걸렸다)
     4. 제품 박스 포인터 기울기 — hover 가 있는 기기에서만
     5. 캡처 자동 대지 — `assets/v2/` 에 파일이 있으면 표시, 없으면 자리표시 유지
     6. KO/EN 토글 — `data-en` 속성 하나로. 선택자 표를 다시 만들지 말 것

   ⚠ 히어로에는 `.rise` 를 붙이지 않는다. 첫 화면을 JS 에 맡기면 스크립트가
     안 뛰는 환경에서 페이지가 빈 화면으로 열린다.
   ============================================================ */
"use strict";
(function(){
  /* JS 가 살아 있을 때만 등장 효과를 켠다.
     ⚠ 반대로 만들면(기본을 숨김) JS 가 죽는 순간 본문이 통째로 사라진다. */
  document.documentElement.classList.add('js');

  var reduce = false;
  try{ reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches; }catch(e){}

  /* 등장 — 같은 줄의 카드들은 조금씩 시차를 준다 */
  var rises = document.querySelectorAll('.rise');
  if(reduce || !('IntersectionObserver' in window)){
    rises.forEach(function(el){ el.classList.add('in'); });
  }else{
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if(!e.isIntersecting) return;
        var sibs = Array.prototype.slice.call(e.target.parentNode.children);
        var i = sibs.indexOf(e.target);
        e.target.style.transitionDelay = Math.min(i, 4) * 70 + 'ms';
        e.target.classList.add('in');
        io.unobserve(e.target);
      });
    }, {threshold:.06, rootMargin:'0px 0px -6% 0px'});
    rises.forEach(function(el){ io.observe(el); });
    /* 안전망. 이 미리보기 창처럼 렌더가 진행되지 않는 환경에서 관찰자 콜백이
       안 뛴 적이 있다. 그러면 본문이 통째로 안 보인다 — 실제로 당했다.
       setTimeout 은 그런 상황에서도 뛰므로 1.2초 뒤엔 무조건 드러낸다. */
    setTimeout(function(){
      rises.forEach(function(el){ el.classList.add('in'); });
    }, 1200);
  }

  /* 파형 막대 — 높이·속도를 조금씩 흩어 기계적으로 안 보이게 */
  var bars = document.querySelector('.bars');
  if(bars){
    /* 좁은 화면에서 막대가 실오라기처럼 되지 않게 개수를 폭에서 정한다 */
    var n = Math.max(20, Math.min(56, Math.round(bars.clientWidth / 8))), html = '';
    for(var i=0;i<n;i++){
      var d = (i * 37 % 100) / 100;
      html += '<i style="animation-delay:' + (-d * 1.5).toFixed(2) + 's;'
            + 'animation-duration:' + (1.1 + d * .9).toFixed(2) + 's;'
            + 'opacity:' + (.55 + d * .4).toFixed(2) + '"></i>';
    }
    bars.innerHTML = html;
  }

  /* 제품 박스 — 포인터를 따라 살짝 기운다 (터치·감소모드에서는 끔) */
  var box = document.getElementById('box');
  if(box && !reduce && window.matchMedia('(hover:hover)').matches){
    var scene = box.closest('.pkg');
    scene.addEventListener('pointermove', function(ev){
      var r = scene.getBoundingClientRect();
      var dx = (ev.clientX - r.left) / r.width - .5;
      var dy = (ev.clientY - r.top) / r.height - .5;
      box.style.animation = 'none';
      box.style.transform = 'rotateX(' + (6 - dy * 10).toFixed(2) + 'deg) '
                          + 'rotateY(' + (-25 + dx * 16).toFixed(2) + 'deg)';
    });
    scene.addEventListener('pointerleave', function(){
      box.style.animation = '';
      box.style.transform = '';
    });
  }

  /* 캡처 자동 대지 — assets/v2/ 에 파일이 있으면 표시, 없으면 자리표시를 남긴다.
     ⚠ 자리표시가 보이는 것은 오류가 아니다. 촬영 대기 상태다. */
  document.querySelectorAll('img[data-src]').forEach(function(im){
    var probe = new Image();
    probe.onload = function(){
      im.src = im.getAttribute('data-src');
      im.classList.add('loaded');
      var fig = im.closest('[data-shot]');
      if(fig){ fig.classList.add('loaded'); }
    };
    probe.src = im.getAttribute('data-src');
  });

  var y = document.getElementById('year');
  if(y){ y.textContent = '© ' + new Date().getFullYear() + ' YSG Audio Labs'; }

  /* 상단바 개발자 소개 — 본문 섹션이 아니라 작은 창으로 띄운다. */
  document.addEventListener('click', function(ev){
    var btn = ev.target.closest('[data-dialog-open]');
    if(!btn) return;
    var dlg = document.getElementById(btn.getAttribute('data-dialog-open'));
    if(!dlg) return;
    ev.preventDefault();
    if(!dlg.__ysgDialogReady){
      dlg.__ysgDialogReady = true;
      dlg.addEventListener('click', function(e){
        if(e.target === dlg){ dlg.hidden = true; }
      });
      dlg.querySelectorAll('[data-dialog-close]').forEach(function(close){
        close.addEventListener('click', function(){ dlg.hidden = true; btn.focus({preventScroll:true}); });
      });
      dlg.addEventListener('keydown', function(e){
        if(e.key === 'Escape'){ dlg.hidden = true; btn.focus({preventScroll:true}); }
      });
    }
    if(dlg.hidden){
      var sx = window.scrollX;
      var sy = window.scrollY;
      dlg.hidden = false;
      var close = dlg.querySelector('[data-dialog-close]');
      if(close){ close.focus({preventScroll:true}); }
      window.scrollTo(sx, sy);
    }
  });

  /* KO / EN — `data-en` 속성 하나로 끝낸다.
     이전 판은 선택자→영문 문자열 표를 86KB JS 로 들고 있어서, 마크업을 조금만
     고쳐도 번역이 조용히 어긋났다.

     고른 언어는 localStorage 에 남긴다. 허브와 제품 페이지가 같은 출처라 한 번
     고르면 페이지를 옮겨도 따라온다 — 예전에는 페이지마다 KO 로 되돌아갔다.
     ⚠ 저장값이 없으면 KO 다. 브라우저 언어를 보고 자동으로 정하지 않는다.
       한국어 지면이 기본이고, 영어는 고른 사람에게만 따라다닌다. */
  var LANG_KEY = 'ysg-lang';
  function readLang(){
    /* 사생활 보호 모드나 저장소 차단 환경에서는 접근 자체가 던진다.
       그때는 그냥 KO 로 두고 넘어간다 — 언어 토글은 계속 동작한다. */
    try{ return localStorage.getItem(LANG_KEY) === 'en'; }catch(e){ return false; }
  }
  function saveLang(en){
    try{ localStorage.setItem(LANG_KEY, en ? 'en' : 'ko'); }catch(e){}
  }

  var langBtn = document.querySelector('.langswitch');
  var isEN = readLang();
  var originalHTML = new WeakMap();
  function applyLang(en){
    document.querySelectorAll('[data-en]').forEach(function(el){
      if(!originalHTML.has(el)){ originalHTML.set(el, el.innerHTML); }
      el.innerHTML = en ? el.getAttribute('data-en') : originalHTML.get(el);
    });
    document.body.classList.toggle('lang-en', en);
    document.documentElement.setAttribute('lang', en ? 'en' : 'ko');
    if(langBtn){ langBtn.setAttribute('aria-pressed', en ? 'true' : 'false'); }
  }
  /* 저장된 값이 EN 일 때만 손댄다. KO 면 마크업이 이미 KO 라 건드릴 게 없다.
     ⚠ 이 호출이 originalHTML 캐시를 채우므로 어떤 치환보다 먼저 와야 한다. */
  if(isEN){ applyLang(true); }
  if(langBtn){
    langBtn.addEventListener('click', function(){
      isEN = !isEN;
      saveLang(isEN);
      applyLang(isEN);
    });
  }
})();
