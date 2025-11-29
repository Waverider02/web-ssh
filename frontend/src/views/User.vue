<template>
    <div class="host">
        <div class="add_host" style="margin: 15px;">
            <a-button @click="createItem" type="primary">
                <plus-outlined />新建
            </a-button>
        </div>
    </div>
    <a-table id="mytable" :columns="userColumns" :data-source="pageData.value" :pagination="pagination"
        @change="handlePageChange">
        <template #bodyCell="{ column, index }">
            <template v-if="column.key === 'action'">
                <a-popconfirm v-if="pageData.value.length" title="Sure to delete?" @confirm="deleteItem(index)">
                    <a>Delete</a>
                </a-popconfirm>
                <a @click="modifyItem(index)" style="margin-left:10px">Modify</a>
            </template>
            <template v-else-if="column.key == 'username' || column.key == 'mobile'">
                <a-input readonly v-model:value="pageData.value[index][column.key]" />
            </template>
            <template v-else>
                <a-switch disabled v-model:checked="pageData.value[index][column.key]"></a-switch>
            </template>
        </template>
    </a-table>
    <a-modal v-model:open="open" title="用户信息" @ok="submitOk">
        <a-form :label-col="{ width: '150px' }" :wrapper-col="{ span: 14 }">
            <a-form-item label="用户名">
                <a-input v-model:value="userForm.username" />
            </a-form-item>
            <a-form-item label="密码">
                <a-input v-model:value="userForm.password" />
            </a-form-item>
            <a-form-item label="手机号">
                <a-input v-model:value="userForm.mobile" />
            </a-form-item>
            <a-form-item label="激活状态">
                <a-switch v-model:checked="userForm.is_active" />
            </a-form-item>
            <a-form-item label="员工">
                <a-switch v-model:checked="userForm.is_staff" />
            </a-form-item>
            <a-form-item label="超级管理员">
                <a-switch v-model:checked="userForm.is_superuser" />
            </a-form-item>
        </a-form>
    </a-modal>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { httpGET, httpPOST, httpPUT, httpDELETE } from '@/http';
import { listData, pageData, pagination, handlePageChange, getindex, current, pageSize } from '@/utils/paginatior'
import { userColumns } from '@/utils/table';
import { userForm } from '@/utils/form';
import { assignSame, clearItem } from '@/utils/copy';
import { api } from '@/settings';

const open = ref(false);

const operation = ref(null);

const modifyid = ref(null);

const getUser = () => {
    httpGET(api.users).then(response => { listData.value = response.data });
};

const deleteItem = (index) => {
    httpDELETE(api.users, listData.value[getindex(index)].id).then(() => {
        getUser();
    });
};

const createItem = () => {
    clearItem(userForm);
    operation.value = "create";
    open.value = true;
};

const modifyItem = (index) => {
    clearItem(userForm);
    assignSame(listData.value[getindex(index)], userForm);
    operation.value = "modify";
    open.value = true;
    modifyid.value = getindex(index);
}

const submitOk = () => {
    if (operation.value == "create") {
        httpPOST(api.users, userForm).then(() => {
            getUser();
            open.value = false;
        })
    }
    else if (operation.value == "modify") {
        httpPUT(api.users, listData.value[modifyid.value].id, userForm).then(() => {
            console.log(userForm)
            getUser();
            open.value = false;
        })
    }
}

onMounted(() => {
    current.value = 1;
    pageSize.value = 5;
    getUser();
})

</script>
