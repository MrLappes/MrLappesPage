<template>
  <div class="min-h-screen bg-transparent">
    <!-- Header -->
    <div class="sticky top-0 z-40 bg-white dark:bg-gray-800 shadow-md transition-all duration-300 bg-opacity-90 dark:bg-opacity-90 backdrop-blur-sm">
      <div class="container mx-auto px-4 py-4 flex justify-between items-center">
        <h1 class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#e384c7] to-[#9e6593]">
          Shared Markdown Editor
        </h1>
        <div class="flex items-center gap-4">
          <span class="text-sm text-gray-600 dark:text-gray-300 flex items-center">
            <i class="fas fa-user-circle mr-2"></i>{{ username }}
          </span>
          <button
            @click="logout"
            class="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-red-500 to-red-600 rounded-lg hover:from-red-600 hover:to-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-all duration-200 transform hover:scale-105"
          >
            <i class="fas fa-sign-out-alt mr-1"></i> Logout
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container mx-auto px-4 py-6">
      <div class="grid grid-cols-12 gap-6 h-[calc(100vh-140px)]">
        <!-- Left Sidebar - Document List -->
        <!-- Desktop: normal sidebar, Mobile: hidden (opened via modal) -->
        <div 
          class="hidden lg:block lg:col-span-3 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 overflow-y-auto relative backdrop-blur-sm bg-opacity-90 dark:bg-opacity-90 animate-fade-in"
        >
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-100">
              <i class="fas fa-folder-open mr-2 text-[#e384c7]"></i>Documents
            </h2>
            <button
              @click="showCreateDialog = true"
              class="p-2 text-white bg-gradient-to-r from-[#e384c7] to-[#9e6593] hover:from-[#d674b7] hover:to-[#8e5583] rounded-full transition-all duration-200 transform hover:scale-110 shadow-md"
              title="Create new document"
            >
              <i class="fas fa-plus"></i>
            </button>
          </div>

          <div class="space-y-2">
            <div
              v-for="doc in documents"
              :key="doc.id"
              class="p-3 rounded-lg transition-all duration-200 transform hover:scale-[1.02] relative group"
              :class="selectedDocId === doc.id 
                ? 'bg-gradient-to-r from-[#e384c7] to-[#9e6593] text-white shadow-md' 
                : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 hover:shadow'"
            >
              <div @click="selectDocument(doc.id)" class="cursor-pointer">
                <div class="font-medium flex items-center">
                  <i class="fas fa-file-alt mr-2" :class="selectedDocId === doc.id ? 'text-white' : 'text-[#e384c7]'"></i>
                  {{ doc.name }}
                </div>
                <div class="text-xs opacity-75 mt-1 ml-6">
                  <i class="far fa-clock mr-1"></i>{{ formatDate(doc.updated_at) }}
                </div>
              </div>
              
              <!-- Delete button -->
              <button
                @click.stop="confirmDeleteDocument(doc.id)"
                class="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded hover:bg-red-500 hover:text-white"
                :class="selectedDocId === doc.id ? 'text-white' : 'text-red-500'"
                title="Delete document"
              >
                <i class="fas fa-trash text-sm"></i>
              </button>
            </div>
          </div>

          <div v-if="documents.length === 0" class="text-center text-gray-500 dark:text-gray-400 mt-8">
            <i class="fas fa-inbox text-4xl mb-2 opacity-50"></i>
            <p>No documents yet. Create one!</p>
          </div>
        </div>

        <!-- Middle - Markdown Editor -->
        <div 
          :class="[
            'col-span-12 bg-white dark:bg-gray-800 rounded-lg shadow-lg flex flex-col relative z-10 backdrop-blur-sm bg-opacity-90 dark:bg-opacity-90 animate-fade-in transition-all duration-300',
            editorMinimized ? 'lg:col-span-1 p-0 items-center justify-center' : 'lg:col-span-5 p-4',
            previewMinimized && !editorMinimized ? 'lg:col-span-8' : ''
          ]"
          style="animation-delay: 0.1s;"
        >
          <!-- Minimized state - thin vertical bar with expand button -->
          <button
            v-if="editorMinimized"
            @click="editorMinimized = false"
            class="hidden lg:flex h-full w-full flex-col items-center justify-center gap-3 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 py-8"
            title="Expand editor"
          >
            <i class="fas fa-chevron-right text-xl text-gray-600 dark:text-gray-300"></i>
            <div class="flex flex-col items-center gap-1">
              <span 
                class="text-xs font-medium text-gray-600 dark:text-gray-300 whitespace-nowrap"
                style="writing-mode: vertical-rl; text-orientation: mixed;"
              >
                Editor
              </span>
            </div>
            <i class="fas fa-edit text-[#e384c7]"></i>
          </button>

          <!-- Full editor state -->
          <template v-if="!editorMinimized">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-100">
                <i class="fas fa-edit mr-2 text-[#e384c7]"></i>Editor
              </h2>
              <div class="flex gap-2">
              <button
                @click="editorMinimized = true; previewMinimized = false"
                class="p-2 text-gray-600 dark:text-gray-300 hover:text-[#e384c7] hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-all hidden lg:block"
                title="Minimize editor"
              >
                <i class="fas fa-compress-alt"></i>
              </button>
              <button
                @click="uploadImage"
                class="px-3 py-1.5 text-sm bg-gradient-to-r from-[#e384c7] to-[#9e6593] text-white rounded-lg hover:from-[#d674b7] hover:to-[#8e5583] transition-all duration-200 transform hover:scale-105 shadow disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="!selectedDocId"
              >
                <i class="fas fa-image mr-1"></i> Upload Image
              </button>
            </div>
          </div>
          
          <!-- Images display -->
          <div v-if="images.size > 0" class="mb-3 flex flex-wrap gap-2">
            <div
              v-for="[imageId, dataUrl] in images"
              :key="imageId"
              class="inline-flex items-center gap-2 px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-lg text-sm"
            >
              <i class="fas fa-image text-[#e384c7]"></i>
              <span class="text-gray-700 dark:text-gray-300 max-w-[150px] truncate">
                {{ imageId.split('_').slice(1).join('_') }}
              </span>
              <button
                @click="removeImage(imageId)"
                class="text-red-500 hover:text-red-700 transition-colors"
                title="Remove image"
              >
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>
          
          <textarea
            ref="textareaRef"
            v-model="markdown"
            @input="debouncedUpdate"
            @keydown="handleKeyDown"
            @click="sendCursorPosition"
            @keyup="sendCursorPosition"
            class="flex-1 w-full p-4 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#e384c7] focus:border-transparent bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white font-mono text-sm resize-none transition-all duration-200 relative"
            placeholder="Write your markdown here..."
            :disabled="!selectedDocId"
          ></textarea>
          
          <!-- Remote cursors indicator -->
          <div v-if="remoteCursors.length > 0" class="mt-2 flex flex-wrap gap-2">
            <div
              v-for="cursor in remoteCursors"
              :key="cursor.username"
              class="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 dark:bg-blue-900 rounded text-xs text-blue-700 dark:text-blue-300"
            >
              <i class="fas fa-edit"></i>
              <span>{{ cursor.username }} @ line {{ cursor.lineNumber }}</span>
            </div>
          </div>

          <input
            type="file"
            ref="fileInput"
            @change="handleImageUpload"
            accept="image/*"
            class="hidden"
          />
          </template>
        </div>

        <!-- Right - Preview -->
        <div 
          :class="[
            'col-span-12 bg-white dark:bg-gray-800 rounded-lg shadow-lg flex flex-col relative z-10 backdrop-blur-sm bg-opacity-90 dark:bg-opacity-90 animate-fade-in transition-all duration-300',
            'hidden lg:flex',
            previewMinimized ? 'lg:col-span-1 p-0 items-center justify-center' : 'lg:col-span-4 p-4',
            editorMinimized && !previewMinimized ? 'lg:col-span-8' : ''
          ]"
          style="animation-delay: 0.2s;"
        >
          <!-- Minimized state - thin vertical bar with expand button -->
          <button
            v-if="previewMinimized"
            @click="previewMinimized = false"
            class="h-full w-full flex-col items-center justify-center gap-3 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 py-8"
            title="Expand preview"
          >
            <i class="fas fa-chevron-left text-xl text-gray-600 dark:text-gray-300"></i>
            <div class="flex flex-col items-center gap-1">
              <span 
                class="text-xs font-medium text-gray-600 dark:text-gray-300 whitespace-nowrap"
                style="writing-mode: vertical-rl; text-orientation: mixed;"
              >
                Preview
              </span>
            </div>
            <i class="fas fa-eye text-[#e384c7]"></i>
          </button>

          <!-- Full preview state -->
          <template v-if="!previewMinimized">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-100">
              <i class="fas fa-eye mr-2 text-[#e384c7]"></i>Preview
            </h2>
            <div class="flex gap-2">
              <button
                @click="previewMinimized = true; editorMinimized = false"
                class="p-2 text-gray-600 dark:text-gray-300 hover:text-[#e384c7] hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-all"
                title="Minimize preview"
              >
                <i class="fas fa-compress-alt"></i>
              </button>
              <button
                @click="downloadMarkdown"
                class="px-3 py-1.5 text-sm bg-gradient-to-r from-[#e384c7] to-[#9e6593] text-white rounded-lg hover:from-[#d674b7] hover:to-[#8e5583] transition-all duration-200 transform hover:scale-105 shadow disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="!selectedDocId"
              >
                <i class="fas fa-download mr-1"></i> Download
              </button>
            </div>
          </div>
          
          <MarkdownRender :content="renderedMarkdown" class="flex-1 overflow-y-auto p-4 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 markdown-preview" />
          </template>
        </div>

        <!-- Minimized Editor Button -->
        <!-- Minimized Preview Button -->
      </div>
    </div>

    <!-- Mobile Floating Menu Button -->
    <button
      @click.stop="mobileMenuOpen = true"
      class="lg:hidden fixed bottom-6 left-6 z-40 w-14 h-14 bg-gradient-to-r from-[#e384c7] to-[#9e6593] text-white rounded-full shadow-lg flex items-center justify-center hover:shadow-xl transition-all duration-200 transform hover:scale-110"
      title="Open documents"
    >
      <i class="fas fa-bars text-xl"></i>
    </button>

    <!-- Mobile Document List Modal -->
    <div
      v-if="mobileMenuOpen"
      class="lg:hidden fixed inset-0 z-50 bg-black bg-opacity-50 backdrop-blur-sm"
      @click.self="mobileMenuOpen = false"
    >
      <div class="h-full w-full bg-white dark:bg-gray-800 p-6 overflow-y-auto animate-fade-in">
        <!-- Close button -->
        <button
          @click="mobileMenuOpen = false"
          class="absolute top-4 right-4 p-3 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 bg-gray-100 dark:bg-gray-700 rounded-full"
        >
          <i class="fas fa-times text-xl"></i>
        </button>

        <div class="flex justify-between items-center mb-6 pr-12">
          <h2 class="text-2xl font-semibold text-gray-800 dark:text-gray-100">
            <i class="fas fa-folder-open mr-2 text-[#e384c7]"></i>Documents
          </h2>
          <button
            @click="showCreateDialog = true"
            class="p-3 text-white bg-gradient-to-r from-[#e384c7] to-[#9e6593] hover:from-[#d674b7] hover:to-[#8e5583] rounded-full transition-all duration-200 transform hover:scale-110 shadow-md"
            title="Create new document"
          >
            <i class="fas fa-plus text-lg"></i>
          </button>
        </div>

        <div class="space-y-3">
          <div
            v-for="doc in documents"
            :key="doc.id"
            class="p-4 rounded-lg transition-all duration-200 transform active:scale-95 relative group"
            :class="selectedDocId === doc.id 
              ? 'bg-gradient-to-r from-[#e384c7] to-[#9e6593] text-white shadow-md' 
              : 'bg-gray-50 dark:bg-gray-700 text-gray-800 dark:text-gray-200 active:bg-gray-100 dark:active:bg-gray-600'"
          >
            <div @click="selectDocument(doc.id)" class="cursor-pointer">
              <div class="font-medium flex items-center text-lg">
                <i class="fas fa-file-alt mr-3" :class="selectedDocId === doc.id ? 'text-white' : 'text-[#e384c7]'"></i>
                {{ doc.name }}
              </div>
              <div class="text-sm opacity-75 mt-2 ml-9">
                <i class="far fa-clock mr-1"></i>{{ formatDate(doc.updated_at) }}
              </div>
            </div>
            
            <!-- Delete button -->
            <button
              @click.stop="confirmDeleteDocument(doc.id)"
              class="absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-full transition-all"
              :class="selectedDocId === doc.id ? 'text-white hover:bg-white/20' : 'text-red-500 hover:bg-red-500 hover:text-white'"
              title="Delete document"
            >
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>

        <div v-if="documents.length === 0" class="text-center text-gray-500 dark:text-gray-400 mt-16">
          <i class="fas fa-inbox text-6xl mb-4 opacity-50"></i>
          <p class="text-lg">No documents yet. Create one!</p>
        </div>
      </div>
    </div>

    <!-- Delete Document Dialog -->
    <div
      v-if="showDeleteDialog"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 backdrop-blur-sm"
      @click.self="showDeleteDialog = false; deleteDocId = null; deleteError = '';"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-2xl p-6 max-w-md w-full mx-4 animate-fade-in">
        <h3 class="text-xl font-bold mb-4 text-gray-900 dark:text-white flex items-center">
          <i class="fas fa-exclamation-triangle text-red-500 mr-2"></i>Delete Document
        </h3>
        
        <p class="text-gray-700 dark:text-gray-300 mb-4">
          Are you sure you want to delete this document? This action cannot be undone.
        </p>

        <div v-if="deleteError" class="text-red-500 text-sm mb-4 bg-red-50 dark:bg-red-900/20 p-3 rounded">
          <i class="fas fa-exclamation-circle mr-1"></i>{{ deleteError }}
        </div>

        <div class="flex justify-end gap-2">
          <button
            @click="showDeleteDialog = false; deleteDocId = null; deleteError = '';"
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all duration-200"
          >
            Cancel
          </button>
          <button
            @click="deleteDocument"
            class="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-red-500 to-red-600 rounded-lg hover:from-red-600 hover:to-red-700 transition-all duration-200 transform hover:scale-105 shadow"
          >
            <i class="fas fa-trash mr-1"></i>Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Create Document Dialog -->
    <div
      v-if="showCreateDialog"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 backdrop-blur-sm"
      @click.self="showCreateDialog = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-2xl p-6 max-w-md w-full mx-4 animate-fade-in">
        <h3 class="text-xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-[#e384c7] to-[#9e6593]">
          <i class="fas fa-plus-circle mr-2"></i>Create New Document
        </h3>
        
        <input
          v-model="newDocName"
          type="text"
          placeholder="Document name"
          class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#e384c7] focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-all duration-200"
          @keyup.enter="createDocument"
        />

        <div v-if="createError" class="text-red-500 text-sm mt-2 bg-red-50 dark:bg-red-900/20 p-2 rounded">
          <i class="fas fa-exclamation-circle mr-1"></i>{{ createError }}
        </div>

        <div class="flex justify-end gap-2 mt-6">
          <button
            @click="showCreateDialog = false"
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all duration-200"
          >
            Cancel
          </button>
          <button
            @click="createDocument"
            class="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-[#e384c7] to-[#9e6593] rounded-lg hover:from-[#d674b7] hover:to-[#8e5583] transition-all duration-200 transform hover:scale-105 shadow"
          >
            <i class="fas fa-check mr-1"></i>Create
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import MarkdownRender from 'markstream-vue';
import 'markstream-vue/index.css';

