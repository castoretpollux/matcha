<script setup>

import { ref, onMounted, defineModel, watch } from 'vue';

import { Send } from 'lucide-vue-next';

import { useChatStore } from "@/stores/chat";
import { SessionStore } from "@/stores/session";



import FileManager from "@/helpers/fileManager.js"
import { checkRequiredFields } from '@/helpers/utils.js'

import MediaPanel       from '@/components/ChatForm/subcomponents/MediaPanel/MediaPanel.vue';  // NOSONAR
import PipelinePanel    from '@/components/ChatForm/subcomponents/PipelinePanel/PipelinePanel.vue';  // NOSONAR
import ParameterPanel   from '@/components/ChatForm/subcomponents/ParameterPanel/ParameterPanel.vue';  // NOSONAR
import VoiceReader      from '@/components/ChatForm/subcomponents/VoiceReader/VoiceReader.vue';  // NOSONAR
import Prompt           from '@/components/ChatForm/subcomponents/Prompt/Prompt.vue';  // NOSONAR
import RegistredPrompt  from '@/components/ChatForm/subcomponents/RegistredPrompt/RegistredPrompt.vue';  // NOSONAR

const chatStore = useChatStore();
const session = SessionStore();

const fileManager = new FileManager();


let dataToSend = {}
const updateDataToSend = (newData) => {
    dataToSend = newData;
}

const promptModel = defineModel()
const promptElement = ref(null)

// #### PANELS ####
// MEDIAS
const mediaPanel = ref(null)
const mediaPanelButton = ref(null)
const toggleMediasPanel = () => {
    mediaPanel.value.display('toggle')
    closePanels(mediaPanel)
}

// PIPELINES
const pipelinePanel = ref(null)
const pipelinePanelButton = ref(null)
const togglePipelinePanel = () => {
    pipelinePanel.value.display('toggle')
    closePanels(pipelinePanel)
}

const checkPipelinePanelState = () => {
    const chat = session.getChat()
    if (!chat.messages || !chat.messages.length) {
        pipelinePanel.value.display('open')
        pipelinePanelButton.value.display('open')
    } else {
        closePanels()
    }
}

const setPipelinePanelButtonLabel = (label) => {
    promptModel.value = ''
    pipelinePanelButton.value.setLabel(label)
}

// PARAMETERS
const parameterPanel = ref(null)
const parameterPanelButton = ref(null)
const toggleParameterPanel = () => {
    parameterPanel.value.display('toggle')
    closePanels(parameterPanel)
}

// REGISTRED PROMPT
const registredPromptPanel = ref(null)
const registredPromptPanelButton = ref(null)
const toggleRegistredPromptPanel = () => {
    registredPromptPanel.value.display('toggle')
    closePanels(registredPromptPanel)
}

// ALL
const closePanels = (except=null) => {
    if (except != parameterPanel) {
        parameterPanel.value.display('close')
        parameterPanelButton.value.display('close')
    }
    if (except != pipelinePanel) {
        pipelinePanel.value.display('close')
        pipelinePanelButton.value.display('close')
    }
    if (except != mediaPanel) {
        mediaPanel.value.display('close')
        mediaPanelButton.value.display('close')
    }
    if (except != registredPromptPanel) {
        registredPromptPanel.value.display('close')
        registredPromptPanelButton.value.display('close')
    }
}
// #### END OF PANELS ####


// #### PROMPT EVENTS ####
const handleRegistredPrompt = (prompt) => {
    promptModel.value = prompt
}

const focusPrompt = (e) => {
    if (e.target.classList.contains('chatform') || e.target.classList.contains('chatform__prompt')) {
        promptElement.value.focusPrompt()
    }
} 
// #### END OF PROMPT EVENTS ####


// SEND REQUEST
const sendRequest = () => {
    checkDataToSend()
    if (!chatStore.isRunning && chatStore.formIsValid) {
        closePanels()
        chatStore.isRunning = true

        // prompt or text
        dataToSend['text'] = promptModel.value
        dataToSend['prompt'] = promptModel.value
        dataToSend['files'] = fileManager.filesSelected()

        session.runPipeline(chatStore.currentChatId, dataToSend);

        promptModel.value = ''

        // wait 500ms to set prompt height
        setTimeout(() => {
            promptElement.value.setPromptHeight()
        }, 500);
    }
}

