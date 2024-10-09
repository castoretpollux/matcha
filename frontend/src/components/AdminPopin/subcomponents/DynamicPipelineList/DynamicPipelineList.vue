<script setup>
import { ref, onMounted, defineEmits } from 'vue';

import FactoryForm from "@/components/AdminPopin/subcomponents/FactoryForm/FactoryForm.vue"

import { useChatStore } from "@/stores/chat";
import FactoryManager from "@/helpers/factoryManager.js"

import { Trash2, Power, Pen } from "lucide-vue-next";
import { useI18n } from "vue-i18n";
const { t } = useI18n();

const chatStore = useChatStore()
const factoryManager = new FactoryManager()

const dynamicPipelines = ref([])
const emits = defineEmits(['updateInfo'])

const confirm = ref({})
const deletePopinOpen = ref(false)

const showFactoryForm = ref(false)
const editMode = ref(false)
const pipelineToEdit = ref({})

onMounted(() => {
    updateDynamicPipelines()
    dynamicPipelines.value.forEach((pipeline) => {
        confirm.value[pipeline.alias] = false
    })
})

const updateDynamicPipelines = () => {
    dynamicPipelines.value = []
    chatStore.pipelines.forEach(pipeline => {
        if (pipeline.alias.startsWith('dynamic')) {
            dynamicPipelines.value.push(pipeline)
        }
    });
}

const back = () => {
    editMode.value = false
    pipelineToEdit.value = {}
    showFactoryForm.value = false
}

const addNewPipeline = () => {
    editMode.value = false
    pipelineToEdit.value = {}
    showFactoryForm.value = true
}

const editPipeline = (pipeline) => {
    editMode.value = true
    pipelineToEdit.value = pipeline
    showFactoryForm.value = true
}

const updateInfo = () => {
    updateDynamicPipelines()
    emits('updateInfo', `${t('the')} ${t('pipeline')} ${t('has_been')} ${t('added')}`);
}

const toggleDynamicPipeline = (pipeline_alias) => {
    deletePopinOpen.value = !deletePopinOpen.value

    const active = !confirm.value[pipeline_alias]
    confirm.value = {}
    confirm.value[pipeline_alias] = active
}

const deleteDynamicPipeline = (pipeline_alias) => {
    factoryManager.deleteDynamicPipeline(pipeline_alias)
    .then(() => {
        dynamicPipelines.value = []
        emits('updateInfo', `${t('the')} ${t('pipeline')} [${pipeline_alias}] ${t('has_been')} ${t('deleted')}`);
        updateDynamicPipelines()
        deletePopinOpen.value = false
    })
}

const toggleActiveDynamicPipeline = (pipeline) => {
    if (pipeline.ready) {
        let status_word = t('activated')
        if (pipeline.active) status_word = t('desactivated')
        
        const status = !pipeline.active
        factoryManager.toogleActiveDynamicPipeline(pipeline.alias, status)
        .then(() => {
            dynamicPipelines.value = []
            emits('updateInfo', `${t('the')} ${t('pipeline')} [${pipeline.label}] ${t('has_been')} ${status_word}`);
            updateDynamicPipelines()
        })
    }
}

</script>

<template>

    <!-- DYNAMIQUE PIPELINE LIST -->
    <div class="dynamicpipelinelist" v-if="dynamicPipelines.length && !showFactoryForm">

        <div class="dynamicpipelinelist__grid-container header">
            <div class="dynamicpipelinelist__grid-item grid-header">{{ $t('label') }}</div>
            <div class="dynamicpipelinelist__grid-item grid-header">{{ $t('description') }}</div>
            <div class="dynamicpipelinelist__grid-item grid-header">{{ 'status' }}</div>
            <div class="dynamicpipelinelist__grid-item grid-header">actions</div>
        </div>

        <div class="dynamicpipelinelist__grid-container body" v-for="dynamicPipeline in dynamicPipelines">
            <div class="dynamicpipelinelist__grid-item">{{ dynamicPipeline.label }}</div>
            <div class="dynamicpipelinelist__grid-item">{{ dynamicPipeline.description }}</div>
            <div class="dynamicpipelinelist__grid-item status">
                <p>Ready <span :class="dynamicPipeline.ready ? 'active' : ''"></span></p>
                <p>Active <span :class="dynamicPipeline.active ? 'active' : ''"></span></p>
            </div>
            <div class="dynamicpipelinelist__grid-item">
                <button 
                    class="dynamicpipelinelist__grid-item__button"
                    @click="editPipeline(dynamicPipeline)"
                    :disabled="!dynamicPipeline.editable"
                >
                    <Pen color="white"/>
                </button>

                <button 
                    :class="[
                        'dynamicpipelinelist__grid-item__button active',
                        dynamicPipeline.ready ? '' : 'disabled'
                    ]"
                    @click="toggleActiveDynamicPipeline(dynamicPipeline)"
                >
                    <Power color="white" :class="dynamicPipeline.active ? 'active' : ''"/>
                </button>

                <button
                    :class="[
                        'dynamicpipelinelist__grid-item__button delete',
                        dynamicPipeline.ready ? '' : 'disabled'
                    ]"
                    @click="toggleDynamicPipeline(dynamicPipeline.alias)"
                >
                    <Trash2 color="red"/>
                </button>
            </div>
        </div>
    </div>

    <!-- ADD PIPELINE IF LIST -->
    <button class="dynamicpipelinelist__add" @click="addNewPipeline" v-if="dynamicPipelines.length && !showFactoryForm">
        {{ $t('add_one') }} {{ $t('new') }} pipeline
    </button>

    <!-- MESSAGE AND ADD PIPELINE IF EMPTY LIST -->
    <div class="dynamicpipelinelist__message" v-if="!dynamicPipelines.length && !showFactoryForm">
        <img src="@/assets/img/aisystem.webp" alt="AI System">
        <h2 class="dynamicpipelinelist__message__text">
            {{ $t('dynamicpipelinelist_message_text_1_1') }}
            <button @click="addNewPipeline" class="dynamicpipelinelist__message__button">{{ $t('here') }}</button>
            {{ $t('dynamicpipelinelist_message_text_1_2') }}
        </h2>
    </div>

    <!-- FACTORY PIPELINE FORM -->
    <FactoryForm v-if="showFactoryForm" @back="back" @updateInfo="updateInfo" :editMode="editMode" :pipeline="pipelineToEdit"/>

    <!-- POPIN DELETE -->
    <div class="dynamicpipelinelist__confirm-deletion" v-show="deletePopinOpen">
        <div 
            v-for="dynamicPipeline in dynamicPipelines"
            :key="dynamicPipeline" 
            class="dynamicpipelinelist__confirm-deletion__content"
            v-show="confirm[dynamicPipeline.alias]"
            >
            <div class="dynamicpipelinelist__confirm-deletion__content__title">
                <span>{{  $t('delete') }} {{ $t('this') }} {{  $t('prompt') }} ?</span>
            </div>
            <div class="dynamicpipelinelist__confirm-deletion__content__text">
                <span>{{  $t('delete_msg') }} "{{ dynamicPipeline.label }}"</span>
            </div>
            <div class="dynamicpipelinelist__confirm-deletion__content__buttons" >
                <button class="back" @click="toggleDynamicPipeline(dynamicPipeline.alias)">
                    <span>{{ $t('back') }}</span>
                </button>
                <button class="delete" @click="deleteDynamicPipeline(dynamicPipeline.alias)">
                    <span>{{ $t('delete') }}</span>
                </button>
            </div>
        </div>
    </div>

</template>

<style lang="scss">@import "./dynamicpipelinelist.scss";</style>
