<template>
    <a-button type="primary" @click="showDrawer">文件管理器</a-button>
    <a-drawer v-model:open="open" class="custom-class" root-class-name="root-class-name" :root-style="{ color: 'blue' }"
        style="color: gray" title="文件管理器" placement="right" width="600">
        <div style="margin-bottom: 20px;color: black;">
            <a-space :size="20" style="line-height: 16px; font-size: 16px;">
                <a-button @click="go_back" type="primary">上一级目录</a-button>
                <a-button @click="new_folder" type="primary">新建文件夹</a-button>
                <a-button @click="upload_file" type="primary">上传文件</a-button>
            </a-space>
        </div>
        <a-divider></a-divider>
        <div style="display: flex; justify-content: space-between;">
            <span>
                <HomeOutlined /> {{ path }}
            </span>
            <span>
                <a-switch v-model:checked="hide" @change="dir(path)" />
            </span>
        </div>
        <a-table id="mytable" :columns="dictColumns" :data-source="dict" :customRow="customRow">
            <template #bodyCell="{ column, index, text }">
                <template v-if="column.key == 'perm'">
                    <component :is="iconMap[text[0]] || FileOutlined" style="font-size: 16px; color: #1890ff;" />
                </template>
                <template v-else>
                    {{ text }}
                </template>
            </template>
        </a-table>
        <!-- 挂载到draw的父节点中 -->
        <a-dropdown v-model:open="menuVisible" :trigger="['contextmenu']"
            :getPopupContainer="trigger => trigger.parentNode">
            <!-- 空触发器：不占空间，只提供右键事件 -->
            <div ref=menuDom class="menu" style="position:fixed; width: 1px; height: 1px;"></div>
            <template #overlay>
                <a-menu mode="vertical" @click="onMenuClick">
                    <a-menu-item id="item1" key="open">打开</a-menu-item>
                    <a-menu-item id="item2" key="download">下载</a-menu-item>
                    <a-menu-item id="item3" key="delete">删除</a-menu-item>
                </a-menu>
            </template>
        </a-dropdown>
        <a-modal v-model:open="setNameVisible" title="名称" @ok="setNameOk(path)">
            设置名称: <a-input v-model:value="setName"></a-input>
        </a-modal>
        <a-modal v-model:open="UploadOpen" title="上传文件" @ok="UploadOk" ok-text="submit">
            <FileUpload v-model:fileList="fileList"></FileUpload>
        </a-modal>
    </a-drawer>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import { httpPOST, httpFileDownload } from '@/http';
import { parseLs, decodePerm } from '@/utils/list';
import { dictColumns } from '@/utils/table';
import { FolderOutlined, FileOutlined, LinkOutlined, HomeOutlined } from '@ant-design/icons-vue';
import { Modal, message } from 'ant-design-vue';
import FileUpload from '@/components/FileUpload.vue';

const props = defineProps({ dev_id: Number });

const open = ref(false);
const setNameVisible = ref(false);
const showDrawer = () => {
    if (props.dev_id) {
        open.value = true;
        refresh(path.value);
    } else {
        message.error("请先选择主机");
    }
};

const customRow = (record) => {
    return {
        class: 'custom-row',
        onDblclick: (event) => {
            go_on(record);
        },
        onContextmenu: (e) => {
            e.preventDefault(); // 阻止默认右键事件
            if (!menuVisible.value) {
                currentRow = record;
                showContextmenu(e);
            }
        },
        style: {
            userSelect: 'none',
            cursor: 'default',
        },
    };
};

const iconMap = {
    'd': FolderOutlined,
    '-': FileOutlined,
    'l': LinkOutlined,
};

const path = ref('./');
const hide = ref(true);
const dict = ref([]);

const get_back_path = () => {
    let current_path = path.value;
    let back_path = current_path.split('/').slice(0, -1).join('/');
    return back_path ? back_path : '/';
}

const get_on_path = (folder_name) => {
    let on_path = path.value + '/' + folder_name;
    return on_path.replace(/\/+/g, '/');
}

const go_back = () => {
    dir(get_back_path());
};

const go_on = (folder) => {
    const { name, perm } = folder; // 对象解构赋值
    let folder_type = decodePerm(perm).type;
    if (folder_type == 'dir' || folder_type == 'link') {
        dir(get_on_path(name));
        menuVisible.value = false;
    }
};

const pwd = async (current_path) => {
    let form_data = { cmd: 'pwd', args: [] };
    return httpPOST(`/host/${props.dev_id}/file/?path=${current_path}`, form_data, false).then(response => {
        if (!response.data.code) {
            path.value = response.data.msg.replace(/\n/g, '');
        }
        return response;
    }).catch(error => {
        throw error;
    });
};

