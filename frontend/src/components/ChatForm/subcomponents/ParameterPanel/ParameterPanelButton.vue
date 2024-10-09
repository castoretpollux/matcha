<script setup>
    import { defineEmits, ref, defineExpose } from 'vue';
    import { SlidersHorizontal, X } from 'lucide-vue-next';
    
    import { useChatStore } from "@/stores/chat";
    
    const chatStore = useChatStore()
    const emits = defineEmits(['toggleParameters'])
    const buttonOpen = ref(null)
    const buttonClose = ref(null)

    const toggleParameters = () => {
        emits('toggleParameters', null)
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
    <!-- BUTTON SUBPARAMETERS -->
    <button ref="buttonOpen" class="chatform__parameters open active" @click="toggleParameters" v-show="chatStore.hasParameters">
        <SlidersHorizontal color="black"/>
    </button>
    <button ref="buttonClose" class="chatform__parameters close" @click="toggleParameters" v-show="chatStore.hasParameters">
        <X color="black"/>
    </button>
    <!-- END OF BUTTON SUBPARAMETERS -->
</template>