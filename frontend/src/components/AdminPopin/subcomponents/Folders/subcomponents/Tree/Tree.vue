<script setup>
    import { ref, onMounted } from 'vue';

    import { useChatStore } from '@/stores/chat'

    import AdminLoader from '@/components/AdminPopin/subcomponents/AdminLoader/AdminLoader.vue'
    import TreeItem from './TreeItem.vue';

    import FolderManager from '@/helpers/folderManager.js'
    import { isEmpty } from '@/helpers/utils.js'

    const loader = ref(null)
    const folderManager = new FolderManager()
    const chatStore = new useChatStore()

    onMounted(() => {
        if (isEmpty(chatStore.folders)) {
            loader.value.load(true)
            folderManager.getFolders()
            .then(function(result) {
                chatStore.folders = result.folders
                loader.value.load(false)
            });
        }
    })

</script>

<template>
    <AdminLoader ref="loader"/>
    <ul class="tree" v-for="(folder, index) in chatStore.folders">
        <TreeItem :folder="{
            ...folder,
            path: folder.name,
            open: true,
            index: index,
        }"
        />
    </ul>
</template>


<style lang="scss">@import "./tree.scss";</style>