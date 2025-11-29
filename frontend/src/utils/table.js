
const categoryColumns = [
    { title: '分类名称', dataIndex: 'category_name', key: 'name', width: 240, },
    { title: '操作', key: 'action', width: 200, dataIndex: 'action', scopedSlots: { customRender: 'action' } }
];

const detailsColumns = [
    { title: '状态', dataIndex: 'update_status', key: 'update_status', width: 40, },
    { title: '类别', dataIndex: 'category_name', key: 'category_name', width: 160, },
    { title: '主机名称', dataIndex: 'name', key: 'name', width: 220, },
    { title: '账户', dataIndex: 'username', key: 'username', width: 120, },
    { title: '地址', dataIndex: 'ip_addr', key: 'ip_addr', width: 200, },
    { title: '端口', dataIndex: 'port', key: 'port', width: 150, elipsis: true, },
    { title: '连接密码', dataIndex: 'connect_pwd', key: 'connect_pwd', width: 220, },
    { title: '备注信息', dataIndex: 'remark', key: 'remark', elipsis: true, },
    { title: '操作', key: 'action', width: 200, dataIndex: 'action', scopedSlots: { customRender: 'action' } }
];

const userColumns = [
    { title: '用户名', dataIndex: 'username', key: 'username', width: 240, },
    { title: '手机号', dataIndex: 'mobile', key: 'mobile', width: 240, },
    { title: '激活状态', dataIndex: 'is_active', key: 'is_active', width: 150, },
    { title: '普通员工', dataIndex: 'is_staff', key: 'is_staff', width: 150, },
    { title: '超级管理员', dataIndex: 'is_superuser', key: 'is_superuser', width: 150, },
    { title: '操作', key: 'action', width: 200, dataIndex: 'action', scopedSlots: { customRender: 'action' } }
];

const userHostColumns = [
    { title: '用户名', dataIndex: 'username', key: 'username', width: 240, },
    { title: '手机号', dataIndex: 'mobile', key: 'mobile', width: 240, },
    { title: '激活状态', dataIndex: 'is_active', key: 'is_active', width: 150, },
    { title: '普通员工', dataIndex: 'is_staff', key: 'is_staff', width: 150, },
    { title: '超级管理员', dataIndex: 'is_superuser', key: 'is_superuser', width: 150, },
    { title: '主机列表', dataIndex: 'hosts', key: 'hosts', width: 150, },
];

const hostSimpleColumns = [
    { title: '主机名称', dataIndex: 'title' },
    { title: '主机分类', dataIndex: 'category' },
    { title: '主机地址', dataIndex: 'ip_addr' },
];

const dictColumns = [
    { title: '类型', dataIndex: 'perm', key: 'perm', width: 60, },
    { title: '名称', dataIndex: 'name', key: 'name', ellipsis: true, width: 140 },
    { title: '大小', dataIndex: 'size', key: 'size', width: 100, sorter: (a, b) => a.size - b.size },
    { title: '修改日期', dataIndex: 'date', key: 'date', width: 140 },
];
export { categoryColumns, detailsColumns, userColumns, userHostColumns, hostSimpleColumns, dictColumns }