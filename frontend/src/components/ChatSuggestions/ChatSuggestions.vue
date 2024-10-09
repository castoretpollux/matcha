<script setup>
import { useChatStore } from "@/stores/chat";
import ChatManager from "@/helpers/chatManager.js";
import { defineProps, defineExpose, defineEmits } from 'vue';
import { Settings } from 'lucide-vue-next';


const chatManager = new ChatManager();
const chatbox = new ChatBox();

const chatStore = useChatStore();

const props = defineProps({
    basePrompt: String
});

const emits = defineEmits(['updateSchemaIsSet', 'sendRequest']);



const selectSuggestion = (suggestion) => {
    if (suggestion.pipeline != chatStore.actualPipeline) {

        emits('updateSchemaIsSet', false);


        // update chatstore
        chatStore.actualPipeline = suggestion.pipeline
        chatStore.actualPipelineLabel = suggestion.label
        chatStore.actualSchema = suggestion.form

        // Manage button suggestion
        // chatbox.toogleSuggestButtons(suggestion.pipeline)
    }
    // sendRequest
    emits('sendRequest')
}

const selectSuggestionParams = (suggestion) => {
    if (suggestion.pipeline != chatStore.actualPipeline) {
        emits('updateSchemaIsSet', false);
    
        // update chatstore
        chatStore.actualPipeline = suggestion.pipeline
        chatStore.actualPipelineLabel = suggestion.label
        chatStore.actualSchema = suggestion.form
        // Manage button suggestion
        // chatbox.toogleSuggestButtons(suggestion.pipeline)
        // chatbox.changeButtonShowPipelines(suggestion.label)
    
        chatStore.suggestions = []
    }
    // force close list
    chatbox.togglePipelineList(true)
}

// GET SUGGESTIONS ON TYPING
let inTyping = false
const querySuggestion = () => {
    if (!inTyping && !chatStore.isRunning) {
        inTyping = true

        setTimeout(() => {
            if (props.basePrompt) {
                chatManager.getSuggestion({ 'prompt': props.basePrompt })
            } else {
                chatStore.suggestions = []
            }

            inTyping = false

        }, 300);
    }
}

defineExpose({
    querySuggestion,
    selectSuggestionParams
})
</script>

<template>
    <!-- SUGGESTIONS -->
    <div class="chatform__prompt__suggestions" v-if="chatStore.suggestions.length">
        Suggestions :
        <p class=" chatform__prompt__suggestions__button" v-for="suggestion in chatStore.suggestions" :id="'button-' + suggestion.pipeline" :key="suggestion.pipeline">
            <button @click="selectSuggestion(suggestion)" :class="'chatform__prompt__suggestions__button__label' + (suggestion.pipeline == chatStore.defaultChatSettings.pipeline ? ' defaultButton' : '')" >
                {{ suggestion.label }}
            </button>

            <button class="chatform__prompt__suggestions__button__icon" @click="selectSuggestionParams(suggestion)" v-if="suggestion.pipeline != chatStore.defaultChatSettings.pipeline">
                <Settings color="white"/>
            </button>
        </p>
    </div>
    <!-- END OF SUGGESTIONS -->
</template>

<style lang="scss">@import "./chatsuggestions.scss";</style>