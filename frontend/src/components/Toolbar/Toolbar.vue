<script setup>
import { reactive, ref, watch, onMounted } from "vue";
import { useUserStore } from "@/stores/user";
import { useChatStore } from "@/stores/chat";
import { SessionStore } from "@/stores/session";
import ChatManager from "@/helpers/chatManager.js";
import UserManager from "@/helpers/userManager.js";
import AdminPopin from "@/helpers/adminPopin.js";
import Popin from "@/components/Popin/Popin.vue"

import {
    FilePenLine,
    Trash2,
    Pencil,
    LogOut,
    Ellipsis,
    ChevronLeft,
    Settings,
} from "lucide-vue-next";

import { useI18n } from "vue-i18n";
const { t } = useI18n();


const chatManager = new ChatManager();
const adminPopin = new AdminPopin();
const userManager = new UserManager();

const chatStore = useChatStore();
const userStore = useUserStore();
const session = SessionStore();

const chats = ref([])
const tooltips = reactive({});

const toolbar = reactive({
    isOpen: true,
    isOpaque: false,
    toggle() {
        this.isOpen = !this.isOpen;
        document.querySelector('.chatbox').classList.toggle('full-width')
    },
    toggleOpacity() {
        this.isOpaque = !this.isOpaque;
    },
});

const editChatSession = (id) => {
    const chat = chatStore.chats.find((item) => item.id === id);
    if (chat) chat.edit = true;
};

const editChatTitle = (id, newValue) => {
    const chat = chatStore.chats.find((item) => item.id === id);
    if (chat) {
        chat.edit = false;
        chat.title = newValue;
        chatManager.updateChat(chat.id, { title: chat.title });
    }
};

const handleTooltipVisibility = (chatId, event) => {
    const visibleTextEl = event.target;
    const isOverflowing = visibleTextEl.offsetWidth < visibleTextEl.scrollWidth;
    tooltips[chatId] = isOverflowing;
};

const handleClick = (event, id) => {
    const targetClass = event.target.classList
    if (targetClass.contains('visible-text') || targetClass.contains('toolbar__nav__ul__li')) {
        session.loadChat(id)
    }
}


const popins = ref({})
const setupPopins = () => {
    popins.value = {
        'delete': {
            title: t('delete_title'),
            open: false,
            selectedChat: {},
            handleFunction: {
                deleteChat: (id) => {
                    session.deleteChat(id);
                    popins.value.delete.open = false
                }
            },
        }
    }
}

const togglePopin = (popin_name, chat) => {
    popins.value[popin_name].open = !popins.value[popin_name].open
    if (popins.value[popin_name].open && chat) {
        popins.value[popin_name].selectedChat = chat
    }
}
const closePopin = (popin_name) => {
    popins.value[popin_name].open = false

}

watch(() => chatStore.chats, () => {
    chats.value = chatStore.chats
})

onMounted(() => {
    setupPopins()
})

</script>


<template>
    <header class="toolbar" :class="{ close: !toolbar.isOpen, 'opacity-it': toolbar.isOpaque }">
        <!-- TOOLBAR HEADER -->
        <div class="toolbar__header">
            <button class="toolbar__header__addchat" @click="session.createChat">
                <img class="toolbar__header__addchat__img" src="@/assets/img/aisystem.webp" alt="" />
                <span>{{ $t('new') }} {{ $t('chat') }}</span>
                <FilePenLine color="white" />
            </button>
        </div>

        <!-- CHAT LIST -->
        <nav class="toolbar__nav">
            <ul class="toolbar__nav__ul">
                <li class="toolbar__nav__ul__li" 
                    v-for="chatsession in chats"
                    :key="chatsession?.id"
                    v-show="chatsession?.has_messages"
                    @click="(e) => handleClick(e, chatsession.id)"
                    :id="'chat-' + chatsession.id"
                    :chat-selected="chatStore.currentChatId == chatsession?.id ? true : false"
                >
                    <button class="toolbar__nav__ul__li__button">
                        <div class="toolbar__nav__ul__li__button__title">
                            <div v-if="chatsession.edit">
                                <input type="text" name="" id="" :value="chatsession.title"
                                    @keyup.enter.exact=" editChatTitle(chatsession.id, $event.target.value)" />
                            </div>
                            <div v-else class="tooltip">
                                <span class="visible-text"
                                    v-if="chatsession.title"
                                    @mouseenter="(event) => handleTooltipVisibility(chatsession.id, event)"
                                    @mouseleave="() => (tooltips[chatsession.id] = false)">
                                    {{ chatsession.title }}
                                </span>
                                <span class="visible-text visible-text-loading" v-else>
                                    {{ $t('new') }} {{ $t('chat') }}
                                </span>
                                <div v-if="tooltips[chatsession.id]" class="tooltip-text">
                                    {{ chatsession.title }}
                                </div>
                            </div>
                        </div>
                        <div class="toolbar__nav__ul__li__button__cases">
                            <Ellipsis color="white" class="more"/>
                            <div class="toolbar__nav__ul__li__button__cases__drop">
                                <span class="edit" @click="editChatSession(chatsession.id)">
                                    <Pencil color="white" />
                                </span>
                                <span class="delete" @click="togglePopin('delete', chatsession)">
                                    <Trash2 color="red" />
                                </span>
                            </div>
                        </div>
                    </button>

                </li>
            </ul>
        </nav>

        <!-- POPIN DELETE -->
        <Popin
            v-if="popins?.delete"
            :title="popins.delete.title"
            :popinOpen="popins.delete.open"
            :embedCloseButton="true"
            customContainerClass="toolbar__popin__container"
            @closePopin="closePopin('delete')"
        >
            {{ $t('delete_msg') }} <strong>"{{ popins.delete.selectedChat?.title }}"</strong>
            <div class="toolbar__popin__buttons">
                <button :title="t('back')" @click="togglePopin('delete', null)">
                    {{ $t('back') }}
                </button>
                <button :title="t('delete')" class="btn-delete" @click="popins.delete.handleFunction.deleteChat(popins.delete.selectedChat?.id)">
                    {{ $t('delete') }}
                </button>
            </div>
        </Popin>

        <!-- USER PROFIL -->
        <div class="toolbar__profil">
            <div class="toolbar__profil__button">
                <img class="toolbar__profil__button__img"
                    src="@/assets/img/profile.webp"
                    alt="Profile" />
                <span>{{ userStore.user.username }}</span>
                <button @click="adminPopin.toggleModal()">
                    <Settings color="white" />
                </button>
                <button @click="userManager.logout()">
                    <LogOut color="white" />
                </button>
            </div>
        </div>

        <!-- HIDE TOOLBAR -->
        <button class="toolbar__toggle" @click="toolbar.toggle()" @mouseover="toolbar.toggleOpacity()"
            @mouseout="toolbar.toggleOpacity()">
            <ChevronLeft color="white" />
        </button>
    </header>
</template>

<style lang="scss">
@import "./toolbar.scss";
</style>
