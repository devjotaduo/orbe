import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import en from "./locales/en.json";
import ru from "./locales/ru.json";
import zh from "./locales/zh.json";
import ja from "./locales/ja.json";
import ptBR from "./locales/pt-BR.json";
import id from "./locales/id.json";
const resources = {
  en: {
    translation: en,
  },
  ru: {
    translation: ru,
  },
  zh: {
    translation: zh,
  },
  ja: {
    translation: ja,
  },
  pt: {
    translation: ptBR,
  },
  "pt-BR": {
    translation: ptBR,
  },
  "pt-br": {
    translation: ptBR,
  },
  id: {
    translation: id,
  },
};

i18n.use(initReactI18next).init({
  resources,
  lng: localStorage.getItem("language") || navigator.language || "pt-BR",
  fallbackLng: ["pt-BR", "pt", "en"],
  supportedLngs: Object.keys(resources),
  nonExplicitSupportedLngs: true,
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
