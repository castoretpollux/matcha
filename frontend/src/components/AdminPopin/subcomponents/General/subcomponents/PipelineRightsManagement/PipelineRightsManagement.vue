<script setup>
    import { ref, onMounted } from 'vue';
    
    import { useChatStore } from '@/stores/chat'
    import { useUserStore } from "@/stores/user";
    import { SessionStore } from "@/stores/session";

    import { deepEqualArray } from '@/helpers/utils.js'
    
    import { Eye, SquarePlus, SquarePen, Trash2 } from 'lucide-vue-next';
    
    const emits = defineEmits(['updateInfo', 'back'])
    
    const chatStore = new useChatStore()
    const userStore = useUserStore() 
    const session = SessionStore()

    const dynamicPipelines = ref([])
    const dynamicPipelinesTest = ref([])
    const rightsChanged = ref(false)

    // EVENTS
    const back = () => {
        emits('back', null)
    }

    const changePipelineRights = (index, type, crud, value) => {
        dynamicPipelines.value[index][type][crud] = value
        checkRigths()
    }

    const groupChange = (e, index) => {
        let group = e.target.value
        if (group == 'null') group = null
        dynamicPipelines.value[index].group = group
        checkRigths()
    }

    const userChange = (e, index) => {
        let user = e.target.value
        if (user == 'null') user = null
        dynamicPipelines.value[index].user = user
        checkRigths()
    }

    const checkRigths = () => {
        if (deepEqualArray(dynamicPipelines.value, dynamicPipelinesTest.value)) rightsChanged.value = false
        else rightsChanged.value = true
    }

    // SAVE CHANGEMENTS
    const save = () => {
        const saveList = []

        for (let pipeline of dynamicPipelines.value) {
            saveList.push({
                alias: pipeline.alias,
                group_id: pipeline.group,
                user_id: pipeline.user,
                other_rights: pipeline.other_rights,
                group_rights: pipeline.group_rights,
                user_rights: pipeline.user_rights,
            })
        }

        session.updateDynamicPipeline({pipelines: saveList})
        rightsChanged.value = false
    }

    onMounted(() => {
        dynamicPipelines.value = []
        chatStore.pipelines.forEach(pipeline => {
            if (pipeline.alias.startsWith('dynamic')) {
                dynamicPipelines.value.push(pipeline)
            }
        });
        dynamicPipelinesTest.value = JSON.parse(JSON.stringify(dynamicPipelines.value));
    })

</script>

<template>
    <AdminLoader ref="loader"/>
    
    <button @click="save" class="rights__save" v-if="rightsChanged">{{ $t('save') }}</button>
    
    <div class="rights">
        <h1>{{ $t('manage') }} {{ $t('pipeline_plural') }} {{ $t('rights') }}</h1>
    </div>

    <div class="rights__management">
        <table class="rights__management__table" v-for="(pipeline, index) in dynamicPipelines" aria-label="Rights Management Table">

            <tr>
                <th>{{ $t('pipeline') }}</th>
                <th>{{ $t('user') }} {{ $t('owner') }}</th>
                <th>{{ $t('group') }} {{ $t('owner') }}</th>
                <th>{{ $t('user_rights') }}</th>
                <th>{{ $t('group_rights') }}</th>
                <th>{{ $t('other_rights') }}</th>
            </tr>

            <tr>
                <td>{{pipeline.label}}</td>
                
                <td>
                    <select class="rights__management__table__select" @change="userChange($event, index)">
                        <option :selected="!pipeline.user" value="">null</option>
                        <option v-for="user in userStore.users" :value="user[0]" :selected="user[0] == pipeline.user">{{ user[1] }}</option>
                    </select>
                </td>
                <td>
                    <select class="rights__management__table__select" @change="groupChange($event, index)">
                        <option :selected="!pipeline.group" :value="null">null</option>
                        <option v-for="group in userStore.groups" :value="group[0]" :selected="group[0] == pipeline.group">{{ group[1] }}</option>
                    </select>
                </td>
                

                <td>
                    <button title="user can create" @click="changePipelineRights(index, 'user_rights', 'can_write', !pipeline.user_rights?.can_write)">
                        <SquarePlus :color="pipeline.user_rights?.can_write ? 'green' : 'red'"/>
                    </button>
                    <button title="user can read" @click="changePipelineRights(index, 'user_rights', 'can_read', !pipeline.user_rights?.can_read)">
                        <Eye :color="pipeline.user_rights?.can_read ? 'green' : 'red'"/>
                    </button>
                    <button title="user can update" @click="changePipelineRights(index, 'user_rights', 'can_update', !pipeline.user_rights?.can_update)">
                        <SquarePen :color="pipeline.user_rights?.can_update ? 'green' : 'red'"/>
                    </button>
                    <button title="user can delete" @click="changePipelineRights(index, 'user_rights', 'can_delete', !pipeline.user_rights?.can_delete)">
                        <Trash2 :color="pipeline.user_rights?.can_delete ? 'green' : 'red'"/>
                    </button>
                </td>
                <td>
                    <button title="group can write" @click="changePipelineRights(index, 'group_rights', 'can_write', !pipeline.group_rights?.can_write)">
                        <SquarePlus :color="pipeline.group_rights?.can_write ? 'green' : 'red'"/>
                    </button>
                    <button title="group can read" @click="changePipelineRights(index, 'group_rights', 'can_read', !pipeline.group_rights?.can_read)">
                        <Eye :color="pipeline.group_rights?.can_read ? 'green' : 'red'"/>
                    </button>
                    <button title="group can update" @click="changePipelineRights(index, 'group_rights', 'can_update', !pipeline.group_rights?.can_update)">
                        <SquarePen :color="pipeline.group_rights?.can_update ? 'green' : 'red'"/>
                    </button>
                    <button title="group can delete" @click="changePipelineRights(index, 'group_rights', 'can_delete', !pipeline.group_rights?.can_delete)">
                        <Trash2 :color="pipeline.group_rights?.can_delete ? 'green' : 'red'"/>
                    </button>
                </td>
                <td>
                    <button title="other can create" @click="changePipelineRights(index, 'other_rights', 'can_write', !pipeline.other_rights?.can_write)">
                        <SquarePlus :color="pipeline.other_rights?.can_write ? 'green' : 'red'"/>
                    </button>
                    <button title="other can read" @click="changePipelineRights(index, 'other_rights', 'can_read', !pipeline.other_rights?.can_read)">
                        <Eye :color="pipeline.other_rights?.can_read ? 'green' : 'red'"/>
                    </button>
                    <button title="other can update" @click="changePipelineRights(index, 'other_rights', 'can_update', !pipeline.other_rights?.can_update)">
                        <SquarePen :color="pipeline.other_rights?.can_update ? 'green' : 'red'"/>
                    </button>
                    <button title="other can delete" @click="changePipelineRights(index, 'other_rights', 'can_delete', !pipeline.other_rights?.can_delete)">
                        <Trash2 :color="pipeline.other_rights?.can_delete ? 'green' : 'red'"/>
                    </button>
                </td>
            </tr>
        </table>


        <button class="factoryform__form__back" @click="backToManage">
                {{ $t('back') }}
        </button>
    </div>

    <button class="factoryform__form__back" @click="back" v-if="!folderSelected">
            {{ $t('back') }}
    </button>

</template>


<style lang="scss">@import "./rightsmanagement.scss";</style>