---
title: kaleidx_scope：Phase1（青门）
editLink: true
---

# Phase 1（青门）

<script setup>
import { onMounted } from "vue";

onMounted(() => {
  const cards = Array.from(document.querySelectorAll(".kaleidx-card"));
  const countEl = document.querySelector("#kaleidx-complete-count");
  const exportBtn = document.querySelector("#kaleidx-export-btn");
  const importBtn = document.querySelector("#kaleidx-import-btn");
  const setCardState = (card, key, checked) => {
    const checkbox = card.querySelector("input[type='checkbox']");
    if (checked) {
      localStorage.setItem(key, "1");
      card.classList.add("is-checked");
      if (checkbox) checkbox.checked = true;
      return;
    }
    localStorage.removeItem(key);
    card.classList.remove("is-checked");
    if (checkbox) checkbox.checked = false;
  };
  const updateCount = () => {
    const checked = cards.filter((card) =>
      card.classList.contains("is-checked")
    ).length;
    const total = cards.length;
    if (countEl) {
      countEl.textContent = `${checked} / ${total}`;
    }
  };

  cards.forEach((card, index) => {
    const titleEl = card.querySelector(".kaleidx-card__title");
    const title = titleEl ? titleEl.textContent.trim() : `song-${index + 1}`;
    const key = `kaleidx_phase1_${title}`;

    const label = document.createElement("label");
    label.className = "kaleidx-check";

    const input = document.createElement("input");
    input.type = "checkbox";
    input.checked = localStorage.getItem(key) === "1";

    const box = document.createElement("span");
    box.className = "kaleidx-check__box";

    label.append(input, box);
    card.appendChild(label);

    if (input.checked) {
      card.classList.add("is-checked");
    }

    input.addEventListener("change", () => {
      if (input.checked) {
        setCardState(card, key, true);
      } else {
        setCardState(card, key, false);
      }
      updateCount();
    });
  });

  updateCount();

  if (exportBtn) {
    exportBtn.addEventListener("click", async () => {
      const picked = cards
        .filter((card) => card.classList.contains("is-checked"))
        .map((card, index) => {
          const titleEl = card.querySelector(".kaleidx-card__title");
          return titleEl ? titleEl.textContent.trim() : `song-${index + 1}`;
        });
      const payload = btoa(unescape(encodeURIComponent(JSON.stringify(picked))));
      try {
        await navigator.clipboard.writeText(payload);
        exportBtn.textContent = "已复制";
        setTimeout(() => {
          exportBtn.textContent = "导出";
        }, 1200);
      } catch {
        prompt("复制失败，请手动复制：", payload);
      }
    });
  }

  if (importBtn) {
    importBtn.addEventListener("click", () => {
      const input = prompt("粘贴导入码：");
      if (!input) return;
      try {
        const decoded = JSON.parse(
          decodeURIComponent(escape(atob(input.trim())))
        );
        const set = new Set(Array.isArray(decoded) ? decoded : []);
        cards.forEach((card, index) => {
          const titleEl = card.querySelector(".kaleidx-card__title");
          const title = titleEl
            ? titleEl.textContent.trim()
            : `song-${index + 1}`;
          const key = `kaleidx_phase1_${title}`;
        setCardState(card, key, set.has(title));
        });
        updateCount();
      } catch {
        alert("导入失败：格式不正确");
      }
    });
  }
});
</script>

::: warning 引文
君はどんな 結末を願っていた？

你究竟 期待着怎样的结局？
:::

::: info 解锁条件
1. 完走 [skystreet6](/areas/skystreet6) 区域
2. 游玩以下区域的全部歌曲，共 29 首
:::

::: tip 青门有关区域
青春区域（天空街区域）：
- 青春区域（dx 的青春区域 + dx plus 的两个区域），由于这三个区域均未提供详细背景故事，所以统称为青春区域（skystreet0 区域）
- [skystreet1](/areas/skystreet), [skystreet2](/areas/skystreet2), [skystreet3](/areas/skystreet3), [skystreet4](/areas/skystreet4), [skystreet5](/areas/skystreet5), [skystreet6](/areas/skystreet6) 区域
:::

<div class="kaleidx-hero">
  <img src="/src/images/kaleidx_scope/phase1/phase1-bg.png" alt="Phase 1">
  <div class="kaleidx-stat-float">
    <div class="kaleidx-stat-float__num" id="kaleidx-complete-count">0</div>
    <div class="kaleidx-stat-float__label">已完成歌曲数</div>
    <div class="kaleidx-stat-actions">
      <button class="kaleidx-stat-btn" id="kaleidx-export-btn">导出</button>
      <button class="kaleidx-stat-btn" id="kaleidx-import-btn">导入</button>
    </div>
  </div>
</div>



## 青春区域（skystreet0 区域）

