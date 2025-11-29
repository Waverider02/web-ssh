import { reactive } from "vue";

const base_list = reactive([ // 动态加载图标,图标需采用大驼峰写法 bug-outlined=>BugOutlined
    { key: 1, name: "展示大厅", icon: "HomeOutlined", link: "home" },
    { key: 2, name: "资产管理", icon: "BankOutlined", link: "host" },
    { key: 3, name: "资源分类", icon: "PartitionOutlined", link: "category" },
    { key: 4, name: "用户管理", icon: "UserOutlined", link: "user" },
    { key: 5, name: "资源分配", icon: "SwapOutlined", link: "allocation" },
    { key: 6, name: "测试页面", icon: "ExperimentOutlined", link: "test" },
]);

/**
 * 字节 → 可读单位
 * @param {number} bytes
 * @returns {string}  例 1.45 GB | 300 KB | 0 B
 */
function formatSize(bytes) {
    if (bytes == 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    const val = (bytes / Math.pow(k, i)).toFixed(i > 1 ? 2 : 0)
    return `${val} ${sizes[i]}`
}

// 正则：权限 硬链接 用户 组 大小 月 日 时间 名称( -> 目标)?
const LS_RE = /^([-\wlrwxstST+]{10})\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)\s+(\w{3})\s+(\d{1,2})\s+([\d:]+)\s+(.+?)(?:\s+->\s+(.*))?$/;

function parseLs(text) { // 将ls -l返回的路径字符串整理为列表
    return text
        .split('\n')
        .map(l => l.trim())
        .filter(l => l && !l.startsWith('total'))
        .reduce((arr, line) => {
            const m = line.match(LS_RE);
            if (!m) return arr;
            const [, perm, nlink, user, group, size, month, day, time, name, target] = m;
            if (name !== '.' && name !== '..') {
                arr.push({
                    perm,
                    nlink: Number(nlink),
                    user,
                    group,
                    size: formatSize(size),
                    date: `${month} ${day} ${time}`,
                    name,
                    target: target || null
                });
            }
            return arr;
        }, []);
}

function decodePerm(perm) { // 解析perm参数
    const typeMap = {
        '-': 'file',
        d: 'dir',
        l: 'link',
        c: 'char',
        b: 'block',
        p: 'pipe',
        s: 'socket',
        D: 'door',
    };
    return {
        type: typeMap[perm[0]] || 'unknown',
        owner: perm.slice(1, 4),
        group: perm.slice(4, 7),
        other: perm.slice(7, 10),
    };
}

export { base_list, parseLs, decodePerm }