<script setup>
    import { ref, onMounted } from 'vue';
    import { useChatStore } from '@/stores/chat'

    import AdminLoader from '@/components/AdminPopin/subcomponents/AdminLoader/AdminLoader.vue'
    import RightTreeItem from '@/components/AdminPopin/subcomponents/General/subcomponents/RightTreeItem/RightTreeItem.vue'

    import FolderManager from '@/helpers/folderManager.js'
    import { isEmpty, deepEqualObj, deepEqualArray } from '@/helpers/utils.js'

    import { Eye, SquarePlus, SquarePen, Trash2, ChevronRight, ChevronLeft } from 'lucide-vue-next';

    const emits = defineEmits(['updateInfo', 'back'])

    const folderManager = new FolderManager()
    const chatStore = new useChatStore()

    const applyToAll = defineModel('applyToAll')
    applyToAll.value = false

    const loader = ref(null)
    const loading = ref(true)

    const folderSelected = ref(null)
    const folderDocuments = ref({})
    const rightsChanged = ref(false)
    const currentFolder = ref(null)

    const page = ref(1)
    const pageCount = ref(0)

    // EVENTS
    const back = () => {
        emits('back', null)
    }
    const backToManage = () => {
        folderSelected.value = null
        folderDocuments.value = {}
        rightsChanged.value = false
        currentFolder.value = null
        page.value = 1
        pageCount.value = 0
    }

    // FOLDER PICKER
    const selectFolder = (folderPath) => {
        // SET ROOT CURRENT FOLDER
        currentFolder.value = JSON.parse(JSON.stringify(chatStore.folders[0]));
        
        // SPLIT PATH AND REMOVE FIRST PATH (ROOT)
        const folderPathSplited = folderPath.split('/')
        folderPathSplited.shift()

        // FIND SUBFOLDER
        for (let childName of folderPathSplited) {
            const child = currentFolder.value.children.find(item => item.name == childName);
            if (child) {
                currentFolder.value = child
            }
        }

        // SET
        folderSelected.value = JSON.parse(JSON.stringify(currentFolder.value));
        if (currentFolder.value.documents.length) {
            pageCount.value = Math.ceil(currentFolder.value.document_count / currentFolder.value.documents.length)
            folderDocuments.value[`page${page.value}`] = JSON.parse(JSON.stringify(currentFolder.value.documents.slice(0, 10)));
        } else {
            page.value = 0
        }
    }

    // CHANGE FOLDER RIGHTS METHOD
    const changeFolderRights = (type, crud, value) => {
        folderSelected.value[type][crud] = value
        if (deepEqualObj(currentFolder.value, folderSelected.value)) rightsChanged.value = false
        else rightsChanged.value = true
    }

    // CHANGE DOCUMENT RIGHTS METHOD
    const changeDocumentRights = (index, _uid, type, crud, value) => {
        if (applyToAll.value) {
            for (const document of folderDocuments.value[`page${page.value}`]) {
                document[type][crud] = value
            }
        } else {
            folderDocuments.value[`page${page.value}`][index][type][crud] = value
        }

        const listTest = []
        for (const [, document_value] of Object.entries(folderDocuments.value)) {
            listTest.push(...document_value)
        }

        if (deepEqualArray(currentFolder.value.documents, listTest)) rightsChanged.value = false
        else rightsChanged.value = true
    }


    // DOCUMENT PAGINATION
    const nextPage = (path) => {
        page.value++;
        if (!folderDocuments.value[`page${page.value}`]) {
            const data = {
                path: path,
                page: page.value
            }
            folderManager.getDocumentsPage(data)
            .then(_data => {
                folderDocuments.value[`page${page.value}`] = JSON.parse(JSON.stringify([..._data.results]))
                currentFolder.value.documents.push(..._data.results)
            })
        }
    }
    const prevPage = () => {
        page.value--;
    }

    // SAVE CHANGEMENTS
    const save = () => {
        // CREATE DOCUMENT LIST
        const documentList = []
        for (const [, value] of Object.entries(folderDocuments.value)) {
            const pagePocumentList = [...value]
            for (let document of pagePocumentList) {
                documentList.push({
                    id:             document.id,
                    other_rights:   document.other_rights,
                    group_rights:   document.group_rights,
                    user_rights:    document.user_rights,
                })
            }
        }
        // CREATE FOLDER DICT
        const folderDict = {
            id:             folderSelected.value.id,
            other_rights:   folderSelected.value.other_rights,
            group_rights:   folderSelected.value.group_rights,
            user_rights:    folderSelected.value.user_rights,
        }

        // CREATE DATA TO SEND
        const data = {
            folder: folderDict,
            documents: documentList
        }

        // POST
        folderManager.updateRights(data)
        .then(() => {
            folderManager.getFolders()
            .then(function(result) {
                chatStore.folders = result.folders
                backToManage()
            })
        })
    }

    onMounted(() => {
        if (isEmpty(chatStore.folders)) {
            loader.value.load(true)
            loading.value = true
            folderManager.getFolders()
            .then(function(result) {
                chatStore.folders = result.folders
                loader.value.load(false)
                loading.value = false
            });
        } else {
            loading.value = false
        }
    })

