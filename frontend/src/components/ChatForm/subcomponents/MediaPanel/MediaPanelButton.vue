<script setup>
    import { defineEmits, ref, defineExpose } from 'vue';
    
    import { ArrowUpFromLine, X } from 'lucide-vue-next';
    import { useChatStore } from "@/stores/chat";

    const chatStore = useChatStore()
    const emits = defineEmits(['toggleMediasPanel'])

    const buttonOpen = ref(null)
    const buttonClose = ref(null)

    const toggleMediasPanel = () => {
        emits('toggleMediasPanel', null)
        display('toggle')
    }

    const display = (state) => {
        switch (state) {
            case 'toggle':
                buttonOpen.value.classList.toggle('active')
                buttonClose.value.classList.toggle('active')
                break;
            case 'close':
                buttonOpen.value.classList.add('active')
                buttonClose.value.classList.remove('active')
                break;
            case 'open':
                buttonOpen.value.classList.remove('active')
                buttonClose.value.classList.add('active')
                break;
        }
    }

    defineExpose({
        display
    })

</script>

<template>
    <button ref="buttonOpen" class="chatform__togglemedia open active" @click="toggleMediasPanel()" :disabled="chatStore.isRunning ? true : false">
        <ArrowUpFromLine color="black"/>
    </button>
    <button ref="buttonClose" class="chatform__togglemedia close" @click="toggleMediasPanel()">
        <X color="black"/>
    </button>
</template>