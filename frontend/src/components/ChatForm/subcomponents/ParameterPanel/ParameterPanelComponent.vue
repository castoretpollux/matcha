<script setup>
    import { defineProps, defineEmits, defineExpose, ref, watch } from 'vue';
    import JsonFormWrapper from '@/components/JsonFormWrapper/JsonFormWrapper.vue';

    import { useChatStore } from "@/stores/chat";
    import { SessionStore } from "@/stores/session";
    import { isEmpty } from '@/helpers/utils.js';

    const chatStore = useChatStore()
    const session = SessionStore();

    const emits = defineEmits(['updateData'])
    const active = ref(false)

    const props = defineProps({
        dataToSend: {
            type: Object,
            required: true,
        }
    })

    let dataToSend = props.dataToSend
    watch(() => props.dataToSend, () => {
        dataToSend = props.dataToSend
    })

    // ### WATCHERS
    let schema = {}
    let uischema = {}
    const formInitialized = ref(false)

    const currentChat = ref(session.getChat())

    // WATCH CURRENT CHAT ID
    watch(() => chatStore.currentChatId, () => {
        dataToSend = {}
        chatStore.hasParameters = false
        currentChat.value = session.getChat()
    }, { deep: true });


    // WATCH CURRENT CHAT PIPELINE
    watch(() => currentChat.value.pipeline_schema, () => {
        formInitialized.value = false;
        currentChat.value = session.getChat();

        if (isEmpty(currentChat.value.pipeline_schema)) return;

        const { properties } = currentChat.value.pipeline_schema;

        chatStore.hasFiles = !!properties.files;
        chatStore.hasParameters = false;

        if (chatStore.hasFiles) delete properties.files;

        schema = currentChat.value.pipeline_schema;
        uischema = currentChat.value.pipeline_uischema;

        const schemaCopy = {...schema.properties};
        if (schemaCopy['prompt']) delete schemaCopy['prompt']
        if (Object.keys(schemaCopy).length >= 1) {
            chatStore.hasParameters = true;
        }

        formInitialized.value = true;
        setTimeout(checkMediaFields, 500);
    });

    // WATCH CURRENT CHAT FILES
    watch(() => currentChat.value.files, () => {
        checkMediaFields()
    })
    // ### END WATCHERS

    // ### CHECK MEDIA FIELDS
    const checkMediaFields = () => {
        const input_type = currentChat.value.pipeline_type.split('->')[0].trim()
        if (['image', 'text/image', 'file', 'text/file'].includes(input_type)) {
            chatStore.onlyFileAllowed = true
        } else {
            chatStore.onlyFileAllowed = false
        }

        // Check media fields
        if (currentChat.value.files?.length) {
            if (schema.properties) {
                const media_fields = Object.entries(schema.properties)
                    .filter(([_key, value]) => value.extra.has_media === true)
                    .map(([key, _value]) => key);
        
                console.log(media_fields)

                const options = []
                currentChat.value.files.forEach((file) => {
                    options.push({"value": file.id, "text": file.name})
                })
    
                media_fields.forEach((media_field_name) => {
                    const media_field_id = `#/properties/${media_field_name}`
                    const media_field_element = document.getElementById(media_field_id)
                    options.forEach(optionData => {
                        const option = document.createElement('option');
                        option.value = optionData.value
                        option.textContent = optionData.text
                        media_field_element.add(option);
                    });
                })
            }
        }
    }

    // # DETECT WHEN FIELD CHANGE
    const updateData = (datas) => {
        dataToSend = datas
        emits('updateData', dataToSend)
    }

    const formIsValid = (state) => {
        chatStore.formIsValid = state
    }

    const display = (state) => {
        switch (state) {
            case 'toggle':
                active.value = !active.value
                break;
            case 'close':
                active.value = false
                break;
            case 'open':
                active.value = true
                break;
        }
    }

    defineExpose({
        display,
        // checkMediaFields
    })

</script>

<template>
    <div class="chatform__subprompt" v-show="formInitialized && active">
        <json-form-wrapper v-if="formInitialized && schema" :schema="schema" :uischema="uischema" @updateData="updateData" @formIsValid="formIsValid"/>
    </div>
</template>