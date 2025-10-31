<template>
  <q-page class="q-pa-xl" :class="$q.dark.isActive ? 'bg-grey-10' : 'bg-grey-2'">
    <div class="q-mx-auto" style="max-width: 1100px">
      <h1 class="text-h4 text-weight-bold q-ma-none q-mb-md" :class="$q.dark.isActive ? 'text-white' : 'text-primary'">
        История документов
      </h1>

      <q-card flat bordered>
        <div class="row items-center q-pa-sm text-caption text-grey-7 gt-sm" style="border-bottom: 1px solid #e0e0e0">
          <div class="col-7">Документ</div>
          <div class="col-2">Тип</div>
          <div class="col-2">Дата создания</div>
          <div class="col-1 text-center">Действия</div>
        </div>

        <q-list separator>
          <q-item v-for="doc in documents" :key="doc.doc_filename">
            <q-item-section class="col-7 gt-sm">
              <q-item-label class="text-weight-bold ellipsis">{{ doc.display_name }}</q-item-label>
              <q-tooltip :delay="500">
                {{ doc.display_name }}
              </q-tooltip>
            </q-item-section>
            <q-item-section class="col-2">
              <q-chip :color="getDocTypeColor(doc.document_type)" text-color="white" size="sm" :label="doc.document_type" />
            </q-item-section>
            <q-item-section class="col-2 gt-sm">
              {{ formatDate(doc.created_at) }}
            </q-item-section>
            <q-item-section side class="col-1">
              <q-btn flat round dense icon="download" @click="downloadDocument(doc.doc_filename)" />
            </q-item-section>
          </q-item>

          <q-item-label v-if="documents.length === 0" header class="text-center text-grey-6 q-py-xl">
            <q-icon name="history" size="lg" />
            <div class="text-h6 q-mt-md">История пуста</div>
            <div>Здесь будет отображаться история сгенерированных документов.</div>
          </q-item-label>
        </q-list>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from 'boot/axios'

defineOptions({
  name: 'HistoryPage'
});

const documents = ref([])

function getDocTypeColor(docType) {
  const colors = {
    'Письмо': 'primary',
    'Служебная записка': 'orange',
    'Справка': 'green',
    'Докладная записка': 'purple',
    'Объяснительная записка': 'teal',
  };
  return colors[docType] || 'grey';
}

async function fetchDocuments() {
  try {
    const response = await api.get('/api/documents')
    // Sort documents by creation date, newest first
    const sortedDocs = response.data.sort((a, b) => {
      return new Date(b.created_at) - new Date(a.created_at);
    });
    documents.value = sortedDocs;
  } catch (error) {
    console.error('Error fetching documents:', error)
  }
}

function downloadDocument(filename) {
  window.open(`${api.defaults.baseURL}/api/download/${filename}`, '_blank')
}

function formatDate(isoString) {
  const date = new Date(isoString);
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

onMounted(fetchDocuments)
</script>