const router = useRouter();

const username = ref(localStorage.getItem('sm_username') || '');
const token = ref(localStorage.getItem('sm_token') || '');

const documents = ref([]);
const selectedDocId = ref(null);
const markdown = ref('');
const showCreateDialog = ref(false);
const newDocName = ref('');
const createError = ref('');
const fileInput = ref(null);
const showDeleteDialog = ref(false);
const deleteDocId = ref(null);
const deleteError = ref('');
const activeUsers = ref(new Map()); // Map of docId -> Set of usernames
const remoteCursors = ref([]); // Array of {username, position, lineNumber}
const textareaRef = ref(null);

// Store images separately with unique IDs
const images = ref(new Map());
let imageIdCounter = 1;

// Panel minimize state
const editorMinimized = ref(false);
const previewMinimized = ref(false);

// Mobile sidebar state
const mobileMenuOpen = ref(false);

// Undo/redo history
const undoHistory = ref([]);
const redoHistory = ref([]);
const maxHistorySize = 50;
let isUndoRedoAction = false;

let ws = null;
let updateTimeout = null;
let cursorUpdateTimeout = null;
let lastSentContent = '';
let lastServerContent = ''; // Track the last known server state for merge conflict resolution

// Check authentication
if (!token.value) {
  router.push('/login');
}

