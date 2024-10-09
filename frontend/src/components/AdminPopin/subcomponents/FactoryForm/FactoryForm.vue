<script setup>
    import { ref, onMounted, onUnmounted, defineEmits } from 'vue';

    import { useAdminStore } from "@/stores/admin";

    import FactoryManager from '@/helpers/factoryManager.js';
    import JsonFormWrapper from '@/components/JsonFormWrapper/JsonFormWrapper.vue'
    import { isEmpty } from '@/helpers/utils';

    const adminStore = useAdminStore();

    const factory = new FactoryManager();

    let schema = {}
    let uischema = {}

    let factoryschema = {}
    let factoryuischema = {}

    const emits = defineEmits(['updateInfo', 'back'])
    const props = defineProps({
        editMode: {
            type: Boolean,
            default: false,
            required: false
        },
        pipeline: {
            type: Object,
            default: {},
            required: false
        }
    })

    // INIT DATA METHODS
    let dataToSend = {}
    const initDataTosend = () => {
        dataToSend = {common: {}, factory: {}}
    }

    // GET LIST OF FACTORIES
    const getFactoryList = () => {
        factory.getFactoryList()
    }

    // GET COMMON FACTORY SCHEMES
    const commonInitialized = ref(false)
    const getFactoryCommonSchemes = () => {
        if (isEmpty(adminStore.BaseModelSchema)) {
            factory.getFactoryCommonSchemes()
            .then(() => {
                schema = JSON.parse(JSON.stringify(adminStore.BaseModelSchema));
                uischema = JSON.parse(JSON.stringify(adminStore.BaseModelUiSchema));
            })
        } else {
            schema = JSON.parse(JSON.stringify(adminStore.BaseModelSchema));
            uischema = JSON.parse(JSON.stringify(adminStore.BaseModelUiSchema));
        }
    }

    // GET FACTORY SCHEMES
    let factoryNote = null
    const factoryInitialized = ref(false)
    const selectFactory = (selected_factory) => {
        factory.getFactorySchemes(selected_factory)
        .then(() => {
            factoryschema = adminStore.FactoryModelSchema
            factoryuischema = adminStore.FactoryModelUiSchema
            if (factoryuischema.note) factoryNote = factoryuischema.note
            factoryInitialized.value = true
            commonInitialized.value = true
        })
    }

    // SEND REQUEST
    async function addNewPipeline() {
        if (formIsValid.common && formIsValid.factory) {
            dataToSend['factory_name'] = adminStore.currentFactory.key
            dataToSend.factory['editable'] = factoryuischema.editable
            factory.createDynamicPipeline(dataToSend)
            .then(() => {
                emits('updateInfo', null);
                back()
            })
        }
    }

    async function updatePipeline() {
        const newDataToSend = {}
        for (const [key, value] of Object.entries(uischema.editable_elements)) {
            if (value) {
                newDataToSend[key] = dataToSend.common[key]
            }
        }
        for (const [key, value] of Object.entries(factoryuischema.editable_elements)) {
            if (value) {
                newDataToSend[key] = dataToSend.factory[key]
            }
        }

        const data = {
            params: newDataToSend,
            alias: props.pipeline.alias,
        }

        factory.updateDynamicPipelineParams(data)
        .then(() => {
            back()
        })
    }

    // EVENTS
    const back = () => {
        resetFactoryForm()
        emits('back', null)
    }

    const updateData = (datas) => {
        dataToSend.common = datas
    }

    const updateFactoryData = (datas) => {
        dataToSend.factory = datas
    }

    const formIsValid = {common: false, factory: false}
    const commonFormValid = (state) => {
        formIsValid.common = state
        checkFormValidity()
    }

    const factoryFormValid = (state) => {
        formIsValid.factory = state
        checkFormValidity()
    }
        
    const submitButton = ref(null)
    const checkFormValidity = () => {
        if (formIsValid.common && formIsValid.factory) {
            submitButton?.value?.removeAttribute('disabled')
        } else {
            submitButton?.value?.setAttribute('disabled', true)
        }
    }

    // RESET METHOD
    const resetFactoryForm = () => {
        initDataTosend()

        commonInitialized.value = false
        factoryInitialized.value = false
        
        adminStore.FactoryModelSchema = {}
        adminStore.FactoryModelUiSchema = {}
        adminStore.currentFactory = null

        factoryschema = {}
        factoryuischema = {}

        formIsValid.common = false
        formIsValid.factory = false

        factoryNote = null
    }

    const initEditPipeline = () => {
        factory.getFactorySchemes({key: props.pipeline.factory})
        .then(() => {
            factoryschema = adminStore.FactoryModelSchema
            factoryuischema = adminStore.FactoryModelUiSchema
            if (factoryuischema.note) factoryNote = factoryuischema.note
            if (props.pipeline.editable) {
                factory.getDynamicPipeline(props.pipeline.alias).then((data) => {
                    const params = data.pipeline.params
                    for (const [key] of Object.entries(schema.properties)) {
                        if (props.pipeline[key]) {
                            schema.properties[key].extra.default = props.pipeline[key]
                        }
                        if (params[key]) {
                            schema.properties[key].extra.default = params[key]
                        }
                    }
                    for (const [key] of Object.entries(factoryschema.properties)) {
                        if (props.pipeline[key]) {
                            factoryschema.properties[key].extra.default = props.pipeline[key]
                        }
                        if (params[key]) {
                            factoryschema.properties[key].extra.default = params[key]
                        }
                    }
                    factoryInitialized.value = true
                    commonInitialized.value = true
                    adminStore.currentFactory = {key: props.pipeline.factory}
                })
            } else {
                back()
            }
        });
    }

    // MOUNTED/UNMOUNTED
    onMounted(() => {
        initDataTosend()
        getFactoryCommonSchemes()

        if (!adminStore.factoryList.length) getFactoryList()

        if (props.editMode) {
            initEditPipeline()
        }
    })

    onUnmounted(() => {
        resetFactoryForm()
    })

