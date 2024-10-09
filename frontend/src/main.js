import { createApp } from "vue";
import { createPinia } from "pinia";
import { createI18n } from 'vue-i18n';

import App from "./App.vue";
import router from "./router";

import local_fr from './locals/fr.json'
import local_en from './locals/en.json'


const i18n = createI18n({
    legacy: false,
    locale: 'fr',
    fallbackLocale: 'en',
    messages: {
      fr: local_fr,
      en: local_en
    }
  });

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(i18n)
app.mount("#app");
