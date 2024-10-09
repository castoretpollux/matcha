<script setup>
import { useChatStore } from "@/stores/chat";
import { SessionStore } from "@/stores/session";

import ChatForm from "@/components/ChatForm/ChatForm.vue";
import ChatMessage from '@/components/ChatMessage/ChatMessage.vue';
import AdminPopin from '@/components/AdminPopin/AdminPopin.vue';

const chatStore = useChatStore();
const session = SessionStore();

</script>

<template>
    <div class="chatbox"  v-if="chatStore.currentChatId">
        <h1 class="chatbox__header" v-if="!session.getChat()?.has_messages">
            <img src="@/assets/img/aisystem.webp" alt="AI System" />
            <span>{{ $t('welcome_dashboard') }}</span>
        </h1>

        <ul class="chatbox__logpanel" v-show="false" :id="'log-' + chatStore.currentChatId"></ul>

        <ChatMessage/>
        <ChatForm/>
    </div>

    <AdminPopin/>

</template>

<style lang="scss">@import "./chatbox.scss";</style>