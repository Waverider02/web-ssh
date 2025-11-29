import { reactive, ref, computed } from "vue";

const listData = reactive({ value: [] })

const current = ref(1);

const pageSize = ref(5);

const pagination = computed(() => ({
    total: listData.value.length, // 数据长度
    current: current.value, // 当前页码
    pageSize: pageSize.value, // 每页项目数目
    showSizeChanger: true, // 每页显示的数据条数是否可编辑
    pageSizeOptions: ["5", "10", "15", "20"], // 每页显示的数据条数的可选值
    showTotal: (total) => `共有${total}数据`, // 分页中一共有多少条数据
}));

const getindex = (index) => { // 从当前分页id计算得到整个数据的id
    return (current.value - 1) * pageSize.value + index
}

const pageData = computed(() => ({
    value: listData.value.slice((current.value - 1) * pageSize.value, current.value * pageSize.value),
}));

const handlePageChange = (pag) => {
    current.value = pag.current;
    pageSize.value = pag.pageSize;
}

export { listData, pageData, pagination, handlePageChange, getindex, current, pageSize }