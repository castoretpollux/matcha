<script setup>
    import { ref, onMounted, defineEmits } from 'vue';
    import { Mic } from 'lucide-vue-next';
    import { useChatStore } from "@/stores/chat";

    const emits = defineEmits(['sendRequest', 'update:read'])
    const chatStore = useChatStore()

    const micColor = ref('black')
    const recognitionIsReady = ref(false)
    
    // Start speech recognition :
    let recognition;
    const handleListening = () => {
        
        recognition.continuous = false;
        recognition.lang = "fr-FR";
        recognition.maxAlternatives = 1;
        recognition.interimResults = true;

        recognition.onresult = (event) => {
            const result = event.results[0][0];
            emits('update:read', result.transcript)
        }
        
        recognition.onend = () => {
            emits('sendRequest', null)
            micColor.value = 'white'
        }

        micColor.value = 'red'
        recognition.start();
    }

    onMounted(() => {
        try {
            // on Google web browser
            recognition = new window.webkitSpeechRecognition();
            recognitionIsReady.value = true
        } catch {
            console.log('recognition is not enabled')
        }
    })

</script>

<template>
    <button v-if="recognitionIsReady" class="chatform__mic clickable" @click="handleListening" :disabled="chatStore.isRunning ? true : false">
        <Mic :color="micColor"/>
    </button>
</template>
