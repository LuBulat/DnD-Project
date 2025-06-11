import { createRouter, createWebHistory } from 'vue-router'
import api from '../axios';

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/races',
    name: 'Races',
    component: () => import('../views/Race.vue'),
  },
  {
    path: '/classes',
    name: 'Classes',
    component: () => import('../views/Class.vue'),
  },
  {
    path: '/spells',
    name: 'Spells',
    component: () => import('../views/Spells.vue'),
  },
  {
    path: '/backgrounds',
    name: 'Backgrounds',
    component: () => import('../views/Background.vue'),
  },
  {
    path: '/characterSheet',
    name: 'NewCharacterSheet',
    component: () => import('../views/CharacterSheet.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/character/:id',
    name: 'EditCharacterSheet',
    component: () => import('../views/CharacterSheet.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

// Navigation Guard
router.beforeEach(async (to, from, next) => {
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';

  // Ako ruta zahteva autentifikaciju
  if (to.matched.some(record => record.meta.requiresAuth)) {
    const token = localStorage.getItem('token');
    
    if (!token) {
      return next('/login');
    }

    try {
      const response = await api.get('http://localhost:5000/api/check_session', {  // Koristi api umesto axios
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.status === 200) {
        return next();
      } else {
        localStorage.removeItem("token");
        localStorage.setItem("isLoggedIn", "false");
        return next('/login');
      }
    } catch (error) {
      localStorage.removeItem("token");
      localStorage.setItem("isLoggedIn", "false");
      return next('/login');
    }
  }

  // Ako ne traži login
  next();
});

export default router;