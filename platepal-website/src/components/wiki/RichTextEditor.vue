<script setup>
import { watch, onBeforeUnmount } from 'vue';
import { useEditor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import Link from '@tiptap/extension-link';
import { useI18n } from 'vue-i18n';

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '' },
});
const emit = defineEmits(['update:modelValue']);
const { t } = useI18n();

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit.configure({ heading: { levels: [1, 2, 3, 4] } }),
    Link.configure({ openOnClick: false, autolink: true, HTMLAttributes: { rel: 'noopener noreferrer nofollow' } }),
  ],
  editorProps: {
    attributes: { class: 'wiki-prose focus:outline-none px-4 py-3' },
  },
  onUpdate: ({ editor }) => {
    const html = editor.getHTML();
    emit('update:modelValue', html === '<p></p>' ? '' : html);
  },
});

watch(
  () => props.modelValue,
  (value) => {
    if (editor.value && value !== editor.value.getHTML()) {
      editor.value.commands.setContent(value || '', false);
    }
  }
);

onBeforeUnmount(() => editor.value?.destroy());

function toggle(cmd) {
  const chain = editor.value.chain().focus();
  cmd(chain).run();
}

function setLink() {
  const previous = editor.value.getAttributes('link').href;
  const url = window.prompt(t('wiki.editor.linkPrompt'), previous || 'https://');
  if (url === null) return;
  if (url === '') {
    editor.value.chain().focus().extendMarkRange('link').unsetLink().run();
    return;
  }
  editor.value.chain().focus().extendMarkRange('link').setLink({ href: url }).run();
}

function isActive(name, attrs) {
  return editor.value?.isActive(name, attrs);
}
</script>

<template>
  <div class="tiptap-editor border border-gray-200 dark:border-dark-elevated rounded-xl overflow-hidden bg-white dark:bg-dark-surface">
    <div
      v-if="editor"
      class="flex flex-wrap gap-1 px-2 py-2 border-b border-gray-100 dark:border-dark-elevated bg-gray-50 dark:bg-dark-bg"
    >
      <button type="button" class="ttbtn" :class="{ ttactive: isActive('bold') }"
        @click="toggle((c) => c.toggleBold())" title="Bold"><i class="fas fa-bold"></i></button>
      <button type="button" class="ttbtn" :class="{ ttactive: isActive('italic') }"
        @click="toggle((c) => c.toggleItalic())" title="Italic"><i class="fas fa-italic"></i></button>
      <button type="button" class="ttbtn" :class="{ ttactive: isActive('strike') }"
        @click="toggle((c) => c.toggleStrike())" title="Strikethrough"><i class="fas fa-strikethrough"></i></button>
      <span class="w-px bg-gray-200 dark:bg-dark-elevated mx-1"></span>
      <button type="button" class="ttbtn" :class="{ ttactive: isActive('heading', { level: 2 }) }"
        @click="toggle((c) => c.toggleHeading({ level: 2 }))" title="Heading">H2</button>
      <button type="button" class="ttbtn" :class="{ ttactive: isActive('heading', { level: 3 }) }"
        @click="toggle((c) => c.toggleHeading({ level: 3 }))" title="Subheading">H3</button>
      <span class="w-px bg-gray-200 dark:bg-dark-elevated mx-1"></span>
      <button type="button" class="ttbtn" :class="{ ttactive: isActive('bulletList') }"
        @click="toggle((c) => c.toggleBulletList())" title="Bullet list"><i class="fas fa-list-ul"></i></button>
      <button type="button" class="ttbtn" :class="{ ttactive: isActive('orderedList') }"
        @click="toggle((c) => c.toggleOrderedList())" title="Numbered list"><i class="fas fa-list-ol"></i></button>
      <button type="button" class="ttbtn" :class="{ ttactive: isActive('blockquote') }"
        @click="toggle((c) => c.toggleBlockquote())" title="Quote"><i class="fas fa-quote-right"></i></button>
      <span class="w-px bg-gray-200 dark:bg-dark-elevated mx-1"></span>
      <button type="button" class="ttbtn" :class="{ ttactive: isActive('link') }" @click="setLink" title="Link">
        <i class="fas fa-link"></i>
      </button>
      <button type="button" class="ttbtn" @click="toggle((c) => c.unsetAllMarks().clearNodes())" title="Clear formatting">
        <i class="fas fa-eraser"></i>
      </button>
    </div>
    <EditorContent :editor="editor" :data-placeholder="placeholder" />
  </div>
</template>

<style scoped>
.ttbtn {
  min-width: 2rem;
  height: 2rem;
  padding: 0 0.5rem;
  border-radius: var(--radius-md, 0.375rem);
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-gray-600, #4b5563);
  transition: background-color 0.15s, color 0.15s;
}
.ttbtn:hover {
  background-color: rgba(227, 132, 199, 0.15);
  color: var(--color-secondary, #9e6593);
}
.ttactive {
  background-color: var(--color-secondary, #9e6593);
  color: #fff;
}
:global(.dark) .ttbtn {
  color: var(--color-gray-300, #d1d5db);
}
</style>
