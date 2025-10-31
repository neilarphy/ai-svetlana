<template>
  <q-page class="q-pa-xl" :class="$q.dark.isActive ? 'bg-grey-10' : 'bg-grey-2'">
    <div class="q-mx-auto" style="max-width: 1100px">
      <h1 class="text-h4 text-weight-bold q-ma-none q-mb-md" :class="$q.dark.isActive ? 'text-white' : 'text-primary'">
        Настройки
      </h1>

      <q-card flat bordered>
        <q-list separator>
          <q-item tag="label" v-ripple>
            <q-item-section>
              <q-item-label>Уведомления по Email</q-item-label>
              <q-item-label caption>Получать уведомления о готовых документах</q-item-label>
            </q-item-section>
            <q-item-section side top>
              <q-toggle color="primary" v-model="notifications" />
            </q-item-section>
          </q-item>

          <q-item tag="label" v-ripple>
            <q-item-section>
              <q-item-label>Сохранять историю</q-item-label>
              <q-item-label caption>Автоматически сохранять все сгенерированные документы</q-item-label>
            </q-item-section>
            <q-item-section side top>
              <q-toggle color="primary" v-model="saveHistory" />
            </q-item-section>
          </q-item>
        </q-list>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'

defineOptions({
  name: 'SettingsPage'
});

const notifications = ref(true)
const saveHistory = ref(true)
</script>