</script>

<template>
    <div class="factoryform">
        <div class="factoryform__factories" v-if="!adminStore.currentFactory">
            <p class="factoryform__factories__title">{{ $t('create_one') }} pipeline</p>
            <button
            v-for="factoryItem in adminStore.factoryList"
            class="factoryform__button"
            @click="selectFactory(factoryItem)"
            >
                {{ factoryItem.label }}
            </button>
        </div>

        <div v-if="adminStore.currentFactory" class="factoryform__form">
            <p class="factoryform__form__title">{{ adminStore.currentFactory.label }} Factory</p>
            <p v-if="factoryNote" class="factoryform__form__legend">{{ factoryNote }}</p>

            <json-form-wrapper v-if="factoryInitialized && factoryschema" :schema="factoryschema" :uischema="factoryuischema" @updateData="updateFactoryData" @formIsValid="factoryFormValid" :editMode="editMode"/>
            <json-form-wrapper v-if="commonInitialized && schema" :schema="schema" :uischema="uischema" @updateData="updateData" @formIsValid="commonFormValid" :editMode="editMode"/>

            <div class="factoryform__buttons">
                <button @click="back" class="factoryform__buttons__reset">{{ $t('back') }}</button>
                <button v-if="!editMode" @click="addNewPipeline" ref="submitButton" class="factoryform__buttons__submit" disabled>{{ $t('add') }}</button>
                <button v-if="editMode" @click="updatePipeline" ref="submitButton" class="factoryform__buttons__submit" disabled>{{ $t('save') }}</button>
            </div>
        </div>
        <button class="factoryform__form__back" @click="back" v-if="!adminStore.currentFactory">
            {{ $t('back') }}
        </button>
    </div>


</template>

<style lang="scss">@import "./factoryform.scss";</style>
