<template>
  <div class="min-h-screen flex items-center justify-center bg-transparent">
    <div class="max-w-md w-full space-y-8 p-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg relative z-10 backdrop-blur-sm bg-opacity-90 dark:bg-opacity-90 animate-fade-in">
      <div>
        <h2 class="text-center text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#e384c7] to-[#9e6593]">
          Sign in to Shared Markdown
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-300">
          Collaborate in real-time
        </p>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="space-y-4">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Username
            </label>
            <input
              id="username"
              v-model="username"
              name="username"
              type="text"
              required
              class="appearance-none relative block w-full px-4 py-3 border border-gray-300 dark:border-gray-600 placeholder-gray-400 dark:placeholder-gray-500 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-[#e384c7] focus:border-transparent bg-white dark:bg-gray-700 transition-all duration-200"
              placeholder="Enter your username"
            />
          </div>
          <div>
            <label for="identifier" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Identifier
            </label>
            <input
              id="identifier"
              v-model="identifier"
              name="identifier"
              type="password"
              required
              class="appearance-none relative block w-full px-4 py-3 border border-gray-300 dark:border-gray-600 placeholder-gray-400 dark:placeholder-gray-500 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-[#e384c7] focus:border-transparent bg-white dark:bg-gray-700 transition-all duration-200"
              placeholder="Enter your identifier"
            />
          </div>
        </div>

        <div v-if="error" class="text-red-500 text-sm text-center bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">
          {{ error }}
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading"
            class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-[#e384c7] to-[#9e6593] hover:from-[#d674b7] hover:to-[#8e5583] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#e384c7] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-[1.02]"
          >
            <span v-if="!loading">Sign in</span>
            <span v-else class="flex items-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Signing in...
            </span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const username = ref('');
const identifier = ref('');
const error = ref('');
const loading = ref(false);

// Check if already logged in on mount
onMounted(() => {
  const existingToken = localStorage.getItem('sm_token');
  if (existingToken) {
    // Already logged in, redirect to shared markdown
    router.push('/sm');
  }
});

const handleLogin = async () => {
  error.value = '';
  loading.value = true;

  try {
    const response = await fetch('/sm-api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        identifier: identifier.value,
      }),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || 'Login failed');
    }

    const data = await response.json();
    
    // Store token and username
    localStorage.setItem('sm_token', data.token);
    localStorage.setItem('sm_username', data.username);
    
    // Redirect to shared markdown editor
    router.push('/sm');
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.6s ease-in-out forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
