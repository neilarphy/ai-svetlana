<template>
  <q-page class="q-pa-xl" :class="$q.dark.isActive ? 'bg-grey-10' : 'bg-grey-2'">
    <div class="q-mx-auto" style="max-width: 1100px">
      <!-- Header -->
      <div class="q-mb-xl">
        <div class="row items-center justify-between q-mb-md">
          <div>
            <h1 class="text-h4 text-weight-bold q-ma-none" :class="$q.dark.isActive ? 'text-white' : 'text-primary'">
              Создание документа
            </h1>
            <p class="text-subtitle1 q-ma-none" :class="$q.dark.isActive ? 'text-grey-5' : 'text-grey-7'">
              Выберите тип документа для создания
            </p>
          </div>
          <q-chip square :color="$q.dark.isActive ? 'grey-9' : 'yellow-2'" :text-color="$q.dark.isActive ? 'white' : 'grey-8'" icon="sparkles">
            ИИ-генерация
          </q-chip>
        </div>
      </div>

      <!-- Document Type Selection -->
      <div class="row q-col-gutter-lg">
        <div
          v-for="docType in documentTypes"
          :key="docType.id"
          class="col-12 col-md-4"
        >
          <q-card class="cursor-pointer full-height card-hover" flat bordered @click="handleTypeSelect(docType)">
            <q-item class="q-pa-lg">
              <q-item-section avatar>
                <q-avatar :color="docType.color" text-color="white" :icon="docType.icon" size="64px" font-size="32px" style="border-radius: 16px;" />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-h6 text-weight-bold">{{ docType.name }}</q-item-label>
                <q-item-label caption :class="{ 'text-grey-4': $q.dark.isActive }">{{ docType.fields.length }} полей для заполнения</q-item-label>
              </q-item-section>
            </q-item>
          </q-card>
        </div>
      </div>

      <!-- Form Dialog -->
      <q-dialog v-model="formDialog">
        <q-card v-if="selectedType" style="width: 700px; max-width: 80vw;">
          <q-card-section>
            <div class="text-h6 row items-center q-gutter-sm">
              <q-icon :name="selectedType.icon" size="md" :color="selectedType.color" />
              <span>{{ selectedType.name }}</span>
            </div>
          </q-card-section>

          <q-card-section class="q-pt-none">
            <div v-if="!isGenerating">
              <q-banner inline-actions rounded class="bg-blue-1 text-primary q-mb-md">
                <template v-slot:avatar>
                  <q-icon name="info" />
                </template>
                Чем больше информации вы предоставите, тем лучше будет результат.
              </q-banner>
              <q-form @submit="handleFormSubmit" class="q-gutter-y-sm q-mt-lg" ref="documentForm">
                <div class="row q-col-gutter-md">
                  <div class="col-6">
                    <q-input
                      v-model="formData.recipient_pos"
                      label="Кому (должность)"
                      :rules="[val => val && val.length > 0 || 'Поле обязательно для заполнения']"
                      outlined
                      stack-label
                    />
                  </div>
                  <div class="col-6">
                    <q-input
                      v-model="formData.recipient_name"
                      label="ФИО получателя"
                      :rules="[val => val && val.length > 0 || 'Поле обязательно для заполнения']"
                      outlined
                      stack-label
                    />
                  </div>
                </div>
                <div class="row q-col-gutter-md">
                  <div class="col-6">
                    <q-input
                      v-model="formData.sender_pos"
                      label="От кого (должность)"
                      :rules="[val => val && val.length > 0 || 'Поле обязательно для заполнения']"
                      outlined
                      stack-label
                    />
                  </div>
                  <div class="col-6">
                    <q-input
                      v-model="formData.sender_name"
                      label="ФИО отправителя"
                      :rules="[val => val && val.length > 0 || 'Поле обязательно для заполнения']"
                      outlined
                      stack-label
                    />
                  </div>
                </div>
                <q-input
                  v-model="formData.user_prompt"
                  label="Суть обращения (опишите своими словами)"
                  type="textarea"
                  placeholder="Опишите причину, цель или просьбу..."
                  outlined
                  stack-label
                />
              </q-form>
            </div>
            <div v-else class="text-center q-pa-xl">
              <q-spinner-cube color="primary" size="4em" />
              <div class="q-mt-md text-subtitle1">Идет генерация документа...</div>
            </div>
          </q-card-section>

          <q-card-actions align="right" class="q-pa-md" :class="$q.dark.isActive ? 'bg-grey-9' : 'bg-grey-2'">
            <q-btn label="Отмена" flat @click="formDialog = false" :disable="isGenerating" />
            <q-btn
              label="Создать документ"
              color="primary"
              :loading="isGenerating"
              @click="() => documentForm.submit()"
              unelevated
            />
          </q-card-actions>
        </q-card>
      </q-dialog>

    </div>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'

