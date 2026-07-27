<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { api } from '../../wiki/api.js';
import { auth, completeLogin } from '../../wiki/auth.js';

const router = useRouter();
const { t } = useI18n();

// step: 'login' | 'password' | 'totp_setup' | 'totp' | 'recovery'
const step = ref('login');
const loading = ref(false);
const error = ref('');

const username = ref('');
const password = ref('');
const newPassword = ref('');
const newPassword2 = ref('');
const code = ref('');

const totpSetup = ref(null); // { secret, otpauth_uri, qr_png }
const recoveryCodes = ref([]);

onMounted(() => {
  // Already authenticated (silent refresh) -> straight to dashboard.
  if (auth.ready && auth.isAuthenticated) {
    router.replace({ name: 'WikiAdminDashboard' });
  }
});

function advance(pending) {
  const next = pending[0];
  if (next === 'password_change') step.value = 'password';
  else if (next === 'totp_setup') startTotpSetup();
  else step.value = 'totp';
}

async function submitLogin() {
  error.value = '';
  loading.value = true;
  try {
    const res = await api.login(username.value, password.value);
    advance(res.pending);
  } catch (e) {
    error.value = e.status === 429 ? e.message : t('wiki.admin.login.invalid');
  } finally {
    loading.value = false;
  }
}