// Send button
const allowSendRequest = ref(false)
watch(() => [promptModel.value, chatStore.onlyFileAllowed, dataToSend],  () => {
    // DELETE (ENTER KEY)
    if (promptModel.value && promptModel.value.endsWith('\n')) {
        promptModel.value = promptModel.value.slice(0, -1);
    }

    dataToSend['prompt'] = promptModel.value
    checkDataToSend()
})

const checkDataToSend = () => {
    session.getChat()
    const chat = session.getChat()
    chatStore.formIsValid = checkRequiredFields(chat.pipeline_schema, dataToSend)
}

watch(() => chatStore.formIsValid, () => {
    allowSendRequest.value = chatStore.formIsValid;
})

// Show or not pipeline panel on chat loading
watch(() => chatStore.currentChatId, () => {
    checkPipelinePanelState()
    checkDataToSend()
})

// on Mounted
onMounted(() => {
    // Display pipeline panel
    checkPipelinePanelState()
    checkDataToSend()
})

</script>

<template>

    <div class="chatform" @click="focusPrompt">
        <!-- SELECT WITH USER REGISTERED PROMPT -->
        <RegistredPrompt.RegistredPromptComponent ref="registredPromptPanel" @handleRegistredPrompt="(prompt) => handleRegistredPrompt(prompt)"/>

        <!-- PARAMETERS PANEL -->
        <ParameterPanel.ParameterPanelComponent ref="parameterPanel" :dataToSend="dataToSend" @updateData="updateDataToSend"/>
        <!-- END OF PARAMETERS PANEL -->

        <!-- PIPELINES -->
        <PipelinePanel.PipelinePanelButton ref="pipelinePanelButton" @togglePipelineList="togglePipelinePanel" @resetPipeline="pipelinePanel.setDefaultPipeline()"/>
        <PipelinePanel.PipelinePanelComponent
            ref="pipelinePanel"
            @togglePipelinePanel="togglePipelinePanel"
            @checkPipelinePanelState="checkPipelinePanelState"
            @setPipelinePanelButtonLabel="setPipelinePanelButtonLabel"
        />
        <!-- END OF PIPELINES -->

        <!-- MEDIA PANEL -->
        <MediaPanel.MediaPanelComponent ref="mediaPanel"/>
        <!-- ENDOF MEDIA PANEL -->

        <!-- FORM -->
        <div class="chatform__prompt" @click="focusPrompt">

            <RegistredPrompt.RegistredPromptButton ref="registredPromptPanelButton" @togglePromptList="toggleRegistredPromptPanel"/>

            <!-- PARAMETERS (button) -->
            <ParameterPanel.ParameterPanelButton
                ref="parameterPanelButton"
                @toggleParameters="toggleParameterPanel"
            />
            <!-- END OF PARAMETERS -->

            <!-- MEDIA (button) -->
            <MediaPanel.MediaPanelButton ref="mediaPanelButton" @toggleMediasPanel="toggleMediasPanel"/>
            <!-- END OF MEDIA -->

            <!-- PROMPT -->
            <Prompt @sendRequest="sendRequest" v-model="promptModel" ref="promptElement"/>
            <!-- END OF PROMPT -->

            <!-- VOICE READER -->
            <VoiceReader @sendRequest="sendRequest" @update:read="(newValue) => promptModel = newValue"/>
            <!-- END OF VOICE READER -->

            <!-- BUTTON SEND -->
            <button class="chatform__send" :disabled="chatStore.isRunning ? true : allowSendRequest ? false : true" @click="sendRequest">
                <Send color="black"/>
            </button>
            <!-- END OF BUTTON SEND -->

        </div>
        <!-- END FORM -->

    </div>

</template>

<style lang="scss">@import "./chatform.scss";</style>