const API_URL = window.location.origin;
const WS_PROTOCOL = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const WS_HOST = window.location.host;

// Advanced diff-based merge using Longest Common Subsequence (LCS)
const computeLCS = (arr1, arr2) => {
  const m = arr1.length;
  const n = arr2.length;
  const dp = Array(m + 1).fill(null).map(() => Array(n + 1).fill(0));
  
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (arr1[i - 1] === arr2[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1] + 1;
      } else {
        dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
      }
    }
  }
  
  // Backtrack to find LCS
  const lcs = [];
  let i = m, j = n;
  while (i > 0 && j > 0) {
    if (arr1[i - 1] === arr2[j - 1]) {
      lcs.unshift({ line: arr1[i - 1], idx1: i - 1, idx2: j - 1 });
      i--;
      j--;
    } else if (dp[i - 1][j] > dp[i][j - 1]) {
      i--;
    } else {
      j--;
    }
  }
  
  return lcs;
};

// Compute diff operations between two texts
const computeDiff = (base, modified) => {
  const baseLines = base.split('\n');
  const modifiedLines = modified.split('\n');
  const lcs = computeLCS(baseLines, modifiedLines);
  
  const operations = [];
  let baseIdx = 0;
  let modIdx = 0;
  let lcsIdx = 0;
  
  while (baseIdx < baseLines.length || modIdx < modifiedLines.length) {
    const nextLCS = lcs[lcsIdx];
    
    // Check if we've reached a common line
    if (nextLCS && baseIdx === nextLCS.idx1 && modIdx === nextLCS.idx2) {
      // This line is unchanged
      operations.push({
        type: 'keep',
        basePos: baseIdx,
        modPos: modIdx,
        content: baseLines[baseIdx]
      });
      baseIdx++;
      modIdx++;
      lcsIdx++;
    }
    // Check for deletion from base
    else if (nextLCS && baseIdx < nextLCS.idx1) {
      operations.push({
        type: 'delete',
        basePos: baseIdx,
        content: baseLines[baseIdx]
      });
      baseIdx++;
    }
    // Check for insertion in modified
    else if (nextLCS && modIdx < nextLCS.idx2) {
      operations.push({
        type: 'insert',
        basePos: baseIdx,
        modPos: modIdx,
        content: modifiedLines[modIdx]
      });
      modIdx++;
    }
    // No more LCS matches
    else if (!nextLCS) {
      if (baseIdx < baseLines.length && modIdx < modifiedLines.length) {
        // Both have content - this is a modification
        if (baseLines[baseIdx] !== modifiedLines[modIdx]) {
          operations.push({
            type: 'modify',
            basePos: baseIdx,
            modPos: modIdx,
            oldContent: baseLines[baseIdx],
            newContent: modifiedLines[modIdx]
          });
        }
        baseIdx++;
        modIdx++;
      } else if (baseIdx < baseLines.length) {
        // Only base has content - deletion
        operations.push({
          type: 'delete',
          basePos: baseIdx,
          content: baseLines[baseIdx]
        });
        baseIdx++;
      } else if (modIdx < modifiedLines.length) {
        // Only modified has content - insertion
        operations.push({
          type: 'insert',
          basePos: baseIdx,
          modPos: modIdx,
          content: modifiedLines[modIdx]
        });
        modIdx++;
      }
    }
  }
  
  return operations;
};

