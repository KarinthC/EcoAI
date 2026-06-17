// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  }
  // Tu ajouteras plus tard :
  // { path: '/editor', name: 'editor', component: () => import('../views/EditorView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router