import { jwtDecode } from "jwt-decode";
import { httpGET } from "@/http";
import { api } from "@/settings";

// token:base64url 解码
function base64urlDecode(str) {
    str = str.split('.')[1];
    str = str.replace(/-/g, '+').replace(/_/g, '/');
    while (str.length % 4) str += '=';
    return atob(str);
}

const refreshToken = () => {
    let refresh = sessionStorage.refresh || localStorage.refresh || '';
    return httpPOST(api.token_refresh, { refresh: refresh }).then((response) => {
        if (localStorage.token) {
            localStorage.token = response.data.access;
        } else {
            sessionStorage.token = response.data.access;
        }
        return response;
    }).catch(error => { return error });
}

const getUserId = () => {
    let token = sessionStorage.token || localStorage.token;
    if (token) {
        const payload = jwtDecode(token); // 解码 payload
        return payload.user_id; // SimpleJWT 默认字段
    }
}

const getUserInfo = async () => {
    return httpGET(`${api.users}${getUserId()}`).then(response => {
        return response;
    }).catch(error => { return error });
}

export { base64urlDecode, getUserId, getUserInfo, refreshToken };