// Apply operations with position transformation
const applyOperations = (base, operations) => {
  const lines = base.split('\n');
  const result = [];
  let positionMap = new Map(); // Track how positions have shifted
  
  // Build position map from operations
  let offset = 0;
  operations.forEach((op, idx) => {
    if (op.type === 'insert') {
      offset++;
    } else if (op.type === 'delete') {
      offset--;
    }
    positionMap.set(op.basePos, offset);
  });
  
  // Apply operations
  let currentPos = 0;
  operations.forEach(op => {
    if (op.type === 'keep') {
      result.push(op.content);
      currentPos++;
    } else if (op.type === 'insert') {
      result.push(op.content);
    } else if (op.type === 'modify') {
      result.push(op.newContent);
      currentPos++;
    }
    // delete: don't add anything, skip the line
    else if (op.type === 'delete') {
      currentPos++;
    }
  });
  
  return result.join('\n');
};

// Three-way merge with operational transformation
const mergeChanges = (base, local, remote) => {
  // Quick checks for simple cases
  if (local === remote) return local;
  if (local === base) return remote;
  if (remote === base) return local;
  
  // Compute operations from base to local and base to remote
  const localOps = computeDiff(base, local);
  const remoteOps = computeDiff(base, remote);
  
  // Merge operations by transforming them relative to each other
  const mergedOps = [];
  let localIdx = 0;
  let remoteIdx = 0;
  let positionOffset = 0; // Track cumulative position shifts
  
  // Map to track which base positions have been handled
  const handledPositions = new Set();
  
  // Process operations in position order
  while (localIdx < localOps.length || remoteIdx < remoteOps.length) {
    const localOp = localOps[localIdx];
    const remoteOp = remoteOps[remoteIdx];
    
    // Both operations exhausted
    if (!localOp && !remoteOp) break;
    
    // Only local operations left
    if (!remoteOp) {
      mergedOps.push({ ...localOp, transformedPos: localOp.basePos + positionOffset });
      localIdx++;
      if (localOp.type === 'insert') positionOffset++;
      else if (localOp.type === 'delete') positionOffset--;
      continue;
    }
    
    // Only remote operations left
    if (!localOp) {
      mergedOps.push({ ...remoteOp, transformedPos: remoteOp.basePos + positionOffset });
      remoteIdx++;
      if (remoteOp.type === 'insert') positionOffset++;
      else if (remoteOp.type === 'delete') positionOffset--;
      continue;
    }
    
    // Both operations at same position - need to merge carefully
    if (localOp.basePos === remoteOp.basePos) {
      handledPositions.add(localOp.basePos);
      
      // Both keeping the line - check if it's actually the same
      if (localOp.type === 'keep' && remoteOp.type === 'keep') {
        mergedOps.push({ ...localOp, transformedPos: localOp.basePos + positionOffset });
        localIdx++;
        remoteIdx++;
        continue;
      }
      
      // Both deleting - only delete once
      if (localOp.type === 'delete' && remoteOp.type === 'delete') {
        mergedOps.push({ ...localOp, transformedPos: localOp.basePos + positionOffset });
        positionOffset--;
        localIdx++;
        remoteIdx++;
        continue;
      }
      
      // Both inserting at same position - keep both insertions
      if (localOp.type === 'insert' && remoteOp.type === 'insert') {
        mergedOps.push({ ...localOp, transformedPos: localOp.basePos + positionOffset });
        positionOffset++;
        mergedOps.push({ ...remoteOp, transformedPos: remoteOp.basePos + positionOffset });
        positionOffset++;
        localIdx++;
        remoteIdx++;
        continue;
      }
      
      // Both modifying same line - keep both versions
      if (localOp.type === 'modify' && remoteOp.type === 'modify') {
        if (localOp.newContent === remoteOp.newContent) {
          // Same modification
          mergedOps.push({ ...localOp, transformedPos: localOp.basePos + positionOffset });
        } else {
          // Different modifications - keep both
          mergedOps.push({ ...localOp, transformedPos: localOp.basePos + positionOffset });
          positionOffset++;
          mergedOps.push({ 
            type: 'insert',
            basePos: remoteOp.basePos,
            content: remoteOp.newContent,
            transformedPos: remoteOp.basePos + positionOffset
          });
          positionOffset++;
        }
        localIdx++;
        remoteIdx++;
        continue;
      }
      
      // One deletes, one modifies - prefer the modification
      if ((localOp.type === 'delete' && remoteOp.type === 'modify') ||
          (localOp.type === 'modify' && remoteOp.type === 'delete')) {
        const modOp = localOp.type === 'modify' ? localOp : remoteOp;
        mergedOps.push({ ...modOp, transformedPos: modOp.basePos + positionOffset });
        localIdx++;
        remoteIdx++;
        continue;
      }
      
      // One keeps, one modifies - take the modification
      if ((localOp.type === 'keep' && remoteOp.type === 'modify') ||
          (localOp.type === 'modify' && remoteOp.type === 'keep')) {
        const modOp = localOp.type === 'modify' ? localOp : { type: 'keep', ...remoteOp };
        mergedOps.push({ ...modOp, transformedPos: modOp.basePos + positionOffset });
        localIdx++;
        remoteIdx++;
        continue;
      }
      
      // Mixed operations - apply both with position adjustment
      mergedOps.push({ ...localOp, transformedPos: localOp.basePos + positionOffset });
      if (localOp.type === 'insert') positionOffset++;
      else if (localOp.type === 'delete') positionOffset--;
      
      mergedOps.push({ ...remoteOp, transformedPos: remoteOp.basePos + positionOffset });
      if (remoteOp.type === 'insert') positionOffset++;
      else if (remoteOp.type === 'delete') positionOffset--;
      
      localIdx++;
      remoteIdx++;
      continue;
    }
    
    // Operations at different positions - apply in order
    if (localOp.basePos < remoteOp.basePos) {
      mergedOps.push({ ...localOp, transformedPos: localOp.basePos + positionOffset });
      if (localOp.type === 'insert') positionOffset++;
      else if (localOp.type === 'delete') positionOffset--;
      localIdx++;
    } else {
      mergedOps.push({ ...remoteOp, transformedPos: remoteOp.basePos + positionOffset });
      if (remoteOp.type === 'insert') positionOffset++;
      else if (remoteOp.type === 'delete') positionOffset--;
      remoteIdx++;
    }
  }
  
  // Apply merged operations to base
  const baseLines = base.split('\n');
  const result = [];
  
  // Sort operations by transformed position
  mergedOps.sort((a, b) => {
    const posA = a.transformedPos !== undefined ? a.transformedPos : a.basePos;
    const posB = b.transformedPos !== undefined ? b.transformedPos : b.basePos;
    return posA - posB;
  });
  
  // Apply operations
  mergedOps.forEach(op => {
    if (op.type === 'keep') {
      result.push(op.content);
    } else if (op.type === 'insert') {
      result.push(op.content);
    } else if (op.type === 'modify') {
      result.push(op.newContent);
    }
    // delete operations are handled by not adding the line
  });
  
  return result.join('\n');
};

