<template>
  <q-layout view="lHh Lpr lFf" :class="$q.dark.isActive ? 'bg-grey-10' : 'bg-grey-2'">
    <q-header bordered :class="$q.dark.isActive ? 'bg-grey-9' : 'bg-white'" class="text-grey-8">
      <q-toolbar class="q-px-lg q-py-sm">
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" class="lt-md" />
        <div class="row items-center no-wrap q-gutter-md">
          <q-avatar size="42px" square style="border-radius: 12px;">
            <img src="~assets/robot_avatar.png">
          </q-avatar>
          <div>
            <div class="text-h6 text-weight-bold" :class="$q.dark.isActive ? 'text-white' : 'text-primary'">Робот Светлана</div>
            <div class="text-caption" :class="$q.dark.isActive ? 'text-grey-5' : 'text-grey-7'">Помощник по документам</div>
          </div>
        </div>
        <q-space />
        <div class="row items-center no-wrap q-gutter-md">
           <div class="text-right gt-sm">
            <div class="text-weight-bold" :class="$q.dark.isActive ? 'text-grey-3' : 'text-grey-8'">СПб ГКУ «ГМЦ»</div>
            <div class="text-caption" :class="$q.dark.isActive ? 'text-grey-5' : 'text-grey-7'">Городской мониторинговый центр</div>
          </div>
          <q-avatar size="lg" color="accent" text-color="white" class="text-weight-bold">П</q-avatar>
        </div>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above :width="320" class="q-pa-md" :class="$q.dark.isActive ? 'bg-grey-10' : 'bg-grey-2'">
      <div class="column full-height">
        <q-card class="my-card rounded-borders q-mb-md" flat bordered>
          <q-card-section class="text-center q-pa-md">
            <q-avatar size="80px" class="q-mb-sm">
              <img src="~assets/robot_avatar.png">
            </q-avatar>
            <div class="text-h6 text-weight-bold">Светлана</div>
            <div class="text-subtitle2 row items-center no-wrap inline-block" :class="$q.dark.isActive ? 'text-grey-4' : 'text-grey-7'">
              <q-icon name="sparkles" color="yellow-8" class="q-mr-xs" />
              <span>ИИ-Ассистент</span>
            </div>
          </q-card-section>
          <q-card-actions class="q-pa-md q-pt-none">
            <q-btn to="/" icon="add" label="Новый документ" color="primary" class="full-width" unelevated />
          </q-card-actions>
        </q-card>

        <q-list class="col" padding>
          <q-item
            v-for="item in menuItems"
            :key="item.name"
            :to="item.url"
            clickable
            v-ripple
            class="q-mb-sm rounded-borders"
            active-class="bg-blue-1 text-primary text-weight-bold"
            :exact="item.url === '/'"
          >
            <q-item-section avatar>
              <q-avatar :color="item.color" text-color="white" :icon="item.icon" />
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ item.name }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>

        <div>
          <q-card class="my-card q-mb-sm" flat bordered>
            <q-item>
              <q-item-section>
                <q-item-label>Темная тема</q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-toggle v-model="darkMode" @update:model-value="toggleDarkMode" />
              </q-item-section>
            </q-item>
          </q-card>
          <q-card class="my-card" flat bordered>
            <q-card-section>
              <div class="row justify-between items-center">
                <span class="text-caption">Документов</span>
                <span class="text-weight-bold text-primary">{{ documentStore.documentCount }}</span>
              </div>
              <q-linear-progress :value="documentStore.documentCount / 100" class="q-mt-sm" />
            </q-card-section>
          </q-card>
        </div>
      </div>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useDocumentStore } from 'src/stores/document-store'

const $q = useQuasar()
const documentStore = useDocumentStore()
const leftDrawerOpen = ref(false)
const darkMode = ref($q.dark.isActive)

function toggleDarkMode (val) {
  $q.dark.set(val)
}

const menuItems = [
  { name: 'Создание документа', url: '/', icon: 'description', color: 'primary' },
  { name: 'История', url: '/history', icon: 'history', color: 'accent' },
  { name: 'Шаблоны', url: '/templates', icon: 'source', color: 'primary' },
  { name: 'Настройки', url: '/settings', icon: 'settings', color: 'secondary' }
]

function toggleLeftDrawer () {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

onMounted(() => {
  documentStore.fetchDocuments()
})
</script>

<style lang="scss">
.q-drawer {
  border-right: 1px solid rgba(0,0,0,0.12);
}
.body--dark .q-drawer {
  border-right: 1px solid rgba(255,255,255,0.28);
}
</style>
