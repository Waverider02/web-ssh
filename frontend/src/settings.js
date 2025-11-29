// http服务端地址
const host = 'http://127.0.0.1:8000'; // 本机
// const host = 'http://10.6.94.252:8000'; // 局域网

export default { host }

// 项目api配置
export const api = {
    'token_obtain': host + '/token/obtain/', // 获取jwt认证token pair
    'token_refresh': host + '/token/refresh/', // 刷新token令牌
    'token_verify': host + '/token/verify/', // 令牌认证
    'users': host + '/user/users/', // 用户管理模型
    'hosts': host + '/host/hosts/', // 主机管理模型
    'category': host + '/host/category/', // 主机分类模型
}