const dir = async (current_path) => {
    let form_data = { cmd: 'ls', args: hide.value ? ['-l'] : ['-la'] };
    return httpPOST(`/host/${props.dev_id}/file/?path=${current_path}`, form_data, false).then(response => {
        if (!response.data.code) {
            let raw = response.data.msg;
            path.value = current_path;
            dict.value = parseLs(raw);
        }
        return response;
    }).catch(error => {
        throw error;
    });
};

const setName = ref('');

const new_folder = () => {
    setNameVisible.value = true;
}

const setNameOk = async (current_path) => {
    let form_data = { cmd: 'mkdir', args: [`${setName.value}`] };
    return httpPOST(`/host/${props.dev_id}/file/?path=${current_path}`, form_data, false).then(response => {
        dir(path.value);
        setNameVisible.value = false;
        return response;
    }).catch(error => {
        throw error;
    });
}

const del_it = async (folder) => {
    const { name } = folder;
    return new Promise((resolve, reject) => {
        Modal.confirm({
            title: '确认删除',
            content: `你确定要删除 “${name}” 吗？此操作不可恢复！`,
            okText: '确定',
            okType: 'danger',
            cancelText: '取消',
            onOk: async () => {
                const form_data = { cmd: 'rm', args: ['-rf', `"${name}"`] };
                try {
                    const res = await httpPOST(
                        `/host/${props.dev_id}/file/?path=${path.value}`,
                        form_data,
                        false
                    );
                    message.success(`已删除 ${name}`);
                    resolve(res);
                    await dir(path.value);
                } catch (e) {
                    message.error(`删除失败：${e.message}`);
                    reject(e);
                }
            },
            onCancel: () => {
                message.info('已取消删除');
                resolve(false);
            }
        });
    });
};

const fileList = ref([]);
const UploadOpen = ref(false);

const upload_file = () => {
    UploadOpen.value = true;
}

async function UploadOk() {
    if (fileList.value.length) {
        fileList.value.forEach(file => {
            let form_data = new FormData()
            form_data.append('file', file)
            form_data.append('path', path.value)
            form_data.append('filename', file.name)
            httpPOST(`/host/${props.dev_id}/upload/?path=${path.value}`, form_data, false).then(async () => {
                await dir(path.value);
                message.info('上传成功');
            }).catch((e) => {
                message.error('上传失败');
            }
            );
        })
    }
}

const refresh = (current_path) => {
    pwd(current_path).then((response) => {
        if (!response.data.code) {
            dir(path.value);
        }
    });
};

const menuVisible = ref(false);
const menuDom = ref();
let currentRow = null;
let highlightTr = null;

const showContextmenu = ((e) => {
    if (highlightTr) {
        highlightTr.classList.remove('hightlight-row');
    }
    highlightTr = e.currentTarget;
    highlightTr.classList.add('highlight-row');
    nextTick(() => { // 等待DOM挂载完成,定位到鼠标
        menuDom.value.style.position = 'fixed';
        menuDom.value.style.left = `${e.clientX + Math.random() * 2}px`;
        menuDom.value.style.top = `${e.clientY + Math.random() * 2}px`;
        menuVisible.value = true;
    });
});

function onMenuClick({ key }) {
    menuVisible.value = false;
    if (key == 'open') {
        go_on(currentRow);
    } else if (key == 'delete') {
        del_it(currentRow);
    } else if (key == 'download') {
        let form_data = { path: path.value, filename: currentRow.name };
        httpFileDownload(`/host/${props.dev_id}/download/?path=${path.value}`, form_data, false).then(async () => {
            message.info('下载成功');
        }).catch((e) => {
            message.error('下载失败');
        })
    }
}

watch(menuVisible, (val) => {
    if (!val && highlightTr) {
        highlightTr.classList.remove('highlight-row');
        highlightTr = null;
    }
});


</script>

<style scoped>
::v-deep(#mytable) {
    line-height: 0.5;
}

::v-deep(tr.custom-row:hover) td,
::v-deep(tr.custom-row:hover) {
    background-color: #fff1b8 !important;
    transition: background-color 0.1s ease-in-out;
}

::v-deep(tr.highlight-row) td,
::v-deep(tr.highlight-row) {
    background-color: #ffd591 !important;
}

::v-deep(#item1:hover),
::v-deep(#item2:hover),
::v-deep(#item3:hover) {
    background-color: #ffd591;
}
</style>