</script>

<template>
    <AdminLoader ref="loader"/>
    
    <button @click="save" class="rights__save" v-if="rightsChanged">{{ $t('save') }}</button>
    
    <div class="rights" v-if="!loading">
        <h1>{{ $t('manage') }} {{ $t('rights') }}</h1>
        <div class="rights__tree" v-if="!folderSelected">
            <ul class="tree" v-for="(folder, index) in chatStore.folders">
                <RightTreeItem :folder="{
                    ...folder,
                    path: folder.name,
                    open: true,
                    index: index,
                }"
                @selectFolder="selectFolder"
                />
            </ul>
        </div>
    </div>

    <div class="rights__management" v-if="folderSelected">
        <p class="rights__management__title"><span>{{ folderSelected.full_path }}</span> </p>

        <table class="rights__management__table" aria-label="Right Management Table">
            <tr>
                <th>{{ $t('user') }} {{ $t('owner') }}</th>
                <th>{{ $t('group') }} {{ $t('owner') }}</th>
                <th>{{ $t('user_rights') }}</th>
                <th>{{ $t('group_rights') }}</th>
                <th>{{ $t('other_rights') }}</th>
            </tr>
            <tr>
                <td v-if="folderSelected.user_rights?.name">{{folderSelected.user_rights?.name}}</td>
                <td v-else>null</td>

                <td v-if="folderSelected.group_rights?.name">{{folderSelected.group_rights?.name}}</td>
                <td v-else>null</td>

                <td>
                    <button title="user can create" @click="changeFolderRights('user_rights', 'can_write', !folderSelected.user_rights?.can_write)">
                        <SquarePlus :color="folderSelected.user_rights?.can_write ? 'green' : 'red'"/>
                    </button>
                    <button title="user can read" @click="changeFolderRights('user_rights', 'can_read', !folderSelected.user_rights?.can_read)">
                        <Eye :color="folderSelected.user_rights?.can_read ? 'green' : 'red'"/>
                    </button>
                    <button title="user can update" @click="changeFolderRights('user_rights', 'can_update', !folderSelected.user_rights?.can_update)">
                        <SquarePen :color="folderSelected.user_rights?.can_update ? 'green' : 'red'"/>
                    </button>
                    <button title="user can delete" @click="changeFolderRights('user_rights', 'can_delete', !folderSelected.user_rights?.can_delete)">
                        <Trash2 :color="folderSelected.user_rights?.can_delete ? 'green' : 'red'"/>
                    </button>
                </td>
                <td>
                    <button title="group can write" @click="changeFolderRights('group_rights', 'can_write', !folderSelected.group_rights?.can_write)">
                        <SquarePlus :color="folderSelected.group_rights?.can_write ? 'green' : 'red'"/>
                    </button>
                    <button title="group can read" @click="changeFolderRights('group_rights', 'can_read', !folderSelected.group_rights?.can_read)">
                        <Eye :color="folderSelected.group_rights?.can_read ? 'green' : 'red'"/>
                    </button>
                    <button title="group can update" @click="changeFolderRights('group_rights', 'can_update', !folderSelected.group_rights?.can_update)">
                        <SquarePen :color="folderSelected.group_rights?.can_update ? 'green' : 'red'"/>
                    </button>
                    <button title="group can delete" @click="changeFolderRights('group_rights', 'can_delete', !folderSelected.group_rights?.can_delete)">
                        <Trash2 :color="folderSelected.group_rights?.can_delete ? 'green' : 'red'"/>
                    </button>
                </td>
                <td>
                    <button title="other can create" @click="changeFolderRights('other_rights', 'can_write', !folderSelected.other_rights?.can_write)">
                        <SquarePlus :color="folderSelected.other_rights?.can_write ? 'green' : 'red'"/>
                    </button>
                    <button title="other can read" @click="changeFolderRights('other_rights', 'can_read', !folderSelected.other_rights?.can_read)">
                        <Eye :color="folderSelected.other_rights?.can_read ? 'green' : 'red'"/>
                    </button>
                    <button title="other can update" @click="changeFolderRights('other_rights', 'can_update', !folderSelected.other_rights?.can_update)">
                        <SquarePen :color="folderSelected.other_rights?.can_update ? 'green' : 'red'"/>
                    </button>
                    <button title="other can delete" @click="changeFolderRights('other_rights', 'can_delete', !folderSelected.other_rights?.can_delete)">
                        <Trash2 :color="folderSelected.other_rights?.can_delete ? 'green' : 'red'"/>
                    </button>
                </td>
            </tr>
        </table>

        <div class="rights__management__documents">

            <div class="rights__management__documents__paginate">
                <p>Page {{ page }}/{{ pageCount }}</p>
                <button :disabled="page==1 || page==0" @click="prevPage"><ChevronLeft color="white"/></button>
                <button :disabled="page==pageCount || pageCount==0" @click="nextPage(folderSelected.full_path)"><ChevronRight color="white"/></button>
            </div>
            <table class="rights__management__table" aria-label="Right Management Table">
                <tr class="rights__management__table__documents">
                    <th>
                        <input class="rights__management__table__documents__checkbox" type="checkbox" v-model="applyToAll"/>
                        {{ $t('file') }}
                    </th>
                    <th>{{ $t('user_rights') }}</th>
                    <th>{{ $t('group_rights') }}</th>
                    <th>{{ $t('other_rights') }}</th>
                </tr>
                <tr class="rights__management__table__documents" v-for="(document, index) in folderDocuments[`page${page}`]">
                    <td>{{document.title}}</td>
                    <td>
                        <button title="user can read" @click="changeDocumentRights(index, document.id, 'user_rights', 'can_read', !document.user_rights?.can_read)">
                            <Eye :color="document.user_rights?.can_read ? 'green' : 'red'"/>
                        </button>
                        <button title="user can update" @click="changeDocumentRights(index, document.id, 'user_rights', 'can_update', !document.user_rights?.can_update)">
                            <SquarePen :color="document.user_rights?.can_update ? 'green' : 'red'"/>
                        </button>
                        <button title="user can delete" @click="changeDocumentRights(index, document.id, 'user_rights', 'can_delete', !document.user_rights?.can_delete)">
                            <Trash2 :color="document.user_rights?.can_delete ? 'green' : 'red'"/>
                        </button>
                    </td>

                    <td>
                        <button title="group can read" @click="changeDocumentRights(index, document.id, 'group_rights', 'can_read', !document.group_rights?.can_read)">
                            <Eye :color="document.group_rights?.can_read ? 'green' : 'red'"/>
                        </button>
                        <button title="group can update" @click="changeDocumentRights(index, document.id, 'group_rights', 'can_update', !document.group_rights?.can_update)">
                            <SquarePen :color="document.group_rights?.can_update ? 'green' : 'red'"/>
                        </button>
                        <button title="group can delete" @click="changeDocumentRights(index, document.id, 'group_rights', 'can_delete', !document.group_rights?.can_delete)">
                            <Trash2 :color="document.group_rights?.can_delete ? 'green' : 'red'"/>
                        </button>
                    </td>

                    <td>
                        <button title="other can read" @click="changeDocumentRights(index, document.id, 'other_rights', 'can_read', !document.other_rights?.can_read)">
                            <Eye :color="document.other_rights?.can_read ? 'green' : 'red'"/>
                        </button>
                        <button title="other can update" @click="changeDocumentRights(index, document.id, 'other_rights', 'can_update', !document.other_rights?.can_update)">
                            <SquarePen :color="document.other_rights?.can_update ? 'green' : 'red'"/>
                        </button>
                        <button title="other can delete" @click="changeDocumentRights(index, document.id, 'other_rights', 'can_delete', !document.other_rights?.can_delete)">
                            <Trash2 :color="document.other_rights?.can_delete ? 'green' : 'red'"/>
                        </button>
                    </td>
                </tr>
            </table>
        </div>

        <button class="factoryform__form__back" @click="backToManage">
                {{ $t('back') }}
        </button>
    </div>

    <button class="factoryform__form__back" @click="back" v-if="!folderSelected">
            {{ $t('back') }}
    </button>

</template>


<style lang="scss">@import "./rightsmanagement.scss";</style>