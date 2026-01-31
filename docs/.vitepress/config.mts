import { defineConfig } from "vitepress";

export default defineConfig({
  title: "Maimai Apocrypha",
  description: "maimai story archive",
  themeConfig: {
    nav: [
      { text: "主页", link: "/" },
      { text: "关于", link: "/about" },
    ],

    sidebar: [
      {
        text: "区域剧情 (Areas)",
        items: [
          // 这里手动填一下你生成的那个文件名，之后可以写脚本自动生成这个列表
          { text: "7sRef 区域", link: "/areas/7sref" },
          { text: "7sRef2 区域", link: "/areas/7sref2" },
          { text: "7sRef3 区域", link: "/areas/7sref3" },
          { text: "7sRef4 区域", link: "/areas/7sref4" },
          //   { text: "HapiFes 区域", link: "/areas/hapifes" },
        ],
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
