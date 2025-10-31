import { defineStore } from 'pinia';
import { api } from 'boot/axios';

export const useDocumentStore = defineStore('document', {
  state: () => ({
    documents: [],
    loading: false,
    error: null,
  }),
  getters: {
    documentCount: (state) => state.documents.length,
  },
  actions: {
    async fetchDocuments() {
      this.loading = true;
      this.error = null;
      try {
        const response = await api.get('/api/documents');
        this.documents = response.data;
      } catch (error) {
        this.error = 'Не удалось загрузить документы';
        console.error(this.error, error);
      } finally {
        this.loading = false;
      }
    },
  },
});
