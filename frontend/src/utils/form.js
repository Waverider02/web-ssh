import { reactive } from "vue";

const userForm = reactive({
    username: '',
    password: null,
    name: '',
    mobile: '',
    is_staff: false,
    is_active: false,
    is_superuser: false,
    hosts: [],
});

const categoryForm = reactive({
    name: ''
});

const detailsForm = {
    status: 1,
    id: '',
    name: '',
    category: 0, // 分类id
    category_name: '', // 分类名
    username: 'root',
    ip_addr: '',
    port: 0,
    connect_pwd: '',
    remark: '',
};

const loginForm = reactive({
    username: '',
    password: '',
    remember: false,
});

export { userForm, categoryForm, detailsForm, loginForm }