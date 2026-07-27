<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { api } from '../../wiki/api.js';

const props = defineProps({
  modelValue: { type: Number, default: null }, // image_id
});
const emit = defineEmits(['update:modelValue']);
const { t } = useI18n();

const uploading = ref(false);
const error = ref('');
const fileInput = ref(null);

function readAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

async function onFileChange(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  error.value = '';
  if (!file.type.startsWith('image/')) {
    error.value = t('wiki.imageUpload.invalid');
    return;
  }
  if (file.size > 8 * 1024 * 1024) {
    error.value = t('wiki.imageUpload.tooLarge');
    return;
  }
  uploading.value = true;
  try {
    const dataUrl = await readAsDataUrl(file);
    const res = await api.uploadImage(dataUrl);
    emit('update:modelValue', res.id);
  } catch (e) {
    error.value = e.message || t('wiki.imageUpload.failed');
  } finally {
    uploading.value = false;
    if (fileInput.value) fileInput.value.value = '';
  }
}

function clearImage() {
  emit('update:modelValue', null);
}
</script>

<template>
  <div>
    <div
      class="relative rounded-xl border-2 border-dashed border-gray-200 dark:border-dark-elevated overflow-hidden"
    >
      <img
        v-if="modelValue"
        :src="api.imageUrl(modelValue)"
        alt=""
        class="w-full h-48 object-cover"
      />
      <div v-else class="h-48 flex flex-col items-center justify-center text-gray-400 gap-2">
        <i class="fas fa-image text-3xl"></i>
        <span class="text-sm">{{ t('wiki.imageUpload.hint') }}</span>
      </div>

      <div
        v-if="uploading"
        class="absolute inset-0 bg-black/40 flex items-center justify-center text-white"
      >
        <i class="fas fa-spinner fa-spin text-2xl"></i>
      </div>
    </div>

    <div class="flex items-center gap-3 mt-2">
      <label
        class="cursor-pointer text-sm px-3 py-1.5 rounded-lg gradient-bg text-white font-medium hover:opacity-90 transition"
      >
        <i class="fas fa-upload mr-1"></i>{{ t('wiki.imageUpload.choose') }}
        <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onFileChange" />
      </label>
      <button
        v-if="modelValue"
        type="button"
        class="text-sm text-gray-500 hover:text-red-500 transition"
        @click="clearImage"
      >
        <i class="fas fa-trash mr-1"></i>{{ t('wiki.imageUpload.remove') }}
      </button>
    </div>
    <p v-if="error" class="text-sm text-red-500 mt-1">{{ error }}</p>
  </div>
</template>
