<script setup>
    import { shallowRef } from 'vue';
    
    import { useUserStore } from "@/stores/user";

    import DeleteChats from './subcomponents/DeleteChats/DeleteChats.vue'
    import FolderRightsManagement from './subcomponents/FolderRightsManagement/FolderRightsManagement.vue'
    import PipelineRightsManagement from './subcomponents/PipelineRightsManagement/PipelineRightsManagement.vue'

    const emits = defineEmits(['updateInfo'])
    const userStore = useUserStore()

    const currentComponent = shallowRef(null)
    const components = {
        'DeleteChats': DeleteChats,
        'FolderRightsManagement': FolderRightsManagement,
        'PipelineRightsManagement': PipelineRightsManagement,
    }

    const back = () => {
        currentComponent.value = null
    }

    const openComponent = (componentName) => {
        currentComponent.value = components[componentName]
    }

</script>

<template>

    <ul class="admin__general" v-if="!currentComponent">
        <li class="admin__general__item">
            <p>{{ $t('delete') }} {{  $t('all_plural') }} {{ $t('chat_plural') }}</p>
            <button @click="openComponent('DeleteChats')" class="red-button">
                {{ $t('delete') }} {{ $t('all') }}
            </button>
        </li>
        <li class="admin__general__item" v-if="userStore.user.is_superuser || userStore.user.is_staff">
            <p>{{ $t('management') }} {{$t('of_plural')}} {{$t('folder_rights') }}</p>
            <button @click="openComponent('FolderRightsManagement')" class="button">
                {{ $t('manage') }}
            </button>
        </li>
        <li class="admin__general__item" v-if="userStore.user.is_superuser || userStore.user.is_staff">
            <p>{{ $t('management') }} {{$t('of_plural')}} {{$t('pipelines_rights') }}</p>
            <button @click="openComponent('PipelineRightsManagement')" class="button">
                {{ $t('manage') }}
            </button>
        </li>
    </ul>

    <component v-if="currentComponent" :is="currentComponent" @back="back"/>

</template>

<style lang="scss">@import "./general.scss";</style>
