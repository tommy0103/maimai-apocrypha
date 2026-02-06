import { ref, onMounted } from "vue";

interface User {
  user_id: number;
  username: string;
  avatar_url: string;
}

const user = ref<User | null>(null);
const loading = ref(true);

const getApiBase = () => {
  if (typeof window === "undefined") {
    return "";
  }
  return import.meta.env.PROD ? window.location.origin : "http://localhost:5173";
};

export function useAuth() {
  const checkAuth = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      loading.value = false;
      return false;
    }

    try {
      const response = await fetch(`${getApiBase()}/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        user.value = data;
        loading.value = false;
        return true;
      } else {
        localStorage.removeItem("token");
        user.value = null;
        loading.value = false;
        return false;
      }
    } catch (error) {
      console.error("Auth check failed:", error);
      localStorage.removeItem("token");
      user.value = null;
      loading.value = false;
      return false;
    }
  };

  const login = () => {
    // Try multiple ways to get client ID
    const clientId =
      import.meta.env.VITE_GITHUB_CLIENT_ID ||
      import.meta.env.GITHUB_CLIENT_ID ||
      (typeof window !== "undefined" &&
        (window as any).__GITHUB_CLIENT_ID__);

    if (!clientId) {
      alert(
        "GitHub Client ID 未配置\n\n请检查：\n1. .env.local 文件是否存在\n2. 是否包含 VITE_GITHUB_CLIENT_ID\n3. 是否重启了开发服务器"
      );
      return;
    }

    const redirectUri = `${getApiBase()}/api/auth/callback`;
    const githubAuthUrl = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${encodeURIComponent(
      redirectUri
    )}&scope=read:user`;

    window.location.href = githubAuthUrl;
  };

  const logout = () => {
    localStorage.removeItem("token");
    user.value = null;
    window.location.reload();
  };

  // Handle OAuth callback
  const handleCallback = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get("token");

    if (token) {
      localStorage.setItem("token", token);
      // Remove token from URL
      const newUrl = window.location.pathname;
      window.history.replaceState({}, "", newUrl);
      // Check auth to load user data
      checkAuth();
    }
  };

  onMounted(() => {
    // Check if this is a callback page
    if (window.location.pathname === "/auth/callback") {
      handleCallback();
    } else {
      checkAuth();
    }
  });

  return {
    user,
    loading,
    login,
    logout,
    checkAuth,
  };
}