// Computed
const renderedMarkdown = computed(() => {
  if (!markdown.value) return '';
  
  // Replace image placeholders with actual base64 data for preview
  let processedMarkdown = markdown.value;
  images.value.forEach((dataUrl, id) => {
    const placeholder = `![Image: ${id}](image:${id})`;
    processedMarkdown = processedMarkdown.replace(placeholder, `![Image](${dataUrl})`);
  });
  
  return processedMarkdown;
});

// Display markdown with clean image indicators
const displayMarkdown = computed(() => {
  if (!markdown.value) return '';
  
  let display = markdown.value;
  images.value.forEach((dataUrl, id) => {
    const placeholder = `![Image: ${id}](image:${id})`;
    // Get filename from id (stored in format: filename.ext)
    const filename = id.split('_').slice(1).join('_');
    display = display.replace(placeholder, `[📷 ${filename}] `);
  });
  
  return display;
});

// Methods
const fetchDocuments = async () => {
  try {
    const response = await fetch(`${API_URL}/sm-api/documents`, {
      headers: {
        'Authorization': `Bearer ${token.value}`,
      },
    });
    
    if (response.ok) {
      documents.value = await response.json();
    }
  } catch (err) {
    console.error('Failed to fetch documents:', err);
  }
};

const selectDocument = async (docId) => {
  selectedDocId.value = docId;
  
  // Close mobile menu after selection
  mobileMenuOpen.value = false;
  
  // Clear undo/redo history for new document
  undoHistory.value = [];
  redoHistory.value = [];
  
  // Save last edited document to localStorage
  localStorage.setItem('sm_last_document', docId.toString());
  
  try {
    const response = await fetch(`${API_URL}/sm-api/documents/${docId}`, {
      headers: {
        'Authorization': `Bearer ${token.value}`,
      },
    });
    
    if (response.ok) {
      const doc = await response.json();
      const fullMarkdown = doc.content || '';
      
      // Clear images map
      images.value.clear();
      imageIdCounter = 1;
      
      // Extract base64 images from markdown and replace with placeholders
      // Pattern: ![alt](data:image/...)
      const imageRegex = /!\[([^\]]*)\]\((data:image\/[^;]+;base64,[^)]+)\)/g;
      let match;
      let displayMarkdown = fullMarkdown;
      
      while ((match = imageRegex.exec(fullMarkdown)) !== null) {
        const altText = match[1];
        const dataUrl = match[2];
        const imageId = `${imageIdCounter++}_${altText || 'image'}`;
        
        // Store the base64 data
        images.value.set(imageId, dataUrl);
        
        // Replace with placeholder in display markdown
        const placeholder = `![Image: ${imageId}](image:${imageId})`;
        displayMarkdown = displayMarkdown.replace(match[0], placeholder);
      }
      
      markdown.value = displayMarkdown;
      lastServerContent = displayMarkdown; // Track server state
      
      // Connect to WebSocket for real-time updates
      connectWebSocket(docId);
    }
  } catch (err) {
    console.error('Failed to fetch document:', err);
  }
};

