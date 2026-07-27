<script setup>
import { ref } from 'vue';

const url = ref('');
const format = ref('mp3');
const loading = ref(false);
const downloadUrl = ref('');
const error = ref('');

async function convert() {
  error.value = '';
  downloadUrl.value = '';
  if (!url.value) {
    error.value = 'Please enter a valid YouTube URL.';
    return;
  }
  loading.value = true;
  try {
    // Use the real backend endpoint
    const response = await fetch('https://magenta.jetzt/rockapi/convert_url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url.value, format: format.value }),
    });
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      error.value = data.detail || 'Conversion failed.';
      throw new Error('Conversion failed');
    }
    const data = await response.json();
    downloadUrl.value = data.downloadUrl || '#';
  } catch (e) {
    if (!error.value) error.value = 'Failed to convert. Please try again.';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen bg-transparent">
    <div class="max-w-2xl mx-auto px-4 py-12">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 md:p-8 relative z-10 backdrop-blur-sm bg-opacity-90 dark:bg-opacity-90">
        <h1 class="text-3xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-[#e384c7] to-[#9e6593] animate-fade-in">
          Convert YouTube to MP3/MP4
        </h1>
        <p class="text-gray-600 dark:text-gray-300 mb-8 italic animate-fade-in">
          Enter a YouTube link below and select your desired format.
        </p>
        <form @submit.prevent="convert" class="space-y-6 animate-fade-in">
          <div>
            <label class="block text-gray-700 dark:text-gray-200 mb-2 font-medium">YouTube URL</label>
            <input
              v-model="url"
              type="url"
              placeholder="https://youtube.com/watch?v=..."
              class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-[#e384c7] transition"
              required
            />
          </div>
          <div>
            <label class="block text-gray-700 dark:text-gray-200 mb-2 font-medium">Format</label>
            <div class="flex space-x-4">
              <label class="flex items-center space-x-2">
                <input type="radio" v-model="format" value="mp3" class="accent-[#e384c7]" />
                <span>MP3</span>
              </label>
              <label class="flex items-center space-x-2">
                <input type="radio" v-model="format" value="mp4" class="accent-[#e384c7]" />
                <span>MP4</span>
              </label>
            </div>
          </div>
          <div>
            <button
              type="submit"
              class="w-full py-3 px-6 rounded-lg bg-gradient-to-r from-[#e384c7] to-[#9e6593] text-white font-semibold shadow-lg hover:from-[#d16ba5] hover:to-[#7f5a83] transition disabled:opacity-60"
              :disabled="loading"
            >
              Convert
            </button>
          </div>
        </form>
        <div v-if="error" class="mt-4 text-red-500 animate-fade-in">{{ error }}</div>
        <div v-if="loading" class="flex flex-col items-center mt-8 animate-fade-in">
          <svg class="animate-spin h-10 w-10 text-[#e384c7] mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
          </svg>
          <span class="text-gray-600 dark:text-gray-300">Converting, please wait...</span>
        </div>
        <div v-if="downloadUrl && !loading" class="flex flex-col items-center mt-8 animate-fade-in">
          <a
            :href="downloadUrl"
            class="py-3 px-8 rounded-lg bg-gradient-to-r from-[#e384c7] to-[#9e6593] text-white font-semibold shadow-lg hover:from-[#d16ba5] hover:to-[#7f5a83] transition"
            download
          >
            Download {{ format.toUpperCase() }}
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.6s ease-in-out forwards;
  opacity: 0;
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
