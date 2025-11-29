<template>
    <div style="margin-bottom: 10px;">
        <a-space :size="20">
            <a-dropdown :trigger="['click']">
                <template #overlay>
                    <a-menu>
                        <a-menu-item @click="onClickSelect(id)" v-for="id in host_ids" :key="id">
                            {{ getHostName(id) }}
                        </a-menu-item>
                    </a-menu>
                </template>
                <a-button style="min-width: 100px;">
                    {{ selectedHost }}
                    <DownOutlined />
                </a-button>
            </a-dropdown>
            <a-button @click="linkToHost" type="primary">
                <CloudServerOutlined />连接主机
            </a-button>
            <FileManager :dev_id="selectedHostId"></FileManager>
        </a-space>
    </div>
    <div class="wrapper">
        <div ref="terminalEl" class="terminal"></div>
    </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { Terminal } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'
import 'xterm/css/xterm.css'
import settings from '@/settings'
import { getUserInfo } from '@/utils/token'
import { httpGET } from '@/http'
import { api } from '@/settings'
import FileManager from '@/components/FileManager.vue'
import { message } from 'ant-design-vue'

let term;
let fitAddon;
let socket;

const terminalEl = ref(null);
const selectedHost = ref("请选择主机");
const selectedHostId = ref();
const host = ref();
const host_ids = ref([]);

const getHostName = (id) => {
    return host.value.filter(item => item.id === id)[0]?.name;
};

const getDetails = () => {
    httpGET(api.hosts).then(response => { host.value = response.data });
};

const getHostIds = () => {
    getUserInfo().then(response => {
        host_ids.value = response.data.hosts;
    });
};

const onClickSelect = (key) => {
    selectedHostId.value = key;
    selectedHost.value = getHostName(key);
};

const linkToHost = () => {
    if (selectedHostId.value) {
        socket?.close();
        initSocket(selectedHostId.value);
    } else {
        message.error("请先选择主机");
    }
};

/* ---------- 1. 创建 WebSocket ---------- */
function initSocket(host_id) {
    let token = sessionStorage.token || localStorage.token;
    socket = new WebSocket(`${settings.host}/ws/ssh/${host_id}/`, ['jwt', token]);
    socket.onopen = () => term.writeln('\r\n[connected]\r\n');
    socket.onmessage = ({ data }) => term.write(atob(data));
    socket.onclose = () => term.writeln('\r\n[disconnected]\r\n');
    socket.onerror = () => term.writeln('\r\n[error]\r\n');
}

/* ---------- 2. 创建 xterm ---------- */
function initTerm() {
    term = new Terminal({
        fontSize: 14,
        cursorBlink: true,
        theme: { background: '#181d28', foreground: '#ECECEC' }
    })

    fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    term.open(terminalEl.value);
    fitAddon.fit();

    let cmd = '';
    term.onData(raw => {
        const code = raw.charCodeAt(0);
        if (code === 13) { // 回车Enter
            term.writeln('');
            if (socket?.readyState === WebSocket.OPEN) {
                socket.send(btoa(cmd + '\n'));
            }
            cmd = '';
            return
        }
        else if (code === 127) { // 退格BackSpace
            if (cmd.length > 0) {
                cmd = cmd.slice(0, -1);
                term.write('\b \b'); // 光标回退
            }
            return
        }
        else {
            term.write(raw); // 写入term以显示
            cmd += raw; // 拼接指令
        }
    })
}

onMounted(() => {
    initTerm();
    getHostIds();
    getDetails();
});

onBeforeUnmount(() => {
    socket?.close();
    term?.dispose();
});
</script>

<style scoped>
.wrapper {
    width: 80%;
    height: calc(80vh - 50px);
    padding: 12px;
    box-sizing: border-box;
    background: #181d28;
    border-radius: 4px;
    overflow: hidden;
}

::v-deep(.terminal) {
    height: calc(80vh - 74px);
}
</style>