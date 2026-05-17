---
title: kaleidx_scope phase4
editLink: true
---

# Phase 4（黑门）

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
          const key = `kaleidx_phase4_${title}`;
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

「KING of Performai」の栄冠を手にするのは誰だ！？

谁将夺得「KING of Performai」的桂冠？！

3、2、1、スタート！

3，2，1，开始！

:::

::: info 解锁条件

- 看到门的条件（解锁黑门的前提）：完走 [metropolis 9 区域](/areas/metropolis9)，完走之后可以发现黑之门

- 拿到钥匙的条件：在通常模式下游玩一次所有 KING of Performai 预选新曲和决胜乐曲，列表如下（没有难度和成绩要求，跳关、段位认定、宴谱面和自由模式无效）

::: tip 黑门有关区域
大都会区域：[metropolis3](/areas/metropolis3), [metropolis4](/areas/metropolis4), [metropolis5](/areas/metropolis5), [metropolis6](/areas/metropolis6), [metropolis7](/areas/metropolis7), [metropolis8](/areas/metropolis8), [metropolis9](/areas/metropolis9) 区域
:::

<div class="kaleidx-hero">
  <img src="/src/images/kaleidx_scope/phase4/phase4-bg.webp" alt="Phase 4">
  <div class="kaleidx-stat-float">
    <div class="kaleidx-stat-float__num" id="kaleidx-complete-count">0</div>
    <div class="kaleidx-stat-float__label">已完成歌曲数</div>
    <div class="kaleidx-stat-actions">
      <button class="kaleidx-stat-btn" id="kaleidx-export-btn">导出</button>
      <button class="kaleidx-stat-btn" id="kaleidx-import-btn">导入</button>
    </div>
  </div>
</div>

## KING of Performai 2019

<div class="kaleidx-grid">
  <div class="kaleidx-card">
    <img src="/src/images/kaleidx_scope/phase4/kop2019-1.jpg" alt="Blows Up Everything">
    <div class="kaleidx-card__title">Blows Up Everything</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/kaleidx_scope/phase4/kop2019-2.jpg" alt="Valsqotch">
    <div class="kaleidx-card__title">Valsqotch</div>
  </div>
</div>

## KING of Performai 2020

<div class="kaleidx-grid">
  <div class="kaleidx-card">
    <img src="/src/images/kaleidx_scope/phase4/kop2020-1.jpg" alt="≠彡”/了→">
    <div class="kaleidx-card__title">≠彡”/了→</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/kaleidx_scope/phase4/kop2020-2.jpg" alt="BREaK! BREaK! BREaK!">
    <div class="kaleidx-card__title">BREaK! BREaK! BREaK!</div>
  </div>
</div>

## KING of Performai 3rd
  
<div class="kaleidx-grid">
  <div class="kaleidx-card">
    <img src="/src/images/kaleidx_scope/phase4/kop2021-1.jpg" alt="U&iVERSE -銀河鸞翔">
    <div class="kaleidx-card__title">U&amp;iVERSE -銀河鸞翔-</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/kaleidx_scope/phase4/kop2021-2.jpg" alt="GIGANTØMAKHIA">
    <div class="kaleidx-card__title">GIGANTØMAKHIA</div>
  </div>
</div>

## KING of Performai 4th
  
<div class="kaleidx-grid">
  <div class="kaleidx-card">
    <img src="/src/images/kaleidx_scope/phase4/kop2022-1.jpg" alt="Rising on the horizon">
    <div class="kaleidx-card__title">Rising on the horizon</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/kaleidx_scope/phase4/kop2022-2.jpg" alt="ViRTUS">
    <div class="kaleidx-card__title">ViRTUS</div>
  </div>
</div>

## KING of Performai 5th
  
<div class="kaleidx-grid">
  <div class="kaleidx-card">
    <img src="/src/images/kaleidx_scope/phase4/kop2023-1.jpg" alt="KHYMΞXΛ">
    <div class="kaleidx-card__title">KHYMΞXΛ</div>
  </div>
  <div class="kaleidx-card">
    <img src="/src/images/kaleidx_scope/phase4/kop2023-2.jpg" alt="系ぎて">
    <div class="kaleidx-card__title">系ぎて</div>
  </div>
</div>

## KING of Performai 6th
  
<div class="kaleidx-grid">
  <div class="kaleidx-card">
    <img src="/src/images/kaleidx_scope/phase4/kop2024-1.jpg" alt="Divide et impera!">
    <div class="kaleidx-card__title">Divide et impera!</div>
  </div>
</div>
