import API from "@/helpers/api";
import { useChatStore } from "@/stores/chat";
import { SessionStore } from "@/stores/session";

import ChatManager from "@/helpers/chatManager.js";

class WebSocketManager {
    constructor() {
        this.api = new API();
        this.chatStore = useChatStore();
        this.chatManager = new ChatManager();
        this.session = SessionStore();
    }

    // WEBSOCKET
    setup(chat) {
        const self = this;
        const ws_protocol_prefix = location.protocol=='http:' ? 'ws://' : 'wss://';
        const url = ws_protocol_prefix + self.api.domain + `/ws/channel/${chat.channel_id}`;
        const chatSession = this.chatManager.getChat(chat.id)
        
        chatSession.wsock = new WebSocket(url)
        chatSession.wsock.onmessage = function(event) {
            const data = JSON.parse(event.data);
            let panel = document.querySelector(`#log-${data.message.session_id}`)
            switch (data.type) {

                case 'runner.status':
                    console.log('runner.status', data.message)
                    // self.setSessionStatus(data.message)
                    break;

                case 'runner.log':
                    if (panel) {
                        const child = document.createElement('li')
                        child.textContent = data.message.content
                        child.classList.add('log')
                        panel.appendChild(child)
                    }
                    console.log('runner.log', data);
                    break;

                case 'runner.checkstatus':
                    console.log('Check status: ', data.messages)
                    break;

                case 'runner.error': {
                    if (panel) {
                        const child = document.createElement('li')
                        child.textContent = data.message.data
                        child.classList.add('error')
                        panel.appendChild(child)
                    }
                    console.log('runner.error', data);
                    self.chatStore.isRunning = false
                    break;
                }

                case 'runner.message': {
                    console.log('runner.message', data);
                    self.upsert(data.message.data)
                    break;
                }

                case 'runner.partial':
                    console.log('runner.partial', data);
                    self.upsert(data.message.data)
                    break;


                case 'runner.result':
                    console.log('runner.result', data);
                    self.chatStore.isRunning = false
                    break;

                case 'runner.title':
                    console.log('runner.title', data);
                    self.updateTitle(data.message.session_id, data.message.title)
                    break;
                default:
            }
        };

        chatSession.wsock.onopen = function() {
            chatSession.wsock.send(JSON.stringify({'type':'client.status', 'message':'connected'}));
        };

        // UPDATE CHAT
        this.chatManager.updateChat(chatSession, {'wsock': chatSession.wsock})
    }

    upsert(msgData) {
        // Find message by id
        const message = this.chatManager.getChatMessage(msgData);
        if (message) {
            // update message
            this.chatManager.updateChatMessage(message, {
                'inProgress': false,
                'content': msgData.content,
                'kind': msgData.kind
            })
        } else {
            // insert message
            msgData.inProgress = true
            this.chatManager.addMessage(msgData)
        }
    }

    updateTitle(sessionId, newTitle) {
        const chat = this.chatManager.getChat(sessionId);
        // update title 
        this.chatManager.updateChat(chat, {
            'title': newTitle
        })
    }

    getLastMessage(session_id) {
        const chat = this.chatManager.getChat(session_id)
        return chat.messages[chat.messages.length - 1]
    }

}

export default WebSocketManager;