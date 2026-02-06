<template>
  <div class="login-button">
    <button
      v-if="!user && !loading"
      @click.prevent="login"
      class="login-button__btn"
      type="button"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
        <polyline points="10 17 15 12 10 7" />
        <line x1="15" y1="12" x2="3" y2="12" />
      </svg>
      登录
    </button>
    <div v-else-if="user" class="login-button__user">
      <img
        :src="user.avatar_url"
        :alt="user.username"
        class="login-button__avatar"
      />
      <span class="login-button__username">{{ user.username }}</span>
      <button @click="logout" class="login-button__logout">登出</button>
    </div>
    <div v-else class="login-button__loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { useAuth } from "../composables/useAuth";

const { user, loading, login, logout } = useAuth();
</script>

<style scoped>
.login-button {
  display: flex;
  align-items: center;
  gap: 8px;
}

.login-button__btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  border: 1px solid var(--vp-c-divider);
  border-radius: 999px;
  cursor: pointer;
  font-size: 14px;
  transition: border-color 0.2s, background 0.2s, color 0.2s;
}

.login-button__btn:hover {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
  background: var(--vp-c-bg-alt);
}

.login-button__user {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 6px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 999px;
}

.login-button__avatar {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 1px solid var(--vp-c-divider);
}

.login-button__username {
  font-size: 14px;
  color: var(--vp-c-text-1);
  max-width: 110px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.login-button__logout {
  padding: 4px 8px;
  background: transparent;
  color: var(--vp-c-text-2);
  border: none;
  border-radius: 999px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.login-button__logout:hover {
  color: var(--vp-c-text-1);
  background: var(--vp-c-bg-alt);
}

.login-button__loading {
  font-size: 14px;
  color: var(--vp-c-text-2);
}
</style>
