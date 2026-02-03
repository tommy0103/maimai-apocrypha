---
# https://vitepress.dev/reference/default-theme-home-page
layout: home

hero:
  name: "Maimai Apocrypha"
  text: "非官方剧情汉化归档"
  tagline: "本不该交会的世界在此折射、变形..."
  #   image:
  #     src: /src/images/7sref4/7sref4-7.png # <--- 找一张好看的洗衣机或者角色透明图
  #     alt: Maimai DX
  actions:
    - theme: brand
      text: "开始阅读"
      link: /areas/7sref
    # - theme: alt
    #   text: "kaleidx_scope"
    #   link: /kaleidx_scope/phase1
    # - theme: alt
    #   text: "贡献翻译"
    #   link: /contribute
---

<section class="home-section">
  <div class="home-grid">
    <div class="home-card home-card--cute">
      <div class="home-card__badge-row">
        <div class="home-card__badge">剧情归档</div>
        <img class="home-card__badge-icon home-card__badge-icon--right" src="/src/images/7sref.png" alt="7sref">
      </div>
      <h3 class="home-card__title">区域剧情 (Areas)</h3>
      <p class="home-card__desc">按区域阅读完整剧情，提供中文翻译与日语原文对照。</p>
      <div class="home-card__actions">
        <a class="VPButton brand" href="/areas/7sref">从 7sRef 开始</a>
      </div>
    </div>
    <div class="home-card home-card--cute">
      <div class="home-card__badge-row">
        <div class="home-card__badge">万花筒解密</div>
        <img class="home-card__badge-icon home-card__badge-icon--right" src="/src/images/phase1.png" alt="phase1">
      </div>
      <h3 class="home-card__title">万花筒 (kaleidx_scope)</h3>
      <p class="home-card__desc">提供解锁条件与歌曲清单，快速定位需要完成的任务。</p>
      <div class="home-card__actions">
        <a class="VPButton brand" href="/kaleidx_scope/phase1">Phase 1</a>
        <!-- <a class="VPButton alt" href="/kaleidx_scope/phase2">Phase 2</a> -->
      </div>
    </div>
  </div>
</section>

<section class="home-section">
  <h2 class="home-section__title">贡献流程</h2>
  <div class="home-steps">
    <div class="home-step">
      <div class="home-step__num">01</div>
      <div class="home-step__title">选择区域</div>
      <div class="home-step__desc">打开任意区域页面，确认待补充内容。</div>
    </div>
    <div class="home-step">
      <div class="home-step__num">02</div>
      <div class="home-step__title">提交翻译</div>
      <div class="home-step__desc">通过表单或 PR 提交翻译内容。</div>
    </div>
    <div class="home-step">
      <div class="home-step__num">03</div>
      <div class="home-step__title">合并发布</div>
      <div class="home-step__desc">审核通过后合并，站点自动更新。</div>
    </div>
  </div>
  <div class="home-center">
    <a class="VPButton brand" href="/contribute">查看贡献方式</a>
  </div>
</section>
