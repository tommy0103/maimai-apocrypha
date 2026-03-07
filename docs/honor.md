---
title: 贡献荣誉榜
editLink: true
---

<script setup>
import contributors from "./data/contributors.json";

const tierFor = (count) => {
  if (count >= 15) {
    return { label: "核心贡献者", cls: "honor-badge--core" };
  }
  if (count >= 10) {
    return { label: "长期贡献者", cls: "honor-badge--major" };
  }
  if (count >= 5) {
    return { label: "活跃贡献者", cls: "honor-badge--active" };
  }
  return { label: "贡献者", cls: "honor-badge--base" };
};

const sorted = [...contributors].sort((a, b) => (b.count || 0) - (a.count || 0));
const totalContributors = sorted.length;
const totalEntries = sorted.reduce((sum, item) => sum + (item.count || 0), 0);
</script>

欢迎来到贡献荣誉榜。所有帮助翻译/校对/整理的朋友都会记录在这里，现在的页面是 demo 页面，欢迎各位积极贡献内容。

如果你想加入，先看看 [贡献翻译与勘误](/contribute) 的说明。

<div class="honor-stats">
  <div class="honor-stat">
    <div class="honor-stat__num">{{ totalContributors }}</div>
    <div class="honor-stat__label">贡献者数量</div>
  </div>
  <div class="honor-stat">
    <div class="honor-stat__num">{{ totalEntries }}</div>
    <div class="honor-stat__label">累计贡献条目</div>
  </div>
</div>

<div v-if="sorted.length === 0" class="honor-empty">
  暂无贡献记录。欢迎第一位贡献者出现。
</div>

<div v-else class="honor-grid">
  <div v-for="person in sorted" :key="person.name" class="honor-card">
    <div class="honor-card__head">
      <div class="honor-card__identity">
        <img
          v-if="person.avatar"
          class="honor-avatar"
          :src="person.avatar"
          :alt="person.name"
          loading="lazy"
        >
        <div class="honor-card__name">{{ person.name }}</div>
      </div>
      <div class="honor-card__count">{{ person.count || 0 }}</div>
    </div>
    <div class="honor-card__meta">
      <span class="honor-badge" :class="tierFor(person.count || 0).cls">
        {{ tierFor(person.count || 0).label }}
      </span>
      <span v-if="person.role" class="honor-role">{{ person.role }}</span>
    </div>
  </div>
</div>

