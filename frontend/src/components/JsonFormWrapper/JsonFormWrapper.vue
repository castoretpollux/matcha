<script setup>
import { ref, onMounted, onUnmounted, defineEmits } from 'vue';

import { isEmpty, formatValue } from '@/helpers/utils';
import { getSchemaProperties, checkRequiredFields, getSchemaRules, checkSchemaRules, getInitialData } from './jsonformwrapper';

import { JsonForms } from '@jsonforms/vue';
import { castorRenderers } from '@/components/vue-castor';
import '@/components/vue-castor/castor.renderers.css';
import { uuid } from 'vue-uuid';


const schemaIsSet = ref(false)

// ### JSON FORMS
let renderers = [...castorRenderers];
renderers = Object.freeze(renderers)

const emits = defineEmits(['updateData', 'formIsValid'])
const props = defineProps({
    schema: {
        type: Object,
        required: true
    },
    uischema: {
        type: Object,
        required: true
    },
    editMode: {
        type: Boolean,
        default: false,
        required: false
    }
})

// INIT DATA METHODS
let initialData = {}
let dataToSend = {}
let data = {}
let rules = {}
let properties = {}
let jsonFormId = null
let isValid = false

const initData = () => {
    jsonFormId = 'json-form-wrapper-' + uuid.v4()

    initialData = getInitialData(props.schema)

    properties = getSchemaProperties(props.schema)
    rules = getSchemaRules(props.uischema)

    data = initialData
    dataToSend = initialData

    props.schema['editMode'] = props.editMode
}

// On Input
const onInput = (e) => {
    const key = e.target.id.replace('#/properties/', '')
    if (dataToSend[key] != undefined) {
        dataToSend[key] = formatValue(e.target.value)

        const checkRules = checkSchemaRules(rules, properties, dataToSend, jsonFormId)
        properties = checkRules[0]
        dataToSend = checkRules[1]

        isValid = checkRequiredFields(properties, dataToSend)

        emits('formIsValid', isValid)
        emits('updateData', dataToSend)
    }
}

// ON CHANGE METHODS
const onChange = (e) => {
    if (e.data && !isEmpty(e.data)) {       
        for (const [key] of Object.entries(dataToSend)) {
            let newValue = formatValue(e.data[key])
            if (newValue != undefined) {
                if (typeof newValue == 'object') {
                    newValue = [...newValue];
                }
                dataToSend[key] = newValue
            }
        }

        const checkRules = checkSchemaRules(rules, properties, dataToSend, jsonFormId)
        properties = checkRules[0]
        dataToSend = checkRules[1]

        isValid = checkRequiredFields(properties, dataToSend)

        emits('formIsValid', isValid)
        emits('updateData', dataToSend)
    }
}

const resetFactoryForm = () => {
    data = {}
    rules = {}
    isValid = false
    initialData = {}
    dataToSend = {}
    properties = {}
    jsonFormId = null
    schemaIsSet.value = false
}

onMounted(() => {
    initData()
    schemaIsSet.value = true
})

onUnmounted(() => {
    resetFactoryForm()
})

</script>

<template>
    <div class="json-form-wrapper" :id="jsonFormId">
        <json-forms 
            v-if="schema && schemaIsSet"
            :renderers="renderers"
            :data="data"
            :schema="schema"
            :uischema="uischema"
            @change="onChange"
            @input="onInput"/>
    </div>
</template>

