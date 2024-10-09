<script setup>
    import { ref, defineEmits, defineModel, defineExpose, watch } from 'vue';
    import { useChatStore } from "@/stores/chat";
    import { SessionStore } from "@/stores/session";
    import { useI18n } from "vue-i18n";

    const { t } = useI18n();

    const emits = defineEmits(['sendRequest'])
    const chatStore = useChatStore()
    const session = SessionStore()

    const promptIsValid = ref(false)
    const promptInput = ref(null)
    const promptModel = defineModel()

    // watch prompt model to know if its valid to send
    const inTyping = ref(false)
    let timeOutTyping = null
    watch(() => promptModel.value, () => {
        promptIsValid.value = !promptModel.value.startsWith("\n") && promptModel.value.trim() != ''

        if (!promptIsValid.value) {
            chatStore.suggestions = []
        } else if (!chatStore.isRunning) {
            inTyping.value = true
            clearTimeout(timeOutTyping)
            timeOutTyping = setTimeout(() => {
                inTyping.value = false
            }, 500);
        }
    })

    watch(() => inTyping.value, () => {
        if (!inTyping.value) {
            session.getPipelineSuggestions({ 'prompt': promptModel.value })
        }
    })

    // GET SUGGESTIONS ON TYPING
    // const querySuggestion = () => {
    //     if (!promptIsValid.value) {
    //         chatStore.suggestions = []
    //     } else if (!inTyping.value && !chatStore.isRunning) {
    //         inTyping.value = true
    //         session.getPipelineSuggestions({ 'prompt': promptModel.value })
    //         .then(() => {
    //             inTyping.value = false
    //         })
    //     }
    // }

    // Set the height of the prompt
    const setPromptHeight = () => {
        promptInput.value.style.height = 'auto';

        if (promptIsValid.value) {
            if(promptInput.value.scrollHeight < 100) {
                promptInput.value.style.height = promptInput.value.scrollHeight + 'px'
                promptInput.value.style.overflowY = 'hidden';
            } else {
                promptInput.value.style.height = '100px'
                promptInput.value.style.overflowY = 'scroll';
            }
        } else {
            promptModel.value = promptModel.value?.replace("\n", "").replace(' ', '') || ''
        }
    }

    const focusPrompt = () => {
        promptInput.value.focus()
    }

    const sendRequest = () => {
        emits('sendRequest', null)
    }

    defineExpose({
        setPromptHeight,
        focusPrompt
    })

</script>

<template>
    <textarea rows="1" @keyup="setPromptHeight" @keyup.enter.exact.prevent="sendRequest" v-model="promptModel" ref="promptInput"
        :placeholder="t('grap') + ' ' + t('your') + ' ' + t('prompt')"></textarea>
</template>
