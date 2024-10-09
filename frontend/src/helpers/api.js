import { useRouter } from 'vue-router'
// class to call backend API
class API {
    constructor() {
        this.url = import.meta.env.VITE_BACKEND_URL;
        this.domain = import.meta.env.VITE_BACKEND_URL.replace('http://', '').replace('https://', '');
        this.router = useRouter()
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (const cookie of cookies) {
                const cookieTrimmed = cookie.trim();
                // Does this cookie string begin with the name we want?
                if (cookieTrimmed.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookieTrimmed.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    getHeadersToken() {
        return {
            'X-CSRFToken': this.getCookie('csrftoken'),
            'Authorization': `Token ${this.getCookie('token')}`
        }
    }
    
    // private method for get and post request
    async _request(method, path, data, type='json') {
        // set new header
        let headers = {}
        if (type == 'json') {
            headers = {
                'Content-Type': 'application/json',
            }
        }

        // FIXME: X-HTTP
        // set x http method override
        // if (method == 'DELETE' || method == 'PATCH' || method == 'PUT') {
        //     headers['X-HTTP-Method-Override'] = method
        //     method = 'POST'
        // }

        // get token headers
        const tokenHeaders = this.getHeadersToken();

        // set options
        let options = {
            method: method,
            credentials: 'include',
            headers: {...headers, ...tokenHeaders},
        };

        // set option body
        if (data && type == 'json') {
            options.body = JSON.stringify(data);
        } else {
            options.body = data
        }

        // fetch it
        const response = await fetch(this.url + path, options);
        if (response.status == 401) {
            this.router.push('/login')
        } else {
            return response.json();
        }
    }

    // === USERS ===
    async getUser() {
        const url = `/api/user/info`;
        return this._request('GET', url);
    }

    // Login
    async login(data) {
        return this._request('POST', '/api/user/login/', data);
    }

    // Logout
    async logout() {
        return this._request('GET', '/api/user/logout/');
    }

    async setUserPrompt(data) {
        const url = `/api/user/prompt/`;
        return this._request('POST', url, data);
    }

    async deleteUserPrompt(id) {
        const url = `/api/user/prompt/${id}/`;
        return this._request('DELETE', url);
    }

    async getUserPrompts() {
        const url = `/api/user/prompt/`;
        return this._request('GET', url);
    }

    // === FILES ===
    async uploadFile(data) {
        const url = `/api/file/`;
        return this._request('POST', url, data, "media");
    }

    async setFileFavorite(file_id, data) {
        const url = `/api/file/${file_id}/favorite/`;
        return this._request('POST', url, data);
    }

    // === CHATS ====
    // get all user chats session
    async getChats() {
        return this._request('GET', '/api/chat/');
    }

    // get single chat session
    async getChat(id) {
        return this._request('GET', `/api/chat/${id}/`);
    }

    // get chat session messages
    async getChatMessages(id) {
        return this._request('GET', `/api/chat/${id}/messages/`);
    }

    // create chat session
    async createChat() {
        return this._request('POST', '/api/chat/');
    }

    // update chat session
    async updateChat(id, data) {
        return this._request('PUT', `/api/chat/${id}/`, data);
    }

    // delete single chat
    async deleteChat(id) {
        return this._request('DELETE', `/api/chat/${id}/`)
    }

    // run pipeline
    async runPipeline(session_id, data) {
        const url = `/api/chat/${session_id}/process/`;
        return this._request('POST', url, data);
    }

    // === PIPELINES ====
    // get pipelines
    async getPipelines() {
        return this._request('GET', '/api/pipeline/');
    }

    // create pipeline
    async createDynamicPipeline(data) {
        const url = `/api/pipeline/`;
        return this._request('POST', url, data);
    }

    async updateDynamicPipelineParams(data) {
        const url = `/api/pipeline/${data.alias}/`;
        return this._request('PATCH', url, {data: data.params, type: "params"});
    }

    // get pipeline
    async getDynamicPipeline(alias) {
        return this._request('GET', `/api/pipeline/${alias}/`);
    }

    // delete pipeline
    async deleteDynamicPipeline(alias) {
        return this._request('DELETE', `/api/pipeline/${alias}/`);
    }

    // toggle status of pipeline
    async toogleActiveDynamicPipeline(alias, status) {
        const url = `/api/pipeline/${alias}/`
        return this._request('PATCH', url, {data: {'active': status}, 'type': 'attr'});
    }

    // get ia suggestion for chat session
    async getPipelineSuggestions(data) {
        return this._request('POST', `/api/pipeline/all/suggestions/`, data);
    }

    async updateDynamicPipeline(data) {
        return this._request('PATCH', `/api/pipeline/`, data);
    }

    // Save Message action
    async saveMessageAction(msg_id, action, data) {
        const url = `/api/message/${msg_id}/${action}/`;
        return this._request('POST', url, data);
    }

    // === FACTORIES ====
    async getFactoryList() {
        const url = `/api/factory/`;
        return this._request('GET', url);
    }

    async getFactoryCommonSchemes() {
        const url = `/api/factory/common/`;
        return this._request('GET', url);
    }

    async getFactorySchemes(factory) {
        const url = `/api/factory/${factory}/`;
        return this._request('GET', url);
    }

    // === FOLDERS & DOCUMENTS ====
    async getFolders() {
        const url = '/api/folders/'
        return this._request('GET', url);
    }

    async getFolder(data) {
        const url = '/api/folder/'
        return this._request('GET', url, data);
    }

    async getDocumentsPage(data) {
        const url = '/api/documents/'
        return this._request('POST', url, data);
    }

    async createFolder(data) {
        const url = '/api/folders/'
        return this._request('POST', url, data);
    }

    async deleteFolder(data) {
        const url = `/api/folder/`
        return this._request('DELETE', url, data);
    }

    async addDocumentToFolder(data) {
        const url = `/api/document/`
        return this._request('POST', url, data, "media");
    }

    async deleteDocumentFromFolder(data) {
        const url = `/api/document/`
        return this._request('DELETE', url, data);
    }

    async updateRights(data) {
        const url = `/api/folder_document_rights/`
        return this._request('PATCH', url, data);
    }

}

export default API;