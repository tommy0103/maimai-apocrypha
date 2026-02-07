// docs/.vitepress/theme/index.ts
import DefaultTheme from "vitepress/theme";
import Layout from "./Layout.vue";
import LoginButton from "./components/LoginButton.vue";
import vitepressNprogress from "vitepress-plugin-nprogress";
import "vitepress-plugin-nprogress/lib/css/index.css";
import "./style.css";

export default {
  extends: DefaultTheme,
  Layout,
  enhanceApp({ app }) {
    app.component("LoginButton", LoginButton);
    if (typeof DefaultTheme.enhanceApp === "function") {
      DefaultTheme.enhanceApp({ app });
    }
    vitepressNprogress({ app });
  },
};
