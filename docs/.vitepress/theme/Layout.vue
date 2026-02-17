<template>
  <Layout>
    <template #nav-bar-content-after>
      <div class="nav-login">
        <LoginButton />
      </div>
    </template>
    <template #sidebar-nav-before> <!-- plugin custom sidebar -->
      <CustomSidebar />
    </template>
  </Layout>
</template>

<script setup>
import DefaultTheme from "vitepress/theme";
import LoginButton from "./components/LoginButton.vue";
import CustomSidebar from "./components/CustomSidebar.vue";
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
