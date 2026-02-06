---
title: 贡献荣誉榜
editLink: true
---

<script setup>
import contributors from "./data/contributors.json";

const tierFor = (count) => {
  if (count >= 15) {
    return { label: "核心贡献者", cls: "badge-core" };
  }
  if (count >= 10) {
    return { label: "长期贡献者", cls: "badge-major" };
  }
  if (count >= 5) {
    return { label: "活跃贡献者", cls: "badge-active" };
  }
  return { label: "贡献者", cls: "badge-base" };
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

<style>
.honor-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin: 18px 0 12px;
}
.honor-stat {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 12px 14px;
  text-align: center;
}
.honor-stat__num {
  font-size: 1.6em;
  font-weight: 700;
}
.honor-stat__label {
  font-size: 0.9em;
  opacity: 0.7;
}
.honor-empty {
  margin: 16px 0;
  padding: 12px 14px;
  border-radius: 10px;
  background: var(--vp-c-bg-soft);
  border: 1px dashed var(--vp-c-divider);
  color: var(--vp-c-text-2);
}
.honor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  margin: 16px 0;
}
.honor-card {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 12px 14px;
}
.honor-card__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.honor-card__identity {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.honor-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg-alt);
}
.honor-card__name {
  font-weight: 600;
  font-size: 1.05em;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.honor-card__count {
  font-weight: 700;
  color: var(--vp-c-brand-1);
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
  margin-left: 8px;
  max-width: 45%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.honor-card__meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  flex-wrap: wrap;
}
.honor-badge {
  font-size: 0.8em;
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg-alt);
}
.honor-role {
  font-size: 0.85em;
  color: var(--vp-c-text-2);
}
.badge-core {
  background: rgba(255, 210, 94, 0.2);
  border-color: rgba(255, 210, 94, 0.4);
}
.badge-major {
  background: rgba(120, 200, 255, 0.18);
  border-color: rgba(120, 200, 255, 0.4);
}
.badge-active {
  background: rgba(130, 255, 190, 0.16);
  border-color: rgba(130, 255, 190, 0.4);
}
.badge-base {
  background: rgba(255, 255, 255, 0.1);
}
</style>
