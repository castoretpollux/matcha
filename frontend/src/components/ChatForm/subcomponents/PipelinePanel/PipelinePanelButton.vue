<script setup>
    import { defineEmits, ref, defineExpose } from 'vue';
    import { ChevronDown, X } from 'lucide-vue-next';
    
    import { useChatStore } from "@/stores/chat";
    import { SessionStore } from "@/stores/session";

    import { useI18n } from "vue-i18n";
    const { t } = useI18n();

    const chatStore = useChatStore()
    const session = SessionStore()
    const emits = defineEmits(['togglePipelineList', 'resetPipeline'])
    const buttonOpen = ref(null)
    const buttonOpenText = ref(null)
    const defaultButtonLabel = `${t('choose_one')} ${t('mode')}`

    const togglePipelineList = () => {
        emits('togglePipelineList', null)
        display('toggle')
    }

    const display = (state) => {
        switch (state) {
            case 'toggle':
                buttonOpen.value.classList.toggle('active')
                break;
            case 'close':
                buttonOpen.value.classList.remove('active')
                break;
            case 'open':
                buttonOpen.value.classList.add('active')
                break;
        }
    }

    const setLabel = (newLabel) => {
        if (newLabel) {
            buttonOpenText.value.textContent = newLabel
        } else {
            buttonOpenText.value.textContent = defaultButtonLabel
            emits('resetPipeline', null)
        }
    }

    defineExpose({
        display,
        setLabel
    })

</script>

<template>
    <div class="chatform__pipelines">
        <button
            v-if="chatStore.defaultChatSettings.pipeline != session.getChat()?.pipeline"
            :class="['chatform__pipelines__reset']"
            title="reset"
            id="resetPipeline"
            @click="setLabel(null)"
            :disabled="chatStore.isRunning ? true : false"
            >
            <X color="black"/>
        </button>
        <button
        :title="t('all_plural_f') + ' ' + t('ai')"
        ref="buttonOpen"
        :class="['chatform__pipelines__show']"
        @click="togglePipelineList()"
        :disabled="chatStore.isRunning ? true : false"
        >
            <ChevronDown class="chatform__pipelines__show__icon" color="black" />
            <span ref="buttonOpenText" class="chatform__pipelines__show__text">{{ defaultButtonLabel }}</span>
        </button>
    
    </div>
</template>