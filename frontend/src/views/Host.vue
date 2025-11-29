<template>
    <div class="add_host" style="margin: 15px;">
        <a-space :size="20">
            <a-button @click="createItem" type="primary">
                <plus-outlined />新建
            </a-button>
            <a-button @click="updateAll" type="primary">
                <cloud-upload-outlined />更新全部数据
            </a-button>
        </a-space>
    </div>
    <a-table :columns="detailsColumns" :data-source="pageData.value" :pagination="pagination"
        @change="handlePageChange">
        <template #bodyCell="{ column, index }">
            <template v-if="column.key === 'action'">
                <a-popconfirm v-if="pageData.value.length" title="Sure to delete?" @confirm="deleteItem(index)">
                    <a>Delete</a>
                </a-popconfirm>
                <a @click="insertItem(index)" style="margin-left:10px">Insert</a>
                <a @click="updateItem(index)" style="margin-left:10px">Update</a>
            </template>
            <template v-else-if="column.key === 'update_status'">
                <!-- 1:正常同步数据 -->
                <a-button v-if="pageData.value[index].update_status == 1" style="background-color: green;"></a-button>
                <!-- 2:数据新建,但没有同步数据到数据库 -->
                <a-button v-else-if="pageData.value[index].update_status == 2"
                    style="background-color: red;"></a-button>
                <!-- 3:数据有更改,但没有同步数据到数据库 -->
                <a-button v-else-if="pageData.value[index].update_status == 3"
                    style="background-color: yellow;"></a-button>
            </template>
            <template v-else-if="column.key === `category_name`">
                <a-dropdown :trigger="['click']">
                    <a-button>
                        {{ pageData.value[index].category_name }}
                        <DownOutlined />
                    </a-button>
                    <template #overlay>
                        <a-menu>
                            <a-menu-item @click="onClickSelect(value.name, index)" v-for="value in categoryList"
                                :key="value.id">
                                {{ value.name }}
                            </a-menu-item>
                        </a-menu>
                    </template>
                </a-dropdown>
            </template>
            <template v-else>
                <div class="editable-cell">
                    <a-input-password v-if="column.key === `connect_pwd`" @change="onChange(index)"
                        v-model:value="pageData.value[index][column.key]" />
                    <a-input v-else @change="onChange(index)" v-model:value="pageData.value[index][column.key]" />
                </div>
            </template>
        </template>
    </a-table>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { httpGET, httpPOST, httpPUT, httpDELETE } from '@/http';
import { listData, pageData, pagination, handlePageChange, getindex, current, pageSize } from '@/utils/paginatior'
import { detailsColumns } from '@/utils/table';
import { detailsForm } from '@/utils/form';
import { api } from '@/settings';
import { assignSame, clearItem } from '@/utils/copy';

const categoryList = ref([]);

const getDetails = () => {
    httpGET(api.hosts).then(response => {
        let data = response.data;
        data.forEach((item) => { item.update_status = 1 });
        listData.value = data;
    });
};

const getCategory = () => {
    httpGET(api.category).then(response => { categoryList.value = response.data; });
};

const onClickSelect = (key, index) => {
    index = getindex(index);
    listData.value[index].category = categoryList.value.find(item => item.name === key).id;
    listData.value[index].category_name = key;
    if (listData.value[index].update_status == 1) {
        listData.value[index].update_status = 3;
    }
}

const updateItem = (index) => {
    index = getindex(index);
    let payload = assignSame(listData.value[index], detailsForm);
    delete payload['update_status'];
    delete payload['id'];
    if (listData.value[index].update_status != 1) {
        if (listData.value[index].update_status == 2) {
            httpPOST(api.hosts, payload).then(() => { listData.value[index].update_status = 1 })
        }
        else if (listData.value[index].update_status == 3) {
            httpPUT(api.hosts, listData.value[index].id, payload).then(() => { listData.value[index].update_status = 1 })
        }
    }
}

const updateAll = () => {
    for (let index = 0; index < listData.value.length; index++) {
        updateItem(index);
    }
}

const deleteItem = index => {
    index = getindex(index);
    if (listData.value[index].update_status == 2) { // 如果数据库没有该数据,直接删除列表
        listData.value.splice(index, 1);
    } else {
        httpDELETE(api.hosts, listData.value[index].id).then(() => { listData.value.splice(index, 1); })
    }
};

const onChange = (index) => {
    index = getindex(index);
    if (listData.value[index].update_status == 1) {
        listData.value[index].update_status = 3;
    }
}

const count = computed(() =>
    listData.value?.length
        ? Math.max(...listData.value.map((item) => parseInt(item.id)))
        : 0
);

const createItem = () => {
    clearItem(detailsForm);
    detailsForm.id = `${count.value + 1}`;
    detailsForm.update_status = 2;
    listData.value.splice(0, 0, structuredClone(detailsForm));
};

const insertItem = index => {
    clearItem(detailsForm);
    index = getindex(index);
    detailsForm.id = `${count.value + 1}`;
    detailsForm.update_status = 2;
    listData.value.splice(index + 1, 0, structuredClone(detailsForm));
};

onMounted(() => {
    current.value = 1;
    pageSize.value = 5;
    getDetails();
    getCategory();
})

</script>
