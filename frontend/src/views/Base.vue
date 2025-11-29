<template>
    <a-layout :style="{ minHeight: '100vh', minWidth: '1200px' }">
        <a-layout-sider v-model:collapsed="collapsed" collapsible>
            <div class="logo">
                <div ref="logoLabel" class="logo-label">{{ logoText }}</div>
            </div>
            <!-- 菜单 -->
            <a-menu v-model:selectedKeys="selectedKeys" theme="dark" mode="inline">
                <a-menu-item v-for="value in base_list" :key="value.key">
                    <component :is="$icons[`${value.icon}`]"></component>
                    <span><router-link :to="`/base/${value.link}`">{{ value.name }}</router-link></span>
                </a-menu-item>
            </a-menu>
        </a-layout-sider>
        <a-layout>
            <!-- 头部 -->
            <a-layout-header style="background: #fff; padding: 0" />
            <!-- 主体 -->
            <a-layout-content style="margin: 0 16px">
                <!-- 面包屑 -->
                <a-breadcrumb>
                    <a-breadcrumb-item>{{ logoText }}</a-breadcrumb-item>
                    <a-breadcrumb-item>{{ base_list[selectedKeys - 1].name }}</a-breadcrumb-item>
                    <!-- 功能栏 -->
                    <a-breadcrumb-item class="toolbar">
                        <user-outlined /> {{ username }}
                        <a-button style="margin: 0 16px" type="primary" html-type="text" @click="logout">
                            <logout-outlined />logout
                        </a-button>
                    </a-breadcrumb-item>
                </a-breadcrumb>
                <div :style="{ padding: '24px', background: '#fff', minHeight: '360px' }">
                    <router-view></router-view>
                </div>
            </a-layout-content>
            <!-- 脚部 -->
            <a-layout-footer style="text-align: center">
                *** Copyright Notice Here ***
            </a-layout-footer>
        </a-layout>
    </a-layout>
</template>


<script setup>
import { createVNode, ref, watch } from 'vue';
import { Modal } from "ant-design-vue"
import { ExclamationCircleOutlined } from '@ant-design/icons-vue';
import router from '@/router/index.js';
import { base_list } from '@/utils/list';

const collapsed = ref(false);
const logoLabel = ref(null);
const logoText = ref('Web-ssh')
const selectedKeys = ref([1]);
const username = localStorage.username;

if (sessionStorage.getItem("selectedKeys")) { // 储存当前页面id,这样刷新页面可以保持原页面不动
    selectedKeys.value = [parseInt(sessionStorage.getItem("selectedKeys"))];
}

watch(selectedKeys, () => {
    sessionStorage.setItem("selectedKeys", selectedKeys.value);
})

watch(collapsed, () => {
    if (collapsed.value) {
        logoText.value = 'Web';
        logoLabel.value.style.fontSize = `20px`;
        logoLabel.value.style.marginLeft = `20px`;
    } else {
        logoText.value = 'Web-ssh';
        logoLabel.value.style.fontSize = `24px`;
        logoLabel.value.style.marginLeft = `36px`;
    }
})

const logout = () => {
    Modal.confirm({
        title: "系统提示",
        icon: createVNode(ExclamationCircleOutlined),
        content: "确认",
        okText: "退出",
        cancelText: "取消",
        onOk() {
            localStorage.removeItem("token");
            sessionStorage.removeItem("token");
            sessionStorage.removeItem("selectedKeys");
            router.go('/login');
        }
    })
}

</script>

<style scoped>
.logo {
    display: flex;
    align-items: center;
    height: 50px;
    width: 100%;
    color: rgba(255, 255, 255, 0.8);
    background-color: rgba(255, 0, 255, 0.1);
    border-bottom: 2px solid rgba(255, 255, 255, 0.8);
    overflow: hidden;
}

.logo-label {
    margin-left: 36px;
    font-size: 28px;
    font-family: 'Times New Roman', Times, serif;
    font-style: italic;
    font-weight: bold;
    letter-spacing: 0.1em;
    white-space: nowrap;
}

.site-layout .site-layout-background {
    background: #fff;
}

[data-theme='dark'] .site-layout .site-layout-background {
    background: #141414;
}

.toolbar {
    margin-left: auto;
}
</style>