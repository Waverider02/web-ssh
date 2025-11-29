<template>
    <div>
        <a-button type="primary" @click="selectUser">选择用户</a-button>
        <a-tag>当前选择的用户</a-tag>
        <br>
        <a-table id="mytable" :columns="userHostColumns" :data-source="pageData.value" :pagination="pagination"
            @change="handlePageChange">
            <template #bodyCell="{ column, index }">
                <template v-if="column.key == 'username' || column.key == 'mobile'">
                    <a-input readonly v-model:value="pageData.value[index][column.key]" />
                </template>
                <template v-else-if="column.key == 'hosts'">
                    <a-list size="large" bordered :data-source="getHostNameList(pageData.value[index][column.key])"
                        style="height:100px;overflow-y:auto;">
                        <template #renderItem="{ item }">
                            <a-list-item style="height:20px;">{{ item }}</a-list-item>
                        </template>
                    </a-list>
                </template>
                <template v-else>
                    <a-switch disabled v-model:checked="pageData.value[index][column.key]"></a-switch>
                </template>
            </template>
        </a-table>
        <a-button type="primary" @click="submitUser">批量分配</a-button>
        <a-tag>主机资源分配</a-tag>
        <a-transfer v-model:target-keys="targetKeys" :data-source="mockData" :disabled="false" :show-search="true"
            :filter-option="(inputValue, item) => item.title.indexOf(inputValue) !== -1" :show-select-all="true"
            @change="onChange">
            <template #children="{ direction, filteredItems, selectedKeys,
                disabled: listDisabled, onItemSelectAll, onItemSelect, }">
                <a-table :row-selection="getRowSelection({
                    disabled: listDisabled,
                    selectedKeys, onItemSelectAll, onItemSelect,
                })" :columns="direction === 'left' ? leftColumns : rightColumns" :data-source="filteredItems"
                    size="small" :style="{ pointerEvents: listDisabled ? 'none' : null }" :custom-row="({ key, disabled: itemDisabled }) => ({
                        onClick: () => {
                            if (itemDisabled || listDisabled) return;
                            onItemSelect(key, !selectedKeys.includes(key));
                        },
                    })" />
            </template>
        </a-transfer>
        <a-modal v-model:open="open" title="用户信息" @ok="selectOk">
            <div style="display: flex; justify-content: space-between;">
                <a-checkbox v-model:checked="state.checkAll" :indeterminate="state.indeterminate"
                    @change="onCheckAllChange">
                    全选
                </a-checkbox>
                <a-input-search v-model:value="searchValue" placeholder="input search text" style="width: 200px"
                    @search="onSearch" />
            </div>
            <a-divider style="margin-top: 10px;" />
            <div style="height:100px;overflow-y:auto;">
                <a-checkbox-group v-model:value="state.checkedList" :options="userOptions" />
            </div>
        </a-modal>
    </div>
</template>
<script setup>
import { ref, reactive, watch, onMounted } from 'vue';
import { userHostColumns, hostSimpleColumns } from '@/utils/table';
import { listData, pageData, pagination, handlePageChange, current, pageSize } from '@/utils/paginatior';
import { httpGET, httpPUT } from '@/http';
import { userForm } from '@/utils/form';
import { assignSame, union } from '@/utils/copy';
import { findSimilarStrings } from '@/utils/search';
import { api } from '@/settings';

let user = ref([]);
let category = ref([]);
let hosts = ref([]);
const open = ref(false);
const mockData = ref([]);
const targetKeys = ref([]);
const leftColumns = ref(hostSimpleColumns);
const rightColumns = ref(hostSimpleColumns);
const rightKeys = ref([]);
const onChange = nextTargetKeys => {
    rightKeys.value = nextTargetKeys;
};
const getRowSelection = ({ disabled, selectedKeys, onItemSelectAll, onItemSelect }) => {
    return {
        getCheckboxProps: item => ({
            disabled: disabled || item.disabled,
        }),
        onSelectAll(selected, selectedRows) {
            const treeSelectedKeys = selectedRows.filter(item => !item.disabled).map(({ key }) => key);
            onItemSelectAll(treeSelectedKeys, selected);
        },
        onSelect({ key }, selected) {
            onItemSelect(key, selected);
        },
        selectedRowKeys: selectedKeys,
    };
};

// 选择用户
const selectUser = () => {
    getUser();
    open.value = true;
};
const selectOk = () => {
    current.value = 1;
    open.value = false;
    user.value = user.value.filter(item => state.checkedList.includes(item["username"]));
    listData.value = user.value;
    resetMock();
};

// 主机属性信息
const resetMock = () => {
    mockData.value = [];
    for (let i = 0; i < hosts.value.length; i++) {
        mockData.value.push({
            key: String(hosts.value[i].id),
            title: hosts.value[i].name,
            category: getCategoryName(hosts.value[i].category),
            ip_addr: `${hosts.value[i].username}@${hosts.value[i].ip_addr}:${hosts.value[i].port}`,
        });
    }
};

// 从服务端获取用户信息
const getUser = async () => {
    return httpGET(api.users).then(response => {
        let data = response.data;
        user.value = data;
        userTotalOptions.value = data.map(item => item["username"]);
        userOptions.value = userTotalOptions.value;
    });
};

const getCategory = () => {
    httpGET(api.category).then(response => { category.value = response.data; });
};

const getDetails = () => {
    httpGET(api.hosts).then(response => { hosts.value = response.data });
};

const getHostNameList = (id_list) => {
    return id_list?.map(id => hosts.value.find(item => item.id === id)?.name)
        .filter(Boolean);
};

const getCategoryName = (id) => {
    return category.value.filter(item => item.id === id)[0]?.name;
};

const submitUser = () => {
    for (let i = 0; i < listData.value.length; i++) {
        assignSame(user.value[i], userForm);
        let payload = userForm;
        payload.hosts = rightKeys.value;
        delete payload.password;
        httpPUT(api.users, user.value[i].id, payload).then(() => {
            getUser().then(() => {
                user.value = user.value.filter(item => state.checkedList.includes(item["username"]));
                listData.value = user.value;
            });
        })
    }
};

const userOptions = ref();
const userTotalOptions = ref();
const searchValue = ref();
const state = reactive({ checkedList: [], checkedAllList: [], checkAll: false, indeterminate: true, });

const onCheckAllChange = e => {
    Object.assign(state, {
        checkedList: e.target.checked ? userOptions.value : [],
        indeterminate: false,
    });
};

const onSearch = () => {
    let val = state.checkedList;
    state.checkedAllList = union(state.checkedAllList, val)
    state.indeterminate = !!val.length && val.length < userOptions.value.length;
    state.checkAll = val.length === userOptions.value.length;
    if (!searchValue.value) {
        userOptions.value = userTotalOptions.value;
    } else {
        userOptions.value = findSimilarStrings(searchValue.value, userTotalOptions.value);
    }
    state.checkedList = state.checkedAllList;
};

watch(
    () => state.checkedList,
    val => {
        state.indeterminate = !!val.length && val.length < userOptions.value.length;
        state.checkAll = val.length === userOptions.value.length;
    },
);

onMounted(() => {
    current.value = 1;
    pageSize.value = 5;
    listData.value = [];
    getUser();
    getCategory();
    getDetails();
});

</script>

<style scoped>
.ant-tag {
    cursor: context-menu;
    width: 100%;
    height: 40px;
    line-height: 40px;
    text-align: center;
    letter-spacing: 5px;
    display: block;
    margin: 10px auto;
    font-size: 16px;
    font-weight: bold;
}

::v-deep(#mytable) {
    margin-top: -20px;
}
</style>