defineOptions({
  name: 'CreateDocumentPage'
})

const $q = useQuasar()
const router = useRouter()
const selectedType = ref(null)
const formData = ref({})
const isGenerating = ref(false)
const formDialog = ref(false)
const documentForm = ref(null)

const documentTypes = [
  {
    id: 'служебная_записка',
    name: 'Служебная записка',
    icon: 'description',
    color: 'primary',
    fields: [
      { name: 'recipient_pos', label: 'Кому (должность)', type: 'text', required: true },
      { name: 'recipient_name', label: 'ФИО получателя', type: 'text', required: true },
      { name: 'sender_pos', label: 'От кого (должность)', type: 'text', required: true },
      { name: 'sender_name', label: 'ФИО отправителя', type: 'text', required: true },
      { name: 'user_prompt', label: 'Суть обращения (опишите своими словами)', type: 'textarea', required: false, placeholder: 'Опишите причину, цель или просьбу...' },
    ]
  },
   {
    id: 'письмо',
    name: 'Деловое письмо',
    icon: 'email',
    color: 'primary',
    fields: [
      { name: 'sender_name', label: 'ФИО отправителя', type: 'text', required: true },
      { name: 'sender_pos', label: 'Должность отправителя', type: 'text', required: true },
      { name: 'recipient_name', label: 'ФИО получателя', type: 'text', required: true },
      { name: 'recipient_pos', label: 'Должность получателя', type: 'text', required: true },
      { name: 'user_prompt', label: 'Текст письма (опишите своими словами)', type: 'textarea', required: false, placeholder: 'Основное содержание письма...' },
    ]
  },
  {
    id: 'приказ',
    name: 'Приказ',
    icon: 'gavel',
    color: 'accent',
    fields: []
  },
  {
    id: 'заявление',
    name: 'Заявление',
    icon: 'article',
    color: 'secondary',
    fields: []
  },
    {
    id: 'протокол',
    name: 'Протокол',
    icon: 'groups',
    color: 'primary',
    fields: []
  },
  {
    id: 'докладная_записка',
    name: 'Докладная записка',
    icon: 'feed',
    color: 'accent',
    fields: []
  }
];

function handleTypeSelect (type) {
  selectedType.value = type
  formData.value = {}
  formDialog.value = true
}

async function handleFormSubmit () {
  isGenerating.value = true
  let success = false
  
  const requestData = {
    document_type: selectedType.value.id,
    recipient: {
      name: formData.value.recipient_name || "",
      position: formData.value.recipient_pos || ""
    },
    sender: {
      name: formData.value.sender_name || "",
      position: formData.value.sender_pos || ""
    },
    user_prompt: formData.value.user_prompt || ""
  }

  try {
    await api.post('/api/generate', requestData)
    success = true
    $q.notify({
      color: 'positive',
      icon: 'check_circle',
      message: 'Документ успешно сгенерирован!'
    })
  } catch (error) {
    success = false
    console.error('Error generating document:', error)
    $q.notify({
      color: 'negative',
      icon: 'error',
      message: 'Ошибка при создании документа. Пожалуйста, проверьте консоль.'
    })
  } finally {
    isGenerating.value = false
    formDialog.value = false // Always close the dialog
    if (success) {
      setTimeout(() => {
        router.push('/history')
      }, 500) // Delay for notification visibility
    }
  }
}
</script>

<style lang="scss" scoped>
.card-hover {
  border-radius: 12px;
  transition: transform 0.2s, box-shadow 0.2s;
}
.card-hover:hover {
  transform: translateY(-4px);
  border-color: var(--q-primary);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
}
</style>
