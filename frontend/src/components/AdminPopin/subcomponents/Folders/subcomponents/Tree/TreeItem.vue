<script setup>
    import { defineProps, ref, computed, defineEmits, watch, onUnmounted, onMounted } from 'vue';
    import { Folder, FolderOpen, FolderPlus, FilePlus2, Trash2, Check, X, Loader, FolderPen, ShieldAlert, Ellipsis } from 'lucide-vue-next';
    import { useChatStore } from '@/stores/chat'
    import FolderManager from '@/helpers/folderManager.js'
    
    const chatStore = useChatStore()
    const folderManager = new FolderManager()
    const emits = defineEmits(['deleteFolderFromParent'])
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
    const folderOpen = ref(false)
    const isOpen = computed(() => {
        if (props.parent) {
            return props.parent.open && folderOpen.value
        } else {
            return folderOpen.value
        }
    })

    const toggleList = () => {
        folderOpen.value = !folderOpen.value
    }


    // ==== FOLDER ====

    const newFolderName = defineModel("newFolderName")
    const newFolderGroupRead = defineModel("newFolderGroupRead")
    const newFolderGroupWrite = defineModel("newFolderGroupWrite")
    const newFolderGroupUpdate = defineModel("newFolderGroupUpdate")
    const newFolderGroupDelete = defineModel("newFolderGroupDelete")

    newFolderGroupRead.value = true
    newFolderGroupWrite.value = true
    newFolderGroupUpdate.value = true
    newFolderGroupDelete.value = true

    const newFolderInput = ref(null)
    
    // ==== TOGGLE
    const addingFolder = ref(false)
    const toggleAddingFolder = () => {
        addingFolder.value = !addingFolder.value
        newFolderName.value = ''
        folderOpen.value = true
        if (addingFolder.value) newFolderInput.value.focus()
    }

    // method to check input
    const checkNewFolderName = (e) => {
        const regex = /^[a-zA-Z0-9._-]+$/;
        if (!regex.test(e.data)) {
            newFolderName.value = newFolderName.value.slice(0, newFolderName.value.length - 1);
        }
    }
    // ==== ADD
    const addFolder = () => {
        if (newFolderName.value?.length) {
            const isExist = props.folder.children.some((obj) => obj.name.toLowerCase() === newFolderName.value.toLowerCase());
            if (!isExist) {

                const newFolder = {
                    name: newFolderName.value,
                    can_read: newFolderGroupRead.value,
                    can_write: newFolderGroupWrite.value,
                    can_update: newFolderGroupUpdate.value,
                    can_delete: newFolderGroupDelete.value,
                    children: [],
                    documents: [],
                }

                props.folder.children.push(newFolder)

                folderManager.createFolder({
                    path: props.folder.path,
                    name: newFolder.name,
                    can_read: newFolderGroupRead.value,
                    can_write: newFolderGroupWrite.value,
                    can_update: newFolderGroupUpdate.value,
                    can_delete: newFolderGroupDelete.value,
                })

                // reset
                newFolderGroupRead.value = true
                newFolderGroupWrite.value = true
                newFolderGroupUpdate.value = true
                newFolderGroupDelete.value = true
                newFolderName.value = ''
                addingFolder.value = false
            }
        }
    }

    // ==== DELETE
    const popinDeleteFolder = ref(false)
    const toggleDeleteFolder = () => {
        popinDeleteFolder.value = !popinDeleteFolder.value
    }
    const deleteFolder = () => {
        popinDeleteFolder.value = false
        removeFolderToParentChildrens(props.folder.name)
        folderManager.deleteFolder({path: props.folder.path})
    }

    const removeFolderToParentChildrens = (name) => {
        emits('deleteFolderFromParent', name)
    }

    const deleteFolderFromParent = (childName) => {
        const index = props.folder.children.findIndex(child => child.name == childName);
        props.folder.children.splice(index, 1)
    }

    // ==== FILES =====

    // ==== GET MORE FILES
    const page = ref(1)
    const nextPage = () => {
        page.value++;
        const data = {
            path: props.folder.path,
            page: page.value
        }

        folderManager.getDocumentsPage(data)
        .then(_data => {
            props.folder.documents.push(..._data.results)
        })
    }

    // ==== ADD
    const addDocument = () => {
        if (fileInput.value.files.length) {
            // open folder
            folderOpen.value = true

            // for each file -> add document
            for (const file of fileInput.value.files) {
                chatStore.filesToUpload[props.folder.path].files[file.name] = {
                    state: 'progress'
                }
                folderManager.addDocument({
                    path: props.folder.path,
                    file: file
                })
            }
        }
    }

    // ==== ADD BY INPUT
    const fileInput = ref(null)
    const toggleFileInput = () => {
        fileInput.value.click()
    }

    // ==== ADD BY DRAG AND DROP
    const dropZone = ref(null)
    const dragover = (event) => {
        event.preventDefault();
        if (!dropZone.value.classList.contains('hover')) {
            dropZone.value.classList.add('hover');
        }
    };
    const dragleave = (_event) => {
        dropZone.value.classList.remove('hover');
    };
    const drop = (event) => {
        event.preventDefault();
        dropZone.value.classList.remove('hover');

        const dataTransfer = new DataTransfer();
        for (const file of event.dataTransfer.files) {
            const hasMatch = props.folder.documents.some((obj) => obj.title === file.name);
            if (!hasMatch) {
                dataTransfer.items.add(file);
            }
        }

        fileInput.value.files = dataTransfer.files
        addDocument();
    };

    // CLEAN STORE FileToUploads
    watch(() => chatStore.filesToUpload[props.folder.path]?.files, (e) => {
        if (e) {
            for (const [key, data] of Object.entries(e)) {
                if (data.state != 'progress' && data.state != 'error') {
                    // remove from files upload
                    removeDocumentToFilesToUpload(key)
                    // add into folder documents
                    props.folder.documents.push({title: key, url:data.url})
                }
            }
        }
    }, { deep: true });

    const removeDocumentToFilesToUpload = (name) => {
        delete chatStore.filesToUpload[props.folder.path].files[name]
    }

    // ==== DELETE
    const popinDeleteDocument = ref(false)
    const currentDeleteDocument = ref('')
    const toggleDeleteDocument = (document) => {
        popinDeleteDocument.value = !popinDeleteDocument.value
        if (document) {
            if (document.name) currentDeleteDocument.value = document.name
            if (document.title) currentDeleteDocument.value = document.title
        } else {
            currentDeleteDocument.value = ''
        }
    }

    const deleteDocument = () => {
        popinDeleteDocument.value = false
        deleteDocumentFromFolder(currentDeleteDocument.value)
        folderManager.deleteDocument({
            path: props.folder.path,
            title: currentDeleteDocument.value
        })
    }

    const deleteDocumentFromFolder = (documentTitle) => {
        const index = props.folder.documents.findIndex(document => document.documentTitle == documentTitle);
        props.folder.documents.splice(index, 1)
    }

    onMounted(() => {
        chatStore.filesToUpload[props.folder.path] = {
            files: {}
        }
    })

    onUnmounted(() => {
        // folder
        folderOpen.value = false

        // delete folder
        popinDeleteFolder.value = false

        // add folder
        newFolderName.value = ""
        newFolderInput.value = null
        addingFolder.value = false

        // delete document
        popinDeleteDocument.value = false
        currentDeleteDocument.value = ''

        // file upload
        chatStore.filesToUpload = {}
    })
