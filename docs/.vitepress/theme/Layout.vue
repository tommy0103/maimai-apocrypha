<template>
  <Layout>
    <template #nav-bar-content-after>
      <div class="nav-login">
        <LoginButton />
      </div>
    </template>
  </Layout>
</template>

<script setup>
import DefaultTheme from "vitepress/theme";
import LoginButton from "./components/LoginButton.vue";
import { onMounted } from 'vue';

const { Layout } = DefaultTheme;

onMounted(() => {
  const mod = '@vercel/' + 'analytics';
  import(/* @vite-ignore */ mod).then(({ inject }) => inject()).catch(() => {});
});
</script>

<style>
.nav-login {
  display: flex;
  align-items: center;
  margin-left: 12px;
}
</style>