const createDocument = async () => {
  createError.value = '';
  
  if (!newDocName.value.trim()) {
    createError.value = 'Document name is required';
    return;
  }
  
  try {
    const response = await fetch(`${API_URL}/sm-api/documents`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token.value}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name: newDocName.value }),
    });
    
    if (response.ok) {
      const doc = await response.json();
      await fetchDocuments();
      showCreateDialog.value = false;
      newDocName.value = '';
      selectDocument(doc.id);
    } else {
      const data = await response.json();
      createError.value = data.detail || 'Failed to create document';
    }
  } catch (err) {
    createError.value = 'Failed to create document';
  }
};

const updateDocument = async () => {
  if (!selectedDocId.value) return;
  
  try {
    // Convert placeholders back to full base64 images for storage
    let fullMarkdown = markdown.value;
    images.value.forEach((dataUrl, imageId) => {
      const placeholder = `![Image: ${imageId}](image:${imageId})`;
      // Get filename from imageId (format: id_filename)
      const filename = imageId.split('_').slice(1).join('_') || 'image';
      const fullImageMarkdown = `![${filename}](${dataUrl})`;
      fullMarkdown = fullMarkdown.replace(placeholder, fullImageMarkdown);
    });
    
    await fetch(`${API_URL}/sm-api/documents/${selectedDocId.value}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token.value}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content: fullMarkdown }),
    });
  } catch (err) {
    console.error('Failed to update document:', err);
  }
};

const saveToHistory = (content) => {
  if (isUndoRedoAction) return;
  
  // Don't save if it's the same as the last entry
  if (undoHistory.value.length > 0 && undoHistory.value[undoHistory.value.length - 1] === content) {
    return;
  }
  
  undoHistory.value.push(content);
  
  // Limit history size
  if (undoHistory.value.length > maxHistorySize) {
    undoHistory.value.shift();
  }
  
  // Clear redo history when new changes are made
  redoHistory.value = [];
};

const debouncedUpdate = () => {
  if (updateTimeout) {
    clearTimeout(updateTimeout);
  }
  
  // Send cursor position immediately
  sendCursorPosition();
  
  updateTimeout = setTimeout(() => {
    // Only send if content actually changed
    if (markdown.value !== lastSentContent) {
      // Save to history before updating
      saveToHistory(lastSentContent);
      
      updateDocument();
      lastSentContent = markdown.value;
      lastServerContent = markdown.value; // Update our known server state
      
      // Send update via WebSocket - convert to full markdown with base64 images
      if (ws && ws.readyState === WebSocket.OPEN) {
        let fullMarkdown = markdown.value;
        images.value.forEach((dataUrl, imageId) => {
          const placeholder = `![Image: ${imageId}](image:${imageId})`;
          const filename = imageId.split('_').slice(1).join('_') || 'image';
          const fullImageMarkdown = `![${filename}](${dataUrl})`;
          fullMarkdown = fullMarkdown.replace(placeholder, fullImageMarkdown);
        });
        
        ws.send(JSON.stringify({ 
          type: 'content_update',
          content: fullMarkdown
        }));
      }
    }
  }, 1000);
};

const undo = () => {
  if (undoHistory.value.length === 0) return;
  
  isUndoRedoAction = true;
  
  // Save current state to redo history
  redoHistory.value.push(markdown.value);
  
  // Pop from undo history
  const previousState = undoHistory.value.pop();
  markdown.value = previousState;
  lastSentContent = previousState;
  
  // Update document and send via WebSocket
  updateDocument();
  if (ws && ws.readyState === WebSocket.OPEN) {
    let fullMarkdown = markdown.value;
    images.value.forEach((dataUrl, imageId) => {
      const placeholder = `![Image: ${imageId}](image:${imageId})`;
      const filename = imageId.split('_').slice(1).join('_') || 'image';
      const fullImageMarkdown = `![${filename}](${dataUrl})`;
      fullMarkdown = fullMarkdown.replace(placeholder, fullImageMarkdown);
    });
    
    ws.send(JSON.stringify({ 
      type: 'content_update',
      content: fullMarkdown
    }));
  }
  
  setTimeout(() => {
    isUndoRedoAction = false;
  }, 100);
};

const redo = () => {
  if (redoHistory.value.length === 0) return;
  
  isUndoRedoAction = true;
  
  // Save current state to undo history
  undoHistory.value.push(markdown.value);
  
  // Pop from redo history
  const nextState = redoHistory.value.pop();
  markdown.value = nextState;
  lastSentContent = nextState;
  
  // Update document and send via WebSocket
  updateDocument();
  if (ws && ws.readyState === WebSocket.OPEN) {
    let fullMarkdown = markdown.value;
    images.value.forEach((dataUrl, imageId) => {
      const placeholder = `![Image: ${imageId}](image:${imageId})`;
      const filename = imageId.split('_').slice(1).join('_') || 'image';
      const fullImageMarkdown = `![${filename}](${dataUrl})`;
      fullMarkdown = fullMarkdown.replace(placeholder, fullImageMarkdown);
    });
    
    ws.send(JSON.stringify({ 
      type: 'content_update',
      content: fullMarkdown
    }));
  }
  
  setTimeout(() => {
    isUndoRedoAction = false;
  }, 100);
};

const handleKeyDown = (event) => {
  // Ctrl+Z or Cmd+Z for undo
  if ((event.ctrlKey || event.metaKey) && event.key === 'z' && !event.shiftKey) {
    event.preventDefault();
    undo();
  }
  // Ctrl+Y or Cmd+Shift+Z for redo
  else if ((event.ctrlKey || event.metaKey) && (event.key === 'y' || (event.shiftKey && event.key === 'z'))) {
    event.preventDefault();
    redo();
  }
};

const sendCursorPosition = () => {
  if (!textareaRef.value || !ws || ws.readyState !== WebSocket.OPEN) return;
  
  if (cursorUpdateTimeout) {
    clearTimeout(cursorUpdateTimeout);
  }
  
  cursorUpdateTimeout = setTimeout(() => {
    const textarea = textareaRef.value;
    const position = textarea.selectionStart;
    
    // Calculate line number
    const textBeforeCursor = markdown.value.substring(0, position);
    const lineNumber = (textBeforeCursor.match(/\n/g) || []).length + 1;
    
    // Get context around cursor (10 chars before and after)
    const contextStart = Math.max(0, position - 10);
    const contextEnd = Math.min(markdown.value.length, position + 10);
    const context = markdown.value.substring(contextStart, contextEnd);
    
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'cursor_position',
        position: position,
        lineNumber: lineNumber,
        context: context
      }));
    }
  }, 200);
};

const connectWebSocket = (docId) => {
  // Close existing connection
  if (ws) {
    ws.close();
  }
  
  remoteCursors.value = [];
  lastSentContent = markdown.value;
  
  ws = new WebSocket(`${WS_PROTOCOL}//${WS_HOST}/sm-ws/${docId}?token=${token.value}`);
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'content_update' && data.username !== username.value) {
      // Extract images from incoming content and replace with placeholders
      let fullMarkdown = data.content;
      const imageRegex = /!\[([^\]]*)\]\((data:image\/[^;]+;base64,[^)]+)\)/g;
      let match;
      let remoteMarkdown = fullMarkdown;
      
      while ((match = imageRegex.exec(fullMarkdown)) !== null) {
        const altText = match[1];
        const dataUrl = match[2];
        
        // Check if we already have this image
        let existingImageId = null;
        for (const [id, url] of images.value) {
          if (url === dataUrl) {
            existingImageId = id;
            break;
          }
        }
        
        if (!existingImageId) {
          // New image from another user
          existingImageId = `${imageIdCounter++}_${altText || 'image'}`;
          images.value.set(existingImageId, dataUrl);
        }
        
        // Replace with placeholder
        const placeholder = `![Image: ${existingImageId}](image:${existingImageId})`;
        remoteMarkdown = remoteMarkdown.replace(match[0], placeholder);
      }
      
      // Perform three-way merge: base (lastServerContent), local (current markdown), remote (incoming)
      const mergedContent = mergeChanges(lastServerContent, markdown.value, remoteMarkdown);
      
      // Update server state to the remote version
      lastServerContent = remoteMarkdown;
      
      // Only update if there's a difference
      if (mergedContent !== markdown.value) {
        // Save cursor position
        const cursorPos = textareaRef.value?.selectionStart || 0;
        
        // Update content
        markdown.value = mergedContent;
        lastSentContent = mergedContent;
        
        // Restore cursor position (approximately)
        nextTick(() => {
          if (textareaRef.value) {
            const newPos = Math.min(cursorPos, markdown.value.length);
            textareaRef.value.selectionStart = newPos;
            textareaRef.value.selectionEnd = newPos;
          }
        });
      }
    } else if (data.type === 'cursor_position' && data.username !== username.value) {
      // Update remote cursor position
      const existingCursor = remoteCursors.value.find(c => c.username === data.username);
      if (existingCursor) {
        existingCursor.position = data.position;
        existingCursor.lineNumber = data.lineNumber;
      } else {
        remoteCursors.value.push({
          username: data.username,
          position: data.position,
          lineNumber: data.lineNumber
        });
      }
    } else if (data.type === 'user_joined') {
      // Track active users
      if (!activeUsers.value.has(docId)) {
        activeUsers.value.set(docId, new Set());
      }
      activeUsers.value.get(docId).add(data.username);
    } else if (data.type === 'user_left') {
      // Remove user from active list and cursors
      if (activeUsers.value.has(docId)) {
        activeUsers.value.get(docId).delete(data.username);
      }
      remoteCursors.value = remoteCursors.value.filter(c => c.username !== data.username);
    } else if (data.type === 'active_users') {
      // Initial list of active users
      activeUsers.value.set(docId, new Set(data.users));
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
};

