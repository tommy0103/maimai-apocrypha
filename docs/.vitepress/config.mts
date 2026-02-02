import { defineConfig } from "vitepress";
import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

function loadAreaSidebar() {
  try {
    const indexPath = resolve(__dirname, "../public/area_index.json");
    const fileContent = readFileSync(indexPath, "utf-8");
    const areas = JSON.parse(fileContent);
    const normalized = areas.map((area) => ({
      id: area.id,
      text: area.text ?? area.name ?? area.id,
      version: area.version ?? "unknown",
    }));

    const grouped = new Map();
    for (const area of normalized) {
      const version = area.version || "unknown";
      if (!grouped.has(version)) {
        grouped.set(version, []);
      }
      grouped.get(version).push(area);
    }

    const versionGroups = Array.from(grouped.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([version, items]) => ({
        text: version,
        items: items
          .sort((a, b) => a.id.localeCompare(b.id))
          .map((area) => ({
            text: `${area.text}（${area.id} 区域）`,
            link: `/areas/${area.id}`,
          })),
      }));

    return versionGroups;
  } catch (e) {
    console.error(
      "⚠️ 无法自动生成侧边栏，请检查 public/area_index.json 是否存在。",
      e
    );
  }
}

const sidebarAreas = loadAreaSidebar();

export default defineConfig({
  // base: "/maimai-apocrypha/",
  base: process.env.VERCEL ?  "/" : "/maimai-apocrypha/",
  title: "Maimai Apocrypha",
  description: "maimai story archive",
  themeConfig: {
    nav: [
      { text: "主页", link: "/" },
      { text: "关于", link: "/about" },
      { text: "贡献翻译", link: "/contribute" },
    ],

    sidebar: [
      {
        text: "区域剧情 (Areas)",
        items: sidebarAreas,
        // items: [
        //   // 这里手动填一下你生成的那个文件名，之后可以写脚本自动生成这个列表
        //   { text: "7sRef 区域", link: "/areas/7sref" },
        //   { text: "7sRef2 区域", link: "/areas/7sref2" },
        //   { text: "7sRef3 区域", link: "/areas/7sref3" },
        //   { text: "7sRef4 区域", link: "/areas/7sref4" },
        //   //   { text: "HapiFes 区域", link: "/areas/hapifes" },
        // ],
      },
    ],

    socialLinks: [
      {
        icon: "github",
        link: "https://github.com/tommy0103/maimai-apocrypha",
      },
    ],
  },
});
