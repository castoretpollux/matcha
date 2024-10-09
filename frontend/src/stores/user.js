import { defineStore } from "pinia";
import { ref, computed } from "vue";

export const useUserStore = defineStore('user', () => {
    const showDashboard = ref(true)
    const forcedLoggedIn = ref(false)
    
    const user = ref({})
    const groups = ref([])
    const users = ref([])
    const preferences = ref({})

    function getCookieValue(name) {
        const regex = new RegExp(`(^| )${name}=([^;]+)`)
        const match = document.cookie.match(regex)
        if (match) {
            return match[2]
        } else {
            return ''
        }
    }

    const loggedIn = computed(() => {
        let token = getCookieValue('token')
        if (token && token != "''") {
            return true
        } else {
            document.cookie = `token=''`;
            document.cookie = `csrftoken=''`;
            return false
        }
    })

    return { user, groups, users, preferences, loggedIn, forcedLoggedIn, showDashboard }
})