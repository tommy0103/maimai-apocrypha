import { defineConfig } from "vitepress";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export default defineConfig({
  // base: "/maimai-apocrypha/",
  // base: process.env.VERCEL ?  "/" : "/maimai-apocrypha/",
  base: "/",
  title: "Maimai Apocrypha",
  description: "maimai story archive",
  vite: {
    envDir: resolve(__dirname, "../../"),
    ssr: {
      noExternal: ["vitepress-plugin-nprogress"],
    },
  },
  themeConfig: {
    nav: [
      { text: "主页", link: "/" },
      { text: "关于", link: "/about" },
      { text: "贡献翻译与勘误", link: "/contribute" },
      { text: "贡献荣誉榜", link: "/honor" },
    ],
    search: {
      provider: "local",
      options: {
        detailedView: true,
        miniSearch: {
          options: {
            tokenize: (text) => {
              // 先去掉所有引号再分词
              return text.replace(/['']/g, '').toLowerCase().split(/\s+/)
            }
          },
          searchOptions: {
            fuzzy: 0.2,
            prefix: true,
            weights: {
              fuzzy: 0.2,
              prefix: 0.4,
            },
          },
        },
      },
    },

    // sidebar 内容由 CustomSidebar.vue 在客户端渲染
    // 此处保留最小配置使 VitePress 渲染 sidebar 容器
    sidebar: [{ text: "", items: [] }],

    socialLinks: [
      {
        icon: "github",
        link: "https://github.com/tommy0103/maimai-apocrypha",
      },
    ],
  },
});
