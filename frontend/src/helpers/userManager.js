import API from "@/helpers/api";

import { useChatStore } from "@/stores/chat";
import { useUserStore } from "@/stores/user";
import { useRouter } from 'vue-router'
import ChatManager from "@/helpers/chatManager.js";

import { validateTrimInput, setNodeError } from "@/helpers/utils";


class UserManager {
    constructor() {
        this.api = new API();
        this.chatStore = useChatStore();
        this.userStore = useUserStore();
        this.router = useRouter()
        this.chatManager = new ChatManager();
    }

    async login(data) {
        if (validateTrimInput(data.username.value, data.username.node) &&
            validateTrimInput(data.password.value, data.password.node)) {
            
            const loginData = {
                username: data.username.value,
                password: data.password.value,
            };

            try {
                // Attempting to log in via the API
                const response = await this.api.login(loginData);
                if (response.status === 'success') {
                    // Storing tokens in cookies if login is successful
                    document.cookie = `token=${response.token};max-age=${response.max_age}`;
                    document.cookie = `csrftoken=${response.csrfToken};max-age=${response.max_age}`;
                    // Updating the user state in the store
                    this.userStore.forcedLoggedIn = true;
                    // Redirecting to the dashboard
                    this.router.push('/');
                } else {
                    // Handling login errors
                    setNodeError(data.username.node);
                    setNodeError(data.password.node);
                }
            } catch (error) {
                console.error("Login error:", error);
                // Handling exceptions during login
                setNodeError(data.username.node);
                setNodeError(data.password.node);
            }
        }
    }

    async logout() {
        await this.api.logout();
        this.router.push('/login')
    }

    async addPromptToUserPreferences(prompt, message = null) {
        if (prompt && prompt.endsWith('\n')) prompt = prompt.slice(0, -1);

        if (message) {
            await this.api.setUserPrompt({"prompt": prompt, "message": message.id})
        } else { 
            await this.api.setUserPrompt({"prompt": prompt})
        }

        const response = await this.api.getUserPrompts()
        this.userStore.preferences['prompts'] = response.prompts

        this.chatManager.updateChatMessage(message, {"is_prompt": true})
    }

    async deletePromptToUserPreferences(message) {
        await this.api.deleteUserPrompt(message.id)
        const response = await this.api.getUserPrompts()
        this.userStore.preferences['prompts'] = response.prompts

        this.chatManager.updateChatMessage(message, {"is_prompt": false})
    }
}

export default UserManager;