<div class="kaleidx-grid">
  <div class="kaleidx-card">
    <img src="/src/images/kaleidx_scope/phase1/11008.png" alt="Crazy Circle">
    <div class="kaleidx-card__title">Crazy Circle</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/kaleidx_scope/phase1/11009.png" alt="STEREOCSCAPE">
    <div class="kaleidx-card__title">STEREOCSCAPE</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/kaleidx_scope/phase1/11097.png" alt="ブレインジャックシンドローム">
    <div class="kaleidx-card__title">ブレインジャックシンドローム</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/kaleidx_scope/phase1/11098.png" alt="共鸣">
    <div class="kaleidx-card__title">共鸣</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/kaleidx_scope/phase1/11099.png" alt="Ututu">
    <div class="kaleidx-card__title">Ututu</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/kaleidx_scope/phase1/11100.png" alt="シエルブルーマルシェ">
    <div class="kaleidx-card__title">シエルブルーマルシェ</div>
  </div>
</div>

## スカイストリートちほー1（skystreet1 区域）

<div class="kaleidx-grid">
  <div class="kaleidx-card">
    <img src="/src/images/skystreet/skystreet-01.png" alt="REAL VOICE">
    <div class="kaleidx-card__title">REAL VOICE</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/skystreet/skystreet-02.png" alt="ユメヒバナ">
    <div class="kaleidx-card__title">ユメヒバナ</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/skystreet/skystreet-03.png" alt="オリフィス">
    <div class="kaleidx-card__title">オリフィス</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/skystreet/skystreet-04.png" alt="パラボラ">
    <div class="kaleidx-card__title">パラボラ</div>
  </div>
</div>

## スカイストリートちほー2（skystreet2 区域）

<div class="kaleidx-grid">
  <div class="kaleidx-card">
    <img src="/src/images/skystreet2/skystreet2-1.png" alt="星めぐり、果ての君へ。">
    <div class="kaleidx-card__title">星めぐり、果ての君へ。</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/skystreet2/skystreet2-2.png" alt="スローアライズ">
    <div class="kaleidx-card__title">スローアライズ</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/skystreet2/skystreet2-4.png" alt="生命不詳">
    <div class="kaleidx-card__title">生命不詳</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/skystreet2/skystreet2-3.png" alt="チエルカ／エソテリカ">
    <div class="kaleidx-card__title">チエルカ／エソテリカ</div>
  </div>
</div>

## スカイストリートちほー3（skystreet3 区域）

<div class="kaleidx-grid">
  <div class="kaleidx-card">
    <img src="/src/images/skystreet3/skystreet3-1.png" alt="RIFFRAIN">
    <div class="kaleidx-card__title">RIFFRAIN</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/skystreet3/skystreet3-2.png" alt="Falling">
    <div class="kaleidx-card__title">Falling</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/skystreet3/skystreet3-3.png" alt="ピリオドサイン">
    <div class="kaleidx-card__title">ピリオドサイン</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/skystreet3/skystreet3-4.png" alt="群青シグナル">
    <div class="kaleidx-card__title">群青シグナル</div>
  </div>
</div>

## スカイストリートちほー4（skystreet4 区域）

<div class="kaleidx-grid">
  <div class="kaleidx-card">
    <img src="/src/images/skystreet4/skystreet4-1.png" alt="アンバークロニクル">
    <div class="kaleidx-card__title">アンバークロニクル</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/skystreet4/skystreet4-2.png" alt="リフヴェイン">
    <div class="kaleidx-card__title">リフヴェイン</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/skystreet4/skystreet4-3.png" alt="宵の鳥">
    <div class="kaleidx-card__title">宵の鳥</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/skystreet4/skystreet4-4.png" alt="Kairos">
    <div class="kaleidx-card__title">Kairos</div>
  </div>
</div>

## スカイストリートちほー5（skystreet5 区域）

<div class="kaleidx-grid">
  <div class="kaleidx-card">
    <img src="/src/images/skystreet5/skystreet5-1.png" alt="フェイクフェイス・フェイルセイフ">
    <div class="kaleidx-card__title">フェイクフェイス・フェイルセイフ</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/skystreet5/skystreet5-2.png" alt="シックスプラン">
    <div class="kaleidx-card__title">シックスプラン</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/skystreet5/skystreet5-3.png" alt="フタタビ">
    <div class="kaleidx-card__title">フタタビ</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/skystreet5/skystreet5-4.png" alt="ふらふらふら、">
    <div class="kaleidx-card__title">ふらふらふら、</div>
  </div>
</div>

## スカイストリートちほー6（skystreet6 区域）

<div class="kaleidx-grid">
  <div class="kaleidx-card">
    <img src="/src/images/skystreet6/skystreet6-1.png" alt="パラドクスイヴ">
    <div class="kaleidx-card__title">パラドクスイヴ</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/skystreet6/skystreet6-2.png" alt="YKWTD">
    <div class="kaleidx-card__title">YKWTD</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/skystreet6/skystreet6-3.png" alt="184億回のマルチトニック">
    <div class="kaleidx-card__title">184億回のマルチトニック</div>
  </div>
</div>
