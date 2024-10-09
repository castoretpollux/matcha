<script setup>
    import { ref, watch, onMounted } from 'vue';

    import { useChatStore } from "@/stores/chat";
    import { SessionStore } from "@/stores/session";
    import ChatManager from "@/helpers/chatManager.js"
    import { useI18n } from "vue-i18n";

    const { t } = useI18n();
    const chatStore = useChatStore();
    const session = SessionStore();
    const chatManager = new ChatManager()

    const emits = defineEmits(['togglePipelinePanel', 'checkPipelinePanelState', 'setPipelinePanelButtonLabel'])

    const pipelineContainer = ref(false)
    const active = ref(false)
    const forceHighlight = ref(null)
    const pipelines = ref([])


    const currentChat = ref(session.getChat())
    watch(() => chatStore.currentChatId, () => {
        currentChat.value = session.getChat()

        emits('setPipelinePanelButtonLabel', currentChat.value.pipeline_label)
        forceHighlight.value = currentChat.value.pipeline

    }, { deep: true });

    watch(() => chatStore.pipelines, () => {
        pipelines.value = []
        chatStore.pipelines.forEach((pipeline) => {
            if (pipeline.active) pipelines.value.push(pipeline)
        })
    })

    const selectPipeline = (pipeline) => {
        const data = {
            pipeline: pipeline.alias,
            pipeline_label: pipeline.label,
            pipeline_type: pipeline.type,
            // DEEP COPY TO NOT LOOSE pipeline things
            pipeline_schema: JSON.parse(JSON.stringify(pipeline.schema)),
            pipeline_uischema: JSON.parse(JSON.stringify(pipeline.uischema)),
        }

        // update chat
        chatManager.updateChat(currentChat.value, data)

        // Force suggest selected
        chatStore.suggestions = []
        forceHighlight.value = pipeline.alias

        // Change pipeline button label
        emits('setPipelinePanelButtonLabel', pipeline.label)

        // force close panels
        emits('checkPipelinePanelState', null)
    }

    const setDefaultPipeline = () => {
        const pipeline = {
            alias: chatStore.defaultChatSettings.pipeline,
            label: `${t('choose_one')} ${t('mode')}`,
            type: chatStore.defaultChatSettings.pipeline_type,
            schema: JSON.parse(JSON.stringify(chatStore.defaultChatSettings.pipeline_schema)),
            uischema: JSON.parse(JSON.stringify(chatStore.defaultChatSettings.pipeline_uischema)),
        }
        selectPipeline(pipeline)
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
        setDefaultPipeline
    })

    onMounted(() => {
        chatStore.pipelines.forEach((pipeline) => {
            if (pipeline.active) pipelines.value.push(pipeline)
        })
    })

</script>

<template>
    <div v-show="active" class="chatform__pipelines__list">
        <div ref="pipelineContainer" class="chatform__pipelines__list__container">
            <button
                v-for="pipeline in pipelines"
                :class="[
                    'chatform__pipelines__list__item',
                    {'highlight': chatStore.suggestions.includes(pipeline.alias) },
                    {'selected': forceHighlight == pipeline.alias }
                ]"
                @click="selectPipeline(pipeline)"
                :title="pipeline.alias"
                :key="pipeline.label"
            >
                {{ pipeline.label }} 
                <span>[{{ pipeline.type }}]</span>
            </button>
        </div>
    </div>
</template>