async function submitPassword() {
  error.value = '';
  if (newPassword.value !== newPassword2.value) {
    error.value = t('wiki.admin.login.passwordMismatch');
    return;
  }
  loading.value = true;
  try {
    const res = await api.challengePassword(newPassword.value);
    advance(res.pending);
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}

async function startTotpSetup() {
  error.value = '';
  loading.value = true;
  try {
    totpSetup.value = await api.totpInit();
    step.value = 'totp_setup';
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}

async function submitTotpSetup() {
  error.value = '';
  loading.value = true;
  try {
    const session = await api.totpVerify(code.value);
    completeLogin(session);
    recoveryCodes.value = session.recovery_codes || [];
    code.value = '';
    step.value = 'recovery';
  } catch (e) {
    error.value = t('wiki.admin.login.invalidCode');
  } finally {
    loading.value = false;
  }
}

async function submitMfa() {
  error.value = '';
  loading.value = true;
  try {
    const session = await api.mfa(code.value);
    completeLogin(session);
    router.replace({ name: 'WikiAdminDashboard' });
  } catch (e) {
    error.value = t('wiki.admin.login.invalidCode');
  } finally {
    loading.value = false;
  }
}

function finishRecovery() {
  router.replace({ name: 'WikiAdminDashboard' });
}

function copyRecovery() {
  navigator.clipboard?.writeText(recoveryCodes.value.join('\n'));
}

function downloadRecovery() {
  const blob = new Blob([recoveryCodes.value.join('\n') + '\n'], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'platepal-wiki-recovery-codes.txt';
  a.click();
  URL.revokeObjectURL(url);
}
</script>

<template>
  <div class="max-w-md mx-auto">
    <div class="text-center mb-8">
      <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl gradient-bg mb-4 shadow-lg">
        <i class="fas fa-lock text-white text-2xl"></i>
      </div>
      <h1 class="text-2xl font-bold gradient-text">{{ t('wiki.admin.login.title') }}</h1>
    </div>

    <div class="bg-white dark:bg-dark-surface rounded-2xl shadow-lg p-6 wiki-fade-in">
      <!-- Step: credentials -->
      <form v-if="step === 'login'" @submit.prevent="submitLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1">{{ t('wiki.admin.login.username') }}</label>
          <input v-model="username" type="text" autocomplete="username" required
            class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-dark-elevated bg-white dark:bg-dark-bg focus:ring-2 focus:ring-primary focus:outline-none" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">{{ t('wiki.admin.login.password') }}</label>
          <input v-model="password" type="password" autocomplete="current-password" required
            class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-dark-elevated bg-white dark:bg-dark-bg focus:ring-2 focus:ring-primary focus:outline-none" />
        </div>
        <button type="submit" :disabled="loading"
          class="w-full py-2.5 rounded-xl gradient-bg text-white font-semibold hover:opacity-90 transition disabled:opacity-50">
          <i v-if="loading" class="fas fa-spinner fa-spin mr-2"></i>{{ t('wiki.admin.login.submit') }}
        </button>
      </form>

      <!-- Step: forced password change -->
      <form v-else-if="step === 'password'" @submit.prevent="submitPassword" class="space-y-4">
        <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('wiki.admin.login.changeHint') }}</p>
        <div>
          <label class="block text-sm font-medium mb-1">{{ t('wiki.admin.login.newPassword') }}</label>
          <input v-model="newPassword" type="password" autocomplete="new-password" required
            class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-dark-elevated bg-white dark:bg-dark-bg focus:ring-2 focus:ring-primary focus:outline-none" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">{{ t('wiki.admin.login.confirmPassword') }}</label>
          <input v-model="newPassword2" type="password" autocomplete="new-password" required
            class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-dark-elevated bg-white dark:bg-dark-bg focus:ring-2 focus:ring-primary focus:outline-none" />
        </div>
        <button type="submit" :disabled="loading"
          class="w-full py-2.5 rounded-xl gradient-bg text-white font-semibold hover:opacity-90 transition disabled:opacity-50">
          <i v-if="loading" class="fas fa-spinner fa-spin mr-2"></i>{{ t('wiki.admin.login.setPassword') }}
        </button>
      </form>

      <!-- Step: TOTP setup (QR) -->
      <form v-else-if="step === 'totp_setup'" @submit.prevent="submitTotpSetup" class="space-y-4">
        <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('wiki.admin.login.totpSetupHint') }}</p>
        <div v-if="totpSetup" class="flex flex-col items-center gap-3">
          <img :src="totpSetup.qr_png" alt="TOTP QR" class="w-44 h-44 rounded-xl border border-gray-100 dark:border-dark-elevated" />
          <code class="text-xs bg-gray-100 dark:bg-dark-bg px-3 py-1.5 rounded-lg break-all select-all">{{ totpSetup.secret }}</code>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">{{ t('wiki.admin.login.enterCode') }}</label>
          <input v-model="code" type="text" inputmode="numeric" autocomplete="one-time-code" required
            class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-dark-elevated bg-white dark:bg-dark-bg text-center tracking-widest focus:ring-2 focus:ring-primary focus:outline-none" />
        </div>
        <button type="submit" :disabled="loading"
          class="w-full py-2.5 rounded-xl gradient-bg text-white font-semibold hover:opacity-90 transition disabled:opacity-50">
          <i v-if="loading" class="fas fa-spinner fa-spin mr-2"></i>{{ t('wiki.admin.login.enableTotp') }}
        </button>
      </form>

      <!-- Step: TOTP verify (returning) -->
      <form v-else-if="step === 'totp'" @submit.prevent="submitMfa" class="space-y-4">
        <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('wiki.admin.login.totpHint') }}</p>
        <div>
          <label class="block text-sm font-medium mb-1">{{ t('wiki.admin.login.enterCode') }}</label>
          <input v-model="code" type="text" inputmode="numeric" autocomplete="one-time-code" required
            class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-dark-elevated bg-white dark:bg-dark-bg text-center tracking-widest focus:ring-2 focus:ring-primary focus:outline-none" />
        </div>
        <button type="submit" :disabled="loading"
          class="w-full py-2.5 rounded-xl gradient-bg text-white font-semibold hover:opacity-90 transition disabled:opacity-50">
          <i v-if="loading" class="fas fa-spinner fa-spin mr-2"></i>{{ t('wiki.admin.login.verify') }}
        </button>
        <p class="text-xs text-gray-400 text-center">{{ t('wiki.admin.login.recoveryHint') }}</p>
      </form>

      <!-- Step: recovery codes display -->
      <div v-else-if="step === 'recovery'" class="space-y-4">
        <div class="text-center">
          <i class="fas fa-shield-halved text-3xl text-primary mb-2"></i>
          <h2 class="font-bold text-lg">{{ t('wiki.admin.login.recoveryTitle') }}</h2>
          <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('wiki.admin.login.recoveryWarning') }}</p>
        </div>
        <div class="grid grid-cols-2 gap-2 bg-gray-50 dark:bg-dark-bg rounded-xl p-4 font-mono text-sm">
          <span v-for="c in recoveryCodes" :key="c" class="select-all">{{ c }}</span>
        </div>
        <div class="flex gap-2">
          <button type="button" @click="downloadRecovery"
            class="flex-1 py-2 rounded-xl border border-gray-200 dark:border-dark-elevated hover:bg-gray-50 dark:hover:bg-dark-bg transition text-sm font-medium">
            <i class="fas fa-download mr-1"></i>{{ t('wiki.admin.login.download') }}
          </button>
          <button type="button" @click="copyRecovery"
            class="flex-1 py-2 rounded-xl border border-gray-200 dark:border-dark-elevated hover:bg-gray-50 dark:hover:bg-dark-bg transition text-sm font-medium">
            <i class="fas fa-copy mr-1"></i>{{ t('wiki.admin.login.copy') }}
          </button>
        </div>
        <button type="button" @click="finishRecovery"
          class="w-full py-2.5 rounded-xl gradient-bg text-white font-semibold hover:opacity-90 transition">
          {{ t('wiki.admin.login.savedContinue') }}
        </button>
      </div>

      <p v-if="error" class="text-sm text-red-500 mt-4 text-center">{{ error }}</p>
    </div>
  </div>
</template>
