import { defineStore } from "pinia";
import { ref } from "vue";


export const useAdminStore = defineStore('admin', () => {
    const BaseModelSchema = ref(null)
    const BaseUiModelSchema = ref(null)
    const FactoryModelSchema = ref(null)
    const FactoryUiModelSchema = ref(null)
    const currentFactory = ref(null)
    const factoryList = ref([])

    return { 
        BaseModelSchema,
        BaseUiModelSchema,
        FactoryModelSchema,
        FactoryUiModelSchema,
        currentFactory,
        factoryList
    }

})