import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../components/HomePage.vue';
import { auth, initAuth } from '../wiki/auth.js';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/privacy',
    name: 'Privacy',
    component: () => import('../views/PrivacyPolicy.vue') // Lazy-loaded
  },
  {
    path: '/convert-to-mp3',
    name: 'ConvertToMP3',
    component: () => import('../views/ConvertToMP3.vue') // Lazy-loaded
  },
  {
    path: '/linktree',
    name: 'LinkTree',
    component: () => import('../views/LinkTree.vue') // Lazy-loaded
  },
  // --- Recipe wiki (public) ---
  {
    path: '/wiki',
    redirect: { name: 'WikiRecipes' }
  },
  {
    path: '/wiki/recipes',
    name: 'WikiRecipes',
    component: () => import('../views/wiki/RecipesList.vue')
  },
  {
    path: '/wiki/recipes/:slug',
    name: 'WikiRecipe',
    component: () => import('../views/wiki/RecipeDetail.vue'),
    props: true
  },
  {
    path: '/wiki/ingredients',
    name: 'WikiIngredients',
    component: () => import('../views/wiki/IngredientsList.vue')
  },
  {
    path: '/wiki/ingredients/:slug',
    name: 'WikiIngredient',
    component: () => import('../views/wiki/IngredientDetail.vue'),
    props: true
  },
  // --- Recipe wiki (admin) ---
  {
    path: '/wiki/admin/login',
    name: 'WikiAdminLogin',
    component: () => import('../views/wiki/AdminLogin.vue')
  },
  {
    path: '/wiki/admin',
    name: 'WikiAdminDashboard',
    component: () => import('../views/wiki/AdminDashboard.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/wiki/admin/recipes/new',
    name: 'WikiAdminRecipeNew',
    component: () => import('../views/wiki/RecipeEditor.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/wiki/admin/recipes/:id',
    name: 'WikiAdminRecipeEdit',
    component: () => import('../views/wiki/RecipeEditor.vue'),
    props: true,
    meta: { requiresAdmin: true }
  },
  {
    path: '/wiki/admin/ingredients/new',
    name: 'WikiAdminIngredientNew',
    component: () => import('../views/wiki/IngredientEditor.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/wiki/admin/ingredients/:id',
    name: 'WikiAdminIngredientEdit',
    component: () => import('../views/wiki/IngredientEditor.vue'),
    props: true,
    meta: { requiresAdmin: true }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  }
});

// Guard admin routes: wait for the initial silent refresh, then require auth.
router.beforeEach(async (to) => {
  if (!to.meta.requiresAdmin) return true;
  if (!auth.ready) await initAuth();
  if (!auth.isAuthenticated) {
    return { name: 'WikiAdminLogin' };
  }
  return true;
});

export default router;
