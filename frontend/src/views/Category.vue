<template>
    <div class="host">
        <div class="add_host" style="margin: 15px;">
            <a-button @click="createItem" type="primary">
                <plus-outlined />新建
            </a-button>
        </div>
    </div>
    <a-table :columns="categoryColumns" :data-source="pageData.value" :pagination="pagination"
        @change="handlePageChange">
        <template #bodyCell="{ column, index }">
            <template v-if="column.key === 'action'">
                <a-popconfirm v-if="pageData.value.length" title="Sure to delete?" @confirm="deleteItem(index)">
                    <a>Delete</a>
                </a-popconfirm>
                <a @click="modifyItem(index)" style="margin-left:10px">Modify</a>
            </template>
            <template v-else>
                <a-input readonly v-model:value="pageData.value[index][column.key]" />
            </template>
        </template>
    </a-table>
    <a-modal v-model:open="open" title="用户信息" @ok="submitOk">
        <a-form :label-col="{ width: '150px' }" :wrapper-col="{ span: 14 }">
            <a-form-item label="分类名称">
                <a-input v-model:value="categoryForm.name" />
            </a-form-item>
        </a-form>
    </a-modal>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { httpGET, httpPOST, httpPUT, httpDELETE } from '@/http';
import { listData, pageData, pagination, handlePageChange, getindex, current, pageSize } from '@/utils/paginatior'
import { categoryColumns } from '@/utils/table';
import { categoryForm } from '@/utils/form';
import { assignSame, clearItem } from '@/utils/copy';
import { api } from '@/settings';

const open = ref(false);

const operation = ref(null);

const modifyid = ref(null);

const getCategory = () => {
    httpGET(api.category).then(response => { listData.value = response.data });
};

const deleteItem = (index) => {
    httpDELETE(api.category, listData.value[getindex(index)].id).then(() => {
        getCategory();
    });
};

const createItem = () => {
    clearItem(categoryForm);
    operation.value = "create";
    open.value = true;
};

const modifyItem = (index) => {
    clearItem(categoryForm);
    assignSame(listData.value[getindex(index)], categoryForm);
    operation.value = "modify";
    open.value = true;
    modifyid.value = getindex(index);
}

const submitOk = () => {
    if (operation.value == "create") {
        httpPOST(api.category, categoryForm).then(() => {
            getCategory();
            open.value = false;
        })
    }
    else if (operation.value == "modify") {
        httpPUT(api.category, listData.value[modifyid.value].id, categoryForm).then(() => {
            getCategory();
            open.value = false;
        })
    }
}

onMounted(() => {
    current.value = 1;
    pageSize.value = 5;
    getCategory();
})

</script>
