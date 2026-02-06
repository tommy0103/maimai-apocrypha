// docs/.vitepress/theme/index.ts
import DefaultTheme from "vitepress/theme";
import Layout from "./Layout.vue";
import LoginButton from "./components/LoginButton.vue";
import "./style.css";

export default {
  extends: DefaultTheme,
  Layout,
  enhanceApp({ app }) {
    app.component("LoginButton", LoginButton);
  },
};
