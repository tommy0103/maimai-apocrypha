<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter, withBase } from "vitepress";

const route = useRoute();
const router = useRouter();

const areas = ref([]);
const groupMode = ref("version");
const collapsedState = ref({});
const loaded = ref(false);

const VERSION_ORDER = [
  "circle",
  "prismplus",
  "prism",
  "buddiesplus",
  "buddies",
  "festivalplus",
  "festival",
  "universeplus",
  "universe",
  "splashplus",
  "splash",
];

const VERSION_LABELS = {
  circle: "CiRCLE",
  prismplus: "PRiSM PLUS",
  prism: "PRiSM",
  buddiesplus: "BUDDiES PLUS",
  buddies: "BUDDiES",
  festivalplus: "FESTiVAL PLUS",
  festival: "FESTiVAL",
  universeplus: "UNiVERSE PLUS",
  universe: "UNiVERSE",
  splashplus: "Splash PLUS",
  splash: "Splash",
};

const COLLAPSE_DEFAULTS = {
  _areas: false,
  kaleidx: false,
  contribute: true,
};

const STATIC_GROUPS = [
  {
    key: "kaleidx",
    label: "万花筒 (kaleidx_scope)",
    items: [
      { text: "Phase 1（青门）", link: "/kaleidx_scope/phase1" },
      { text: "Phase 2（白门）", link: "/kaleidx_scope/phase2" },
    ],
  },
  {
    key: "contribute",
    label: "贡献",
    items: [
      { text: "贡献翻译与勘误", link: "/contribute" },
      { text: "贡献荣誉榜", link: "/honor" },
    ],
  },
];

function getSeriesKey(id) {
  return id.replace(/\d+$/, "");
}

function getTrailingNum(id) {
  const m = id.match(/(\d+)$/);
  return m ? parseInt(m[1]) : 0;
}

function getSeriesLabel(items) {
  if (items.length > 0) {
    return items[0].text.replace(/\d+$/, "").trim();
  }
  return "";
}

function makeItem(area) {
  return {
    text: `${area.text}（${area.id} 区域）`,
    link: `/areas/${area.id}`,
  };
}

const areaGroups = computed(() => {
  if (groupMode.value === "version") {
    const grouped = new Map();
    for (const area of areas.value) {
      const ver = area.version || "unknown";
      if (!grouped.has(ver)) grouped.set(ver, []);
      grouped.get(ver).push(area);
    }
    return Array.from(grouped.entries())
      .sort(([a], [b]) => { // increasing order
        const ai = VERSION_ORDER.indexOf(a);
        const bi = VERSION_ORDER.indexOf(b);
        return (ai === -1 ? 999 : ai) - (bi === -1 ? 999 : bi);
      })
      .map(([ver, items]) => ({
        key: `v_${ver}`,
        label: VERSION_LABELS[ver] || ver,
        items: items.sort((a, b) => a.id.localeCompare(b.id)).map(makeItem),
      }));
  }

  const grouped = new Map();
  for (const area of areas.value) {
    const series = getSeriesKey(area.id);
    if (!grouped.has(series)) grouped.set(series, []);
    grouped.get(series).push(area);
  }
  return Array.from(grouped.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([series, items]) => {
      items.sort((a, b) => getTrailingNum(a.id) - getTrailingNum(b.id));
      return {
        key: `s_${series}`,
        label: `${series} 系列（${getSeriesLabel(items)}）`,
        items: items.map(makeItem),
      };
    });
});

function isCollapsed(key) {
  if (key in collapsedState.value) return collapsedState.value[key];
  if (key in COLLAPSE_DEFAULTS) return COLLAPSE_DEFAULTS[key];
  return true;
}

function toggleGroup(key) {
  collapsedState.value[key] = !isCollapsed(key);
  saveState();
}

function switchMode(mode) {
  groupMode.value = mode;
  saveState();
}

function saveState() {
  if (typeof localStorage === "undefined") return;
  localStorage.setItem("cs_mode", groupMode.value);
  localStorage.setItem("cs_collapsed", JSON.stringify(collapsedState.value));
}

function isActive(link) {
  const p = route.path;
  return p === link || p === link + ".html" || p === link + "/";
}

function navigate(link) {
  router.go(withBase(link));
}

onMounted(async () => {
  try {
    const savedMode = localStorage.getItem("cs_mode");
    if (savedMode === "version" || savedMode === "series") {
      groupMode.value = savedMode;
    }
    const savedCollapsed = localStorage.getItem("cs_collapsed");
    if (savedCollapsed) {
      collapsedState.value = JSON.parse(savedCollapsed);
    }
  } catch {}

  try {
    const res = await fetch(withBase("/area_index.json"));
    areas.value = await res.json();
  } catch (e) {
    console.error("Failed to load area_index.json:", e);
  }

  loaded.value = true;
});
</script>

<template>
  <div class="custom-sidebar" v-if="loaded">
    <!-- 排序切换 -->
    <div class="cs-toggle">
      <button
        :class="['cs-toggle-btn', { active: groupMode === 'version' }]"
        @click="switchMode('version')"
      >
        按版本
      </button>
      <button
        :class="['cs-toggle-btn', { active: groupMode === 'series' }]"
        @click="switchMode('series')"
      >
        按系列
      </button>
    </div>

    <!-- 区域剧情 -->
    <div class="cs-section">
      <button class="cs-head" @click="toggleGroup('_areas')">
        <span
          :class="['cs-arrow', { open: !isCollapsed('_areas') }]"
        >›</span>
        <span class="cs-head-text">区域剧情</span>
      </button>
      <div v-show="!isCollapsed('_areas')" class="cs-body">
        <div v-for="g in areaGroups" :key="g.key" class="cs-group">
          <button class="cs-group-head" @click="toggleGroup(g.key)">
            <span
              :class="['cs-arrow', { open: !isCollapsed(g.key) }]"
            >›</span>
            <span class="cs-group-label">{{ g.label }}</span>
            <span class="cs-count">{{ g.items.length }}</span>
          </button>
          <ul v-show="!isCollapsed(g.key)" class="cs-list">
            <li v-for="item in g.items" :key="item.link">
              <a
                :href="withBase(item.link)"
                :class="['cs-link', { active: isActive(item.link) }]"
                @click.prevent="navigate(item.link)"
              >{{ item.text }}</a>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 静态分组（万花筒、贡献） -->
    <div v-for="sg in STATIC_GROUPS" :key="sg.key" class="cs-section">
      <button class="cs-head" @click="toggleGroup(sg.key)">
        <span
          :class="['cs-arrow', { open: !isCollapsed(sg.key) }]"
        >›</span>
        <span class="cs-head-text">{{ sg.label }}</span>
      </button>
      <ul v-show="!isCollapsed(sg.key)" class="cs-list cs-list--top">
        <li v-for="item in sg.items" :key="item.link">
          <a
            :href="withBase(item.link)"
            :class="['cs-link', { active: isActive(item.link) }]"
            @click.prevent="navigate(item.link)"
          >{{ item.text }}</a>
        </li>
      </ul>
    </div>
  </div>
</template>
