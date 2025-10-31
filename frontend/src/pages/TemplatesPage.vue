<template>
  <q-page class="q-pa-xl" :class="$q.dark.isActive ? 'bg-grey-10' : 'bg-grey-2'">
    <div class="q-mx-auto" style="max-width: 1100px">
      <h1 class="text-h4 text-weight-bold q-ma-none q-mb-md" :class="$q.dark.isActive ? 'text-white' : 'text-primary'">
        Шаблоны документов
      </h1>

      <q-list bordered :class="$q.dark.isActive ? 'bg-grey-9' : 'bg-white'" class="rounded-borders">
        <q-item v-for="template in templates" :key="template">
          <q-item-section>
            <q-item-label>{{ template }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from 'boot/axios'

defineOptions({
  name: 'TemplatesPage'
});

const templates = ref([])

async function fetchTemplates() {
  try {
    const response = await api.get('/api/templates')
    templates.value = response.data
  } catch (error) {
    console.error('Error fetching templates:', error)
  }
}

onMounted(() => {
  fetchTemplates()
})
</script>
