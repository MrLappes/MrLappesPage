import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../components/HomePage.vue';

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
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue') // Lazy-loaded
  },
  {
    path: '/linktree',
    name: 'LinkTree',
    component: () => import('../views/LinkTree.vue') // Lazy-loaded
  },
  {
    path: '/sm',
    name: 'SharedMarkdown',
    component: () => import('../views/SharedMarkdown.vue'), // Lazy-loaded
    beforeEnter: async (to, from, next) => {
      const token = localStorage.getItem('sm_token');
      if (!token) {
        next('/login');
      } else {
        // Verify token is still valid
        try {
          const response = await fetch('/sm-api/documents', {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });
          if (response.ok) {
            next();
          } else {
            // Token expired or invalid
            localStorage.removeItem('sm_token');
            localStorage.removeItem('sm_username');
            next('/login');
          }
        } catch (err) {
          next('/login');
        }
      }
    }
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

export default router;
