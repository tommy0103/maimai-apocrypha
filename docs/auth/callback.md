---
title: 登录回调
layout: home
---

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vitepress';

const router = useRouter();

onMounted(() => {
  // The token is handled by useAuth composable
  // Redirect to home after a short delay
  setTimeout(() => {
    router.go('/');
  }, 1000);
});
</script>

<div style="text-align: center; padding: 40px 20px;">
  <p>正在完成登录...</p>
</div>
