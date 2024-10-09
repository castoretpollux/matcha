<script setup>
import { useChatStore } from "@/stores/chat";
import MediaBar from "@/components/MediaBar/mediabar.js"
import ChatManager from "../../helpers/chatManager";
import { ChevronRight } from 'lucide-vue-next';
import { getUrlType } from "@/helpers/utils.js";

const mediabar = new MediaBar();
const chatStore = useChatStore();
const chatmanager = new ChatManager();

</script>
<template>
    <!-- TAB FILES LIST -->
    <div class="mediabar" v-show="chatStore.chat.files?.length">
        <button class="mediabar__button" @click="mediabar.toggle()">
            <ChevronRight color="white"/>
        </button>
        <ul class="mediabar__list">
            <li>
                <p class="mediabar__list__indication">Sélectionner un fichier pour l'intégrer dans la requête à l'IA</p>
            </li>
            <li class="mediabar__list__item" v-for="file, index in chatStore.chat.files" :key="index">
                <label :class="{ checked: file.favorite }">
                    <input type="checkbox" :checked="file.favorite" @change="chatmanager.setFileFavorite(index)"/>
                    <img :src="file.url" v-if="getUrlType(file.url) == 'image'" alt="" />
                    <img src="https://cdn-icons-png.flaticon.com/512/337/337946.png"
                        v-if="getUrlType(file.url) == 'pdf'" alt="" />
                    <img src="https://cdn-icons-png.flaticon.com/512/3979/3979406.png"
                        v-if="getUrlType(file.url) == 'doc'" alt="" />
                    {{ file.name }}
                </label>
            </li>
        </ul>
    </div>
</template>
<style lang="scss">@import "./mediabar.scss";</style>