</script>

<template>
    <button 
        class="tree__button"
        @dragover="dragover"
        @dragleave="dragleave"
        @drop="drop"
        ref="dropZone"
    >
        <Folder @click="toggleList" :class="['tree__icon', { 'open': !isOpen}]" color="white"/>
        <FolderOpen @click="toggleList" :class="['tree__icon', { 'open': isOpen}]" color="white"/>
        <span @click="toggleList">{{ folder.name }}/</span>

        <!-- ACTIONS -->
        <!-- add folder -->
        <button @click="toggleAddingFolder" v-if="folder.can_write" title="add folder" class="tree__button__option">
            <FolderPlus color="white"/>
        </button>
        <!-- add documents -->
        <button @click="toggleFileInput" v-if="folder.can_write" title="add document" class="tree__button__option">
            <FilePlus2 color="white"/>
        </button>
        <input type="file" ref="fileInput" class="tree__button__option__addfile" @change="addDocument" multiple>
        
        <!-- button delete -->
        <button @click="toggleDeleteFolder" v-if="parent && folder.can_delete" title="remove folder" class="tree__button__option tree__button__option__delete">
            <Trash2 color="white"/>
        </button>

    </button>


    <div :class="['tree__list', { 'open': isOpen}]">
        <!-- FOLDER LIST -->
        <ul class="tree__list__folder" v-for="(subfolder,  index) in folder.children">
            <TreeItem
                :parent="folder"
                :folder="{
                    ...subfolder,
                    path: folder.path + '/' + subfolder.name,
                    index: index,
                    open: isOpen,
                }"
                @deleteFolderFromParent="deleteFolderFromParent"
            />
        </ul>

        <!-- ADD NEW FOLDER -->
        <div class="tree__list__folder__add" v-show="addingFolder">
            <div class="tree__list__folder__add__row">
                <FolderPen class="tree__icon open" color="white"/>
                <input 
                    v-model="newFolderName"
                    ref="newFolderInput"
                    class="tree__list__folder__add__input"
                    placeholder="Folder name"
                    type="text"
                    @keyup.enter.exact="addFolder"
                    @input="checkNewFolderName"
                />
    
                <!-- BUTTON ADD FOLDER -->
                <button class="tree__list__folder__add__submit" @click="addFolder">
                    <Check class="tree__icon open" color="white"/>
                </button>
                <!-- BUTTON TOGGLE ADD FOLDER -->
                <button class="tree__list__folder__add__submit" @click="toggleAddingFolder">
                    <X class="tree__icon open" color="white"/>
                </button>
            </div>
            <div class="tree__list__folder__add__row">
                <label>
                    <input
                        type="checkbox"
                        checked
                        v-model="newFolderGroupRead"
                    />
                    {{ $t('group') }} {{ $t('can') }} {{ $t('read') }}
                </label>
                <label>
                    <input
                        type="checkbox"
                        checked
                        v-model="newFolderGroupWrite"
                    />
                    {{ $t('group') }} {{ $t('can') }} {{ $t('write') }}
                </label>
                <label>
                    <input
                        type="checkbox"
                        checked
                        v-model="newFolderGroupUpdate"
                    />
                    {{ $t('group') }} {{ $t('can') }} {{ $t('update') }}
                </label>
                <label>
                    <input
                        type="checkbox"
                        checked
                        v-model="newFolderGroupDelete"
                    />
                    {{ $t('group') }} {{ $t('can') }} {{ $t('delete') }}
                </label>
            </div>
        </div>

        <!-- CONTENT LIST -->
        <ul class="tree__list__content">
            <!-- CURRENT DOCS -->
            <li class="tree__list__content__item" v-for="document in folder.documents">
                <div class="tree__button__content">
                    <a :href="document.url" target="_blank">{{ document.title }}</a> <!-- NOSONAR -->
                    <span class="tree__list__content__label">{{ document.state }}</span>
                    <!-- {{ content.namespace }} -->
                     <button v-if="document.can_delete" class="tree__button__content__delete" @click="toggleDeleteDocument(document)">
                        <Trash2 color="white"/>
                    </button>
                </div>
            </li>

            <!-- IN UPLOAD DOCS -->
            <div v-for="(file, name) in chatStore.filesToUpload[props.folder.path]?.files">
                <li 
                    :class="'tree__list__content__item tree__list__content__item__loader '  + file.state"
                    v-if="file.state == 'progress' || file.state == 'error'"
                    >
                    <p :class="'tree__button__content ' + file.state">
                        {{name}}
                        <Loader v-if="file.state == 'progress'" color="white"/>
                        <ShieldAlert title="delete" @click="removeDocumentToFilesToUpload(name)" v-if="file.state == 'error'"/>
                        <span class="tree__list__content__label">{{ file.state }}</span>
                    </p>
                </li>
            </div>

            <button class="tree__list__content__loadmore" v-if="page * 10 < folder.document_count" @click="nextPage">
                <Ellipsis color="white"/>
            </button>

        </ul>

    </div>

    <!-- POPIN DELETE FOLDER -->
    <div class="subpopin" v-if="popinDeleteFolder">
        <div class="subpopin__content">
            <div class="subpopin__content__title">
                <span>{{ $t('delete') }} {{ $t('folder') }} [{{ folder.name }}]</span>
            </div>

            <div class="subpopin__content__text">
                <span>{{  $t('delete_msg') }} {{ $t('all_plural') }} {{ $t('folder_plural') }} {{ $t('and') }} {{ $t('file_plural') }} {{ $t('child_plural') }}</span>
            </div>

            <div class="subpopin__content__buttons" >
                <button class="back" @click="toggleDeleteFolder">
                    <span>{{ $t('back') }}</span>
                </button>
                <button class="delete" @click="deleteFolder">
                    <span>{{ $t('delete') }}</span>
                </button>
            </div>
        </div>
    </div> 

    <!-- POPIN DELETE FILE -->
    <div class="subpopin" v-if="popinDeleteDocument">
        <div class="subpopin__content">
            <div class="subpopin__content__title">
                <span>{{ $t('delete') }} [{{ currentDeleteDocument }}]</span>
            </div>

            <div class="subpopin__content__text">
                <span>{{  $t('delete_msg') }} ce document.</span>
            </div>

            <div class="subpopin__content__buttons" >
                <button class="back" @click="toggleDeleteDocument(null)">
                    <span>{{ $t('back') }}</span>
                </button>
                <button class="delete" @click="deleteDocument">
                    <span>{{ $t('delete') }}</span>
                </button>
            </div>
        </div>
    </div> 

</template>