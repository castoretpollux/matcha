import API from "@/helpers/api";
import { useChatStore } from "@/stores/chat";
import { useUserStore } from "@/stores/user";
import { SessionStore } from "@/stores/session";
import { useRouter } from 'vue-router'


class FileManager {
    constructor() {
        this.api = new API();
        this.chatStore = useChatStore();
        this.userStore = useUserStore();
        this.router = useRouter();
        this.session = SessionStore();
    }

    async uploadFile(e) {
        const chat = this.session.getChat()
        const formData = new FormData();
        for (let file of e.target.files) {
            formData.append('files', file)
        }
        formData.append('session_id', chat.id)

        const response = await this.api.uploadFile(formData)
        chat.files = response.files
    }

    async setFileFavorite(index) {
        const chat = this.session.getChat()
        const file = chat.files[index]
        const file_id = file.id
        const file_state = !file.favorite
        await this.api.setFileFavorite(file_id, {'state': file_state})
    }

    filesSelected() {
        let fileSelecteds = []
        const chat = this.session.getChat()
        for (let file of chat.files) {
            if (file.selected) {
                fileSelecteds.push(file)
            }
        }
        return fileSelecteds
    }
}

export default FileManager;