const uploadImage = () => {
  fileInput.value?.click();
};

const handleImageUpload = async (event) => {
  const file = event.target.files?.[0];
  if (!file || !selectedDocId.value) return;
  
  const reader = new FileReader();
  reader.onload = async (e) => {
    try {
      const response = await fetch(`${API_URL}/sm-api/documents/${selectedDocId.value}/images`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token.value}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: file.name,
          data: e.target.result,
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Generate unique ID for this image using counter and filename
        const imageId = `${imageIdCounter++}_${file.name}`;
        
        // Store the base64 data in our map
        images.value.set(imageId, data.dataUrl);
        
        // Insert a placeholder in markdown
        const imageMarkdown = `![Image: ${imageId}](image:${imageId})`;
        markdown.value += `\n${imageMarkdown}\n`;
        updateDocument();
      }
    } catch (err) {
      console.error('Failed to upload image:', err);
    }
  };
  
  reader.readAsDataURL(file);
  event.target.value = '';
};

const removeImage = (imageId) => {
  // Remove from images map
  images.value.delete(imageId);
  
  // Remove from markdown
  const placeholder = `![Image: ${imageId}](image:${imageId})`;
  markdown.value = markdown.value.replace(new RegExp(`\\n?${placeholder.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\n?`, 'g'), '');
  
  updateDocument();
};

