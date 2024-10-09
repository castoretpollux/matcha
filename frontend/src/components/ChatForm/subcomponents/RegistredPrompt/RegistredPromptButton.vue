<script setup>
    import { ref, defineEmits, defineExpose } from 'vue';
    import { MessageSquareShare, MessageSquareOff } from 'lucide-vue-next';
    import { useChatStore } from '@/stores/chat'

    const emits = defineEmits(['togglePromptList', 'sendRequest', 'update:read'])
    const chatStore = useChatStore()

    const buttonOpenRegistredPrompt = ref(null)
    const buttonCloseRegistredPrompt = ref(null)

    const togglePromptList = () => {
        emits('togglePromptList', null)
        display('toggle')
    }

    const display = (state) => {
        switch (state) {
            case 'toggle':
                buttonOpenRegistredPrompt.value.classList.toggle('active')
                buttonCloseRegistredPrompt.value.classList.toggle('active')
                break;
            case 'close':
                buttonOpenRegistredPrompt.value.classList.add('active')
                buttonCloseRegistredPrompt.value.classList.remove('active')
                break;
            case 'open':
                buttonOpenRegistredPrompt.value.classList.remove('active')
                buttonCloseRegistredPrompt.value.classList.add('active')
                break;
        }
    }

    defineExpose({
        display
    })

</script>

<template>
    <button ref="buttonOpenRegistredPrompt" class="registred-prompt__button active" @click="togglePromptList" :disabled="chatStore.isRunning ? true : false">
        <MessageSquareShare color="black"/>
    </button>
    <button ref="buttonCloseRegistredPrompt" class="registred-prompt__button" @click="togglePromptList" :disabled="chatStore.isRunning ? true : false">
        <MessageSquareOff color="black"/>
    </button>
</template>

<style lang="scss">@import "./registredprompt.scss";</style>
