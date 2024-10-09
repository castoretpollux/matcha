import { useChatStore } from "@/stores/chat";


class ChatManager {
    constructor() {
        this.chatStore = useChatStore();
    }

    // ==== MAP ====
    // set
    setChatsMap() {
        this.chatStore.chatsMap = {}
        this.chatStore.chats.forEach((chat, chatIndex) => {
            this.chatStore.chatsMap[chat.id] = {
                index: chatIndex,
                messageIdToIndex: {}
            }
        });
    }

    // set messages
    setChatMessagesMap(chat) {
        const messageIdToIndex = {}
        chat.messages.forEach((message, messageIndex) => {
            messageIdToIndex[message.id] = messageIndex
        })
        this.chatStore.chatsMap[chat.id].messageIdToIndex = messageIdToIndex
    }

    // add
    addChatToMap(chat) {
        this.chatStore.chatsMap[chat.id] = {
            index: 0,
            messageIdToIndex: {}
        }
        this.resetChatMapIndex()
    }

    // delete
    deleteChatToMap(chat) {
        delete this.chatStore.chatsMap[chat.id]
        this.resetChatMapIndex()
    }

    // reset index
    resetChatMapIndex() {
        this.chatStore.chats.forEach((chat, chatIndex) => {
            this.chatStore.chatsMap[chat.id].index = chatIndex
        });
    }

    // ==== CHATS ====
    // get chat
    getChat(id=false) {
        let target_id = null
        if (id) target_id = id
        else if (!id) target_id = this.chatStore.currentChatId

        if (this.chatStore.chatsMap[target_id]) {
            const chatIndex = this.chatStore.chatsMap[target_id].index
            return this.chatStore.chats[chatIndex]
        }
        return null
    }

    // update chat
    updateChat(chat, datas) {
        const chatIndex = this.chatStore.chatsMap[chat.id].index
        for (const [key, value] of Object.entries(datas)) {
            this.chatStore.chats[chatIndex][key] = value
        }
    }

    // ==== CHAT LIST ====
    // add
    addToChatList(chat) {
        this.chatStore.chats.unshift(chat)
        this.chatStore.currentChatId = chat.id
        this.addChatToMap(chat)
    }

    // remove one
    removeFromChatList(chat) {
        const chatIndex = this.chatStore.chatsMap[chat.id].index
        this.chatStore.chats.splice(chatIndex, 1);
        this.deleteChatToMap(chat)
    }

    // remove all
    removeChatList() {
        this.chatStore.chats = []
        this.setChatsMap()
    }

    // ==== MESSAGES ====
    // add message
    addMessage(message) {
        const chat = this.chatStore.chatsMap[message.session_id]
        const chatIndex = chat.index

        this.chatStore.chats[chatIndex].messages.push(message)
        this.chatStore.chats[chatIndex].has_messages = true

        const lengthMessages = this.chatStore.chats[chatIndex].messages.length
        chat.messageIdToIndex[message.id] = lengthMessages - 1
    }

    // get message
    getChatMessage(message) {
        const chat = this.chatStore.chatsMap[message.session_id]

        const chatIndex = chat.index
        const messageIndex = chat.messageIdToIndex[message.id]
        
        return this.chatStore.chats[chatIndex].messages[messageIndex]
    }

    // update message
    updateChatMessage(message, datas) {
        const chat = this.chatStore.chatsMap[message.session_id]

        const chatIndex = chat.index
        const messageIndex = chat.messageIdToIndex[message.id]

        for (const [key, value] of Object.entries(datas)) {
            this.chatStore.chats[chatIndex].messages[messageIndex][key] = value
        }
    }

    // get last chat message
    getLastChatMessage(session_id) {
        const chat = this.chatStore.chats.find((chat2) => chat2.id === session_id);
        if (chat.messages) return chat.messages[chat.messages.length - 1]
        return null
    }

    // ==== PIPELINES ====
    getPipelineByAlias(alias) {
        return this.chatStore.pipelines.find((pipeline) => pipeline.alias === alias);
    }
}

export default ChatManager;
