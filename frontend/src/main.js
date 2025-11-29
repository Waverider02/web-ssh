// 项目启动js脚本
import { createApp } from 'vue'; // 构造函数
import './style.css'; // 全局样式
import App from './App.vue'; // 入口组件
import router from './router/index.js'; // 路由
import Antd from 'ant-design-vue'; // Antd组件插件
import * as Icons from '@ant-design/icons-vue' // Antd图标
import 'ant-design-vue/dist/reset.css'; // Antd图标样式

const app = createApp(App); // 创建应用实例
app.use(router); // 绑定路由
app.use(Antd); // 绑定Antd组件库
app.mount('#app'); // 绑定app

app.config.globalProperties.$icons = Icons
for (const key in Icons) {
    app.component(key, Icons[key]);
}
