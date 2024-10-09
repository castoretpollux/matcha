import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "@/views/Dashboard/Dashboard.vue";
import { useUserStore } from "@/stores/user";



const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/",
            name: "Dashboard",
            component: Dashboard,
            meta: { requiresAuth: true },
        },
        {
            path: "/login",
            name: "login",
            component: () => import("../views/Login/Login.vue"),
        }
    ],
});

router.beforeEach((to, _from, next) => {
    if (to.matched.some(record => record.meta.requiresAuth)) {
        // Check if the user is authenticated before allowing access to this route
        if (useUserStore().loggedIn || useUserStore().forcedLoggedIn) {
            useUserStore().forcedLoggedIn = false
            next()
        } else {
            next({
                path: '/login',
                query: { redirect: to.fullPath },
            })
        }
    } else {
        next() // Make sure to call next() when the user is not going to a route that requires authentication
    }
})

export default router;