const confirmDeleteDocument = (docId) => {
  deleteDocId.value = docId;
  deleteError.value = '';
  showDeleteDialog.value = true;
};

const deleteDocument = async () => {
  if (!deleteDocId.value) return;
  
  deleteError.value = '';
  
  // Check if other users are editing this document
  const users = activeUsers.value.get(deleteDocId.value);
  if (users && users.size > 0) {
    const otherUsers = Array.from(users).filter(u => u !== username.value);
    if (otherUsers.length > 0) {
      deleteError.value = `Cannot delete: ${otherUsers.join(', ')} ${otherUsers.length === 1 ? 'is' : 'are'} currently editing this document`;
      return;
    }
  }
  
  try {
    const response = await fetch(`${API_URL}/sm-api/documents/${deleteDocId.value}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token.value}`,
      },
    });
    
    if (response.ok) {
      // If we're deleting the currently selected document, clear selection
      if (selectedDocId.value === deleteDocId.value) {
        selectedDocId.value = null;
        markdown.value = '';
        images.value.clear();
        if (ws) {
          ws.close();
          ws = null;
        }
      }
      
      // Refresh document list
      await fetchDocuments();
      showDeleteDialog.value = false;
      deleteDocId.value = null;
    } else {
      const data = await response.json();
      deleteError.value = data.detail || 'Failed to delete document';
    }
  } catch (err) {
    deleteError.value = 'Failed to delete document';
  }
};

const downloadMarkdown = () => {
  if (!selectedDocId.value) return;
  
  const doc = documents.value.find(d => d.id === selectedDocId.value);
  const blob = new Blob([markdown.value], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${doc?.name || 'document'}.md`;
  a.click();
  URL.revokeObjectURL(url);
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now - date;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString();
};

const logout = async () => {
  try {
    await fetch(`${API_URL}/sm-api/logout`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token.value}`,
      },
    });
  } catch (err) {
    console.error('Logout error:', err);
  }
  
  localStorage.removeItem('sm_token');
  localStorage.removeItem('sm_username');
  
  if (ws) {
    ws.close();
  }
  
  router.push('/login');
};

// Lifecycle
onMounted(async () => {
  await fetchDocuments();
  
  // Try to restore last edited document
  const lastDocId = localStorage.getItem('sm_last_document');
  if (lastDocId) {
    const docExists = documents.value.find(d => d.id === parseInt(lastDocId));
    if (docExists) {
      selectDocument(parseInt(lastDocId));
    }
  }
});

onUnmounted(() => {
  if (ws) {
    ws.close();
  }
  if (updateTimeout) {
    clearTimeout(updateTimeout);
  }
  if (cursorUpdateTimeout) {
    clearTimeout(cursorUpdateTimeout);
  }
});

// Watch for cursor position changes
watch(() => textareaRef.value, (newVal) => {
  if (newVal) {
    newVal.addEventListener('selectionchange', sendCursorPosition);
  }
});
</script>

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

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(158, 101, 147, 0.3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(158, 101, 147, 0.5);
}

.dark ::-webkit-scrollbar-thumb {
  background: rgba(227, 132, 199, 0.3);
}

.dark ::-webkit-scrollbar-thumb:hover {
  background: rgba(227, 132, 199, 0.5);
}

/* Basic markdown-preview styling for elements not handled by markstream-vue */
.markdown-preview {
  line-height: 1.6;
}

/* Code block styling */
.markdown-preview pre {
  background-color: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  padding: 16px;
  overflow: auto;
  font-size: 14px;
  line-height: 1.45;
  margin: 16px 0;
}

.dark .markdown-preview pre {
  background-color: #0d1117;
  border-color: #30363d;
}

.markdown-preview code {
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace;
  font-size: 0.875em;
}

.markdown-preview pre code {
  background: none;
  padding: 0;
  border: none;
  color: inherit;
}

.markdown-preview :not(pre) > code {
  background-color: rgba(175, 184, 193, 0.2);
  padding: 0.2em 0.4em;
  border-radius: 6px;
  font-size: 85%;
}

.dark .markdown-preview :not(pre) > code {
  background-color: rgba(110, 118, 129, 0.4);
}

/* Dark mode CSS variables for markstream-vue code blocks */
.markdown-preview {
  --markstream-code-fallback-fg: #24292e;
  --markstream-code-fallback-bg: #f6f8fa;
  --vscode-editor-foreground: #24292e;
  --vscode-editor-background: #f6f8fa;
  --vscode-editor-selectionBackground: rgba(0, 0, 0, 0.1);
}

.dark .markdown-preview {
  --markstream-code-fallback-fg: #e6edf3;
  --markstream-code-fallback-bg: #0d1117;
  --vscode-editor-foreground: #e6edf3;
  --vscode-editor-background: #0d1117;
  --vscode-editor-selectionBackground: rgba(255, 255, 255, 0.1);
}
</style>
