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

const { Layout } = DefaultTheme;
</script>

<style>
.nav-login {
  display: flex;
  align-items: center;
  margin-left: 12px;
}
</style>
