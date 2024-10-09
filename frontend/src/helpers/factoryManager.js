import API from "@/helpers/api";
import { useAdminStore } from "@/stores/admin";
import { SessionStore } from "@/stores/session";
import { useChatStore } from "@/stores/chat";

class FactoryManager {
    constructor() {
        this.api = new API();
        this.adminStore = useAdminStore();
        this.chatStore = useChatStore();
        this.session = SessionStore();
    }

    async getFactoryCommonSchemes() {
        // Initialize baseModelSchema
        const response = await this.api.getFactoryCommonSchemes()
        this.adminStore.BaseModelSchema = response.schema
        this.adminStore.BaseModelUiSchema = response.uischema
    }

    async getFactorySchemes(factory) {
        const response = await this.api.getFactorySchemes(factory.key);
        this.adminStore.FactoryModelSchema = response.schema
        this.adminStore.FactoryModelUiSchema = response.uischema
        this.adminStore.currentFactory = factory
    }

    async getFactoryList() {
        const response = await this.api.getFactoryList()
        this.adminStore.factoryList = response.factory_list
    }

    async getDynamicPipeline(alias) {
        return this.api.getDynamicPipeline(alias)
    }

    async createDynamicPipeline(data) {
        console.log("createDynamicPipeline")

        await this.api.createDynamicPipeline(data)
        const responsePipeline = await this.session.getUserPipelines()
        this.chatStore.pipelines = responsePipeline.pipelines
    }

    async updateDynamicPipelineParams(data) {
        await this.api.updateDynamicPipelineParams(data)
        const responsePipeline = await this.session.getUserPipelines()
        this.chatStore.pipelines = responsePipeline.pipelines
    }
    
    async deleteDynamicPipeline(alias) {
        await this.api.deleteDynamicPipeline(alias)
        const responsePipeline = await this.session.getUserPipelines()
        this.chatStore.pipelines = responsePipeline.pipelines
    }

    async toogleActiveDynamicPipeline(alias, status) {
        await this.api.toogleActiveDynamicPipeline(alias, status)
        const responsePipeline = await this.session.getUserPipelines()
        this.chatStore.pipelines = responsePipeline.pipelines
    }

}

export default FactoryManager;
