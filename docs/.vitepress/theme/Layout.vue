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
import { inject } from '@vercel/analytics';

const { Layout } = DefaultTheme;

onMounted(() => {
  inject();
});
</script>

<style>
.nav-login {
  display: flex;
  align-items: center;
  margin-left: 12px;
}
</style>
