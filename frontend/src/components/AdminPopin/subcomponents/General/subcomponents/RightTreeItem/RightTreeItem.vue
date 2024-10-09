<script setup>
    import { defineProps, ref, computed } from 'vue';
    import { Folder, FolderOpen, FolderArchive, Crown } from 'lucide-vue-next';
    
    const emits = defineEmits(['selectFolder'])
    const props = defineProps({
        folder: {
            type: Object,
            required: true,
        },
        parent: {
            type: Object,
            required: false
        },
    })

    // OPEN CLOSE FOLDER
    const folderOpen = ref(true)
    const isOpen = computed(() => {
        if (props.folder.children.length) return folderOpen.value
        else return null
    })

    const toggleList = () => {
        if (props.folder.children.length) {
            folderOpen.value = !folderOpen.value
        }
    }

    const selectFolder = (folderPath) => {
        emits('selectFolder', folderPath)
    }

</script>

<template>
    <button 
        class="tree__button"
    >
        <Folder @click="toggleList" :class="['tree__icon', { 'open': isOpen == false}]" color="white"/>
        <FolderOpen @click="toggleList" :class="['tree__icon', { 'open': isOpen == true}]" color="white"/>
        <FolderArchive @click="toggleList" :class="['tree__icon', { 'open': isOpen == null}]" color="white"/>
        <span @click="toggleList">{{ folder.name }}/</span>

        <button @click="selectFolder(folder.path)" class="tree__button__option rights__crown">
            <Crown color="white"/>
        </button>

    </button>


    <div :class="['tree__list', { 'open': isOpen}]">
        <!-- FOLDER LIST -->
        <ul class="tree__list__folder" v-for="(subfolder,  index) in folder.children">
            <RightTreeItem
                :parent="folder"
                :folder="{
                    ...subfolder,
                    path: folder.path + '/' + subfolder.name,
                    index: index,
                    open: isOpen,
                }"
                @selectFolder="selectFolder"
            />
        </ul>
    </div>

</template>