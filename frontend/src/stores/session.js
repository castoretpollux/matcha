import { defineStore } from "pinia";
import { useRouter } from 'vue-router'

import { useChatStore } from "@/stores/chat";
import { useUserStore } from "@/stores/user";


import API from "@/helpers/api";
import ChatManager from "@/helpers/chatManager.js";
import WebSocketManager from "@/helpers/websocketManager.js";
import { isEmpty } from '@/helpers/utils.js';


export const SessionStore = defineStore('session', () => {

    const api = new API();
    const chatStore = useChatStore();
    const userStore = useUserStore();
    const router = useRouter();
    const websocket = new WebSocketManager();
    const chatManager = new ChatManager();

    async function init() {
        const response = await api.getUser();
        if (response.connected) {
            // Show the dashboard
            userStore.showDashboard = true

            // Get user informations
            userStore.user = response.user
            userStore.groups = response.groups
            userStore.users = response.users
            userStore.preferences = response.preferences

            // get default chat settings
            setDefaultChatSettings()

            // get all user chats
            await getChats()

            // Get all user pipelines
            const pipelineReponse = await getUserPipelines();
            chatStore.pipelines = pipelineReponse.pipelines;
    
            // If there are no chat sessions, create a new one
            if (!chatStore.chats?.length) addChat();

            // If there are chat sessions, retrieve the LAST one
            if (chatStore.chats.length) {
                // get the last one chat
                const lastChat = chatStore.chats[0]
                // If the last one chat have some messages, create new chat
                lastChat.has_messages ? await addChat() : loadChat(lastChat.id);
            }
        } else {
            userStore.showDashboard = false
            router.push('/login')
        }
    }

    function getChat() {
        return chatManager.getChat()
    }

    async function getChats() {
        chatStore.chats = await api.getChats()
        chatManager.setChatsMap()
    }

    async function setDefaultChatSettings() {
        // Set default chat
        if (isEmpty(chatStore.defaultChatSettings)) {
            chatStore.defaultChatSettings = await api.getChat('default');
        }
    }

    async function addChat() {
        resetSession()
        // Create new chat session
        const newChat = await api.createChat()
        chatManager.addToChatList(newChat)
        chatStore.currentChatId = newChat.id
        websocket.setup(newChat)
    }

    // Add new chat if current session chat have message
    async function createChat() {
        const chat = chatManager.getChat()
        if (!chat || chat.has_messages) addChat()
    }

    // Load chat session
    async function loadChat(id) {
        resetSession()
        const chat = chatManager.getChat(id)

        // If chat doesn't have web socket
        if (!chat.wsock) websocket.setup(chat);

        // If chat has messages
        if (chat.has_messages) {
            // Get chat messages
            const chat_messages = await api.getChatMessages(id);
            chatManager.updateChat(chat, chat_messages)
            chatManager.setChatMessagesMap(chat)
        }

        let pipeline_to_update = chatStore.defaultChatSettings
        // If chat doesn't have pipeline
        if (!chat.pipeline && chat.has_messages) {
            // Update pipeline
            const last_message = chatManager.getLastChatMessage(id)
            if (last_message) {
                const last_pipeline = chatManager.getPipelineByAlias(last_message.pipeline)
                if (last_pipeline) {
                    pipeline_to_update = {
                        pipeline: last_pipeline.alias,
                        pipeline_label: last_pipeline.label,
                        pipeline_type: last_pipeline.type,
                        pipeline_schema: JSON.parse(JSON.stringify(last_pipeline.schema)),
                        pipeline_uischema: JSON.parse(JSON.stringify(last_pipeline.uischema)),
                    }
                }
            }
        }
        chatManager.updateChat(chat, pipeline_to_update)

        // Change this id
        chatStore.currentChatId = id
    }


    // delete chat session
    async function deleteChat(id) {
        resetSession()

        if (id == 'all') {
            chatStore.chats.forEach((chat) => {
                chat.wsock?.close();
            })
            chatManager.removeChatList()
        } else {
            const chat = chatManager.getChat(id)
            chat.wsock?.close();
            chatManager.removeFromChatList(chat)
        }

        await api.deleteChat(id)
        await createChat()
    }

    function resetSession() {
        chatStore.isRunning = false
        chatStore.suggestions = [];
    }

    // // POST ACTION
    async function setMessageAction(message, action, state) {
        const messageObj = chatManager.getChatMessage(message)
        const data = {}

        if (action == 'favorite') {
            state = !state
            data.favorite = state
        } else if (action == 'valid') {
            if (messageObj.valid === state) {
                state = ''
            }
            data.valid = state
        }
        
        const datas = {
            'state': state,
            'session_id': messageObj.session_id
        }

        await api.saveMessageAction(messageObj.id, action, datas)
        chatManager.updateChatMessage(messageObj, data)
    }


    // ======================
    // ====== PIPELINE ======
    // ======================
    // GET PIPELINE LIST
    async function getUserPipelines() {
        return api.getPipelines();
    }

    // GET PIPELINE SUGGESTIONS
    async function getPipelineSuggestions(data) {
        // Get suggestions from data
        const suggestions = await api.getPipelineSuggestions(data);
        chatStore.suggestions = []

        // Updaye chatstore suggestions
        suggestions?.data?.forEach(suggestionPipeline => {
            chatStore.suggestions.push(suggestionPipeline.alias)    
        });
    }
    
    // RUN PIPELINE
    async function runPipeline(sessionId, data) {
        const chat = chatManager.getChat(sessionId)
        const datas = {
            pipeline: chat.pipeline,
            payload: data,
        };
        await api.runPipeline(sessionId, datas);
    }

    async function updateDynamicPipeline(data) {
        await api.updateDynamicPipeline(data)
    }

    return {
        init,
        getChats,

        getChat,
        createChat,
        loadChat,
        // updateChat,
        deleteChat,

        setMessageAction,

        getPipelineSuggestions,
        getUserPipelines,
        runPipeline,
        updateDynamicPipeline,
    }
})