import { defineStore } from "pinia";
import { ref } from "vue";

export const useChatStore = defineStore('chat', () => {
    
    
    const chats = ref([])
    const chatsMap = ref([])
    
    const chatSettings = ref({})
    const defaultChatSettings = ref({})
    

    const currentChatId = ref('')
    const hasParameters = ref(false)
    const hasFiles = ref(false)
    const onlyFileAllowed = ref(false)
    const formIsValid = ref(false)

    const pipelines = ref([])
    const suggestions = ref([])

    const isRunning = ref(false)

    const currentChat = ref(null)
    const webSockets = ref({})
    const folders = ref([])
    const filesToUpload = ref({})

    return { 
        chats,
        chatsMap,
        chatSettings,
        defaultChatSettings,
        
        currentChat,
        currentChatId,
        hasParameters,
        hasFiles,
        onlyFileAllowed,
        formIsValid,
        
        pipelines,
        suggestions,

        isRunning,
        webSockets,

        folders,
        filesToUpload
    }
})