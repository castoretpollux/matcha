<script setup>
import { ref, shallowRef, onMounted, onUnmounted } from 'vue';

import Folders from '@/components/AdminPopin/subcomponents/Folders/Folders.vue';
import DynamicPipelineList from "@/components/AdminPopin/subcomponents/DynamicPipelineList/DynamicPipelineList.vue"
import RegistredPromptList from "@/components/AdminPopin/subcomponents/RegistredPromptList/RegistredPromptList.vue"
import General from "@/components/AdminPopin/subcomponents/General/General.vue"
import { X, Settings, Bot, MessageSquareMore, FolderCog } from "lucide-vue-next";
import { useI18n } from "vue-i18n";
const { t } = useI18n();

// Modal management
const adminPopin = ref(null)
const closePopin = ref(null)
const infoMsg = ref('')

const closeAdminPopin = (e) => {
    let target = e.target
    if (target == adminPopin.value || target == closePopin.value) {
        adminPopin.value.classList.remove('open')
    }
}

const forceClosePopin = () => {
    adminPopin.value.classList.remove('open')
}

// Components management
const components = [
    {label: t('general'), component: General, icon: Settings },
    {label: t('pipeline_plural'), component: DynamicPipelineList, icon: Bot},
    {label: t('prompt_plural'), component: RegistredPromptList, icon: MessageSquareMore},
    {label: t('folder_plural'), component: Folders, icon: FolderCog}
]

const adminNav = ref(null)
const selectedComponent = shallowRef(components[0].component);
const selectComponent = (e, component) => {
    adminNav.value.querySelectorAll('button').forEach((button) => {
        button.classList.remove('active')
    })
    e.target.classList.add('active')
    selectedComponent.value = component;
}; 

const updateInfo = (info) => {
    infoMsg.value = info
    setTimeout(() => {
        infoMsg.value = ''
    }, 10000);
}

onMounted(() => {
    window.addEventListener('keydown', (e) => handleKeyDown(e))
})

onUnmounted(() => {
    window.removeEventListener('keydown', (e) => handleKeyDown(e))
})

const handleKeyDown = (e) => {
    if (e.key == 'Escape') {
        forceClosePopin()
    }
}

</script>

<template>

    <div class="admin-popin" ref="adminPopin" @click="closeAdminPopin">
        <div class="admin-popin__container">

            <div class="admin-popin__container__header">
                <p class="admin-popin__container__header__title">{{ $t('administration') }}</p>
                <p v-if="infoMsg" class="admin-popin__container__header__info">
                    {{infoMsg}} 
                    <X color="white" @click="infoMsg = ''"/>
                </p>
                <button class="admin-popin__container__header__close" ref="closePopin" @click="closeAdminPopin">
                    <X color="white"/>
                </button>
            </div>

            <div ref="adminNav" class="admin-popin__container__nav">
                <button
                    v-for="item, index in components"
                    :class="index == 0 ? 'active' : ''"
                    @click="selectComponent($event, item.component)">
                        <component :is="item.icon" color="white"/>
                        {{ item.label }}
                </button>
            </div>

            <div class="admin-popin__container__content">
                <div class="admin-popin__container__content__container">
                    <component :is="selectedComponent" @updateInfo="updateInfo"/>
                </div>
            </div>
        
        </div>
    </div>

</template>

<style lang="scss">@import "./adminpopin.scss";</style>