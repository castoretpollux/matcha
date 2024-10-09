import API from "@/helpers/api";
import { useChatStore } from "@/stores/chat";


class FolderManager {
    constructor() {
        this.api = new API();
        this.chatStore = useChatStore();
    }

    async getFolders() {
        return this.api.getFolders()
    }

    async createFolder(data) {
        this.api.createFolder(data)
    }

    async deleteFolder(data) {
        await this.api.deleteFolder(data)
    }

    async getDocumentsPage(data) {
        return this.api.getDocumentsPage(data)
    }

    async addDocument(data) {
        const formContentData = new FormData();
        formContentData.append('file', data.file);
        formContentData.append('path', data.path);

        await this.api.addDocumentToFolder(formContentData)
        .then(data2 => {
            this.chatStore.filesToUpload[data2.path].files[data2.file] = {
                state: data2.state,
                url: data2.url
            }
        })
    }

    async deleteDocument(data) {
        await this.api.deleteDocumentFromFolder(data)
    }

    async updateRights(data) {
        await this.api.updateRights(data)
    }
}

export default FolderManager;