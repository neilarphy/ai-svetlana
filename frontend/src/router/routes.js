const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'create', component: () => import('pages/CreateDocumentPage.vue') },
      { path: '/history', name: 'history', component: () => import('pages/HistoryPage.vue') },
      { path: '/templates', name: 'templates', component: () => import('pages/TemplatesPage.vue') },
      { path: '/settings', name: 'settings', component: () => import('pages/SettingsPage.vue') }
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

export default routes
