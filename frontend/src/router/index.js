import { createRouter, createWebHistory } from "vue-router";
import http from "@/http";
import { api } from "@/settings";
import { refreshToken } from "@/utils/token";

const routes = [
    {
        path: "/login", // 访问路径
        name: "Login", // 组件别名
        alias: "/", // 路径别名
        component: () => import("../views/Login.vue"),
        meta: {
            requiresAuth: false,
        },
    },
    {
        path: "/base", // 导航组件
        name: "Base",
        component: () => import("../views/Base.vue"),
        meta: {
            requiresAuth: true,
        },
        children: [
            {
                path: "home",
                name: "Home",
                component: () => import("../views/Home.vue"),
                meta: {
                    requiresAuth: true,
                }
            },
            {
                path: "host",
                name: "Host",
                component: () => import("../views/Host.vue"),
                meta: {
                    requiresAuth: true,
                }
            },
            {
                path: "category",
                name: "Category",
                component: () => import("../views/Category.vue"),
                meta: {
                    requiresAuth: true,
                }
            },
            {
                path: "user",
                name: "User",
                component: () => import("../views/User.vue"),
                meta: {
                    requiresAuth: true,
                }
            },
            {
                path: "allocation",
                name: "Allocation",
                component: () => import("../views/Allocation.vue"),
                meta: {
                    requiresAuth: true,
                }
            },
            {
                path: "test",
                name: "Test",
                component: () => import("../views/Test.vue"),
                meta: {
                    requiresAuth: true,
                }
            },
        ],
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes: routes,
});

// 路由守卫,前置守卫,页面渲染前执行
router.beforeEach((to, from, next) => {
    document.title = to.name;
    let token = sessionStorage.token || localStorage.token;
    if (to.meta.requiresAuth) {
        if (token) {
            http.post(api.token_verify, {
                token: token
            }).then(() => {
                next();
            }).catch(() => {
                sessionStorage.removeItem("token");
                localStorage.removeItem("token");
                console.log("token已过期或已失效");

                next({ name: "Login" })
            })
        } else {
            next({ name: "Login" })
        }
    } else {
        // 如果是Login页面,有令牌就直接到主页
        if (token && to.name == 'Login') {
            http.post(api.token_verify, {
                token: token
            }).then(() => {
                console.log("当前用户已通过token验证");
                next({ name: "Home" });
            }).catch(() => {
                sessionStorage.removeItem("token");
                localStorage.removeItem("token");
                console.log("token已过期或已失效");
                refreshToken()
                next();
            })
        } else {
            next();
        }
    }
});

export default router;