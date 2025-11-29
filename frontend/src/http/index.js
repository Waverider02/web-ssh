import axios from "axios";
import settings from "@/settings";
import { message } from 'ant-design-vue';
const http = axios.create({
    baseURL: settings.host,
    withCredentials: false,
})

http.interceptors.request.use((config) => {
    // console.log("http请求成功");
    return config;
}, (error) => {
    console.log("http请求失败");
    throw error;
});

http.interceptors.response.use((response) => {
    // console.log("http响应成功");
    // console.log('response:', response);
    return response;
}, async (error) => {
    if (error.response?.status == 401)
        console.log("token令牌失效");
    else if (error.response?.status == 400)
        console.log("提交信息有误");
    else {
        console.log("http响应失败");
    }
    throw error;
});

const getErrorMessage = (error) => {
    return error.response.data.message;
}

// JWT认证令牌
const getConfg = () => {
    let token = sessionStorage.token || localStorage.token;
    return {
        headers: {
            Authorization: `Bearer ${token}`,
        }
    };
}

const httpGET = async (url, show_massage = false) => {
    return http.get(url, getConfg()).then(response => {
        if (show_massage) {
            message.info('数据获取成功');
        }
        return response;
    }).catch(error => {
        console.log(getErrorMessage(error));
        message.error("数据获取失败");
        throw error;
    });
};

const httpPOST = async (url, form, show_massage = true) => {
    return http.post(url, form, getConfg()).then((response) => {
        if (show_massage) {
            message.info('数据上传成功');
        }
        return response;
    }).catch(error => {
        console.log(getErrorMessage(error));
        message.error("数据上传失败");
        throw error;
    })
}

const httpPUT = async (url, id, form, show_massage = true) => {
    return http.put(url + id + '/', form, getConfg()).then((response) => {
        if (show_massage) {
            message.info('数据更新成功');
        }
        return response;
    }).catch(error => {
        console.log(getErrorMessage(error));
        message.error("数据更新失败");
        throw error;
    })
}

const httpDELETE = async (url, id, show_massage = true) => {
    return http.delete(url + id + '/', getConfg()).then((response) => {
        if (show_massage) {
            message.info('数据删除成功');
        }
        return response;
    }).catch(error => {
        console.log(getErrorMessage(error));
        message.error("数据删除失败");
        throw error;
    })
}

/* 专用：下载文件（返回 blob 并触发浏览器保存） */
const httpFileDownload = async (url, form = {}, show_massage = true) => {
    return http
        .post(url, form, {
            ...getConfg(),          // 你原来的头、拦截器等
            responseType: 'blob',   // 关键：二进制
        })
        .then((response) => {
            // 创建临时地址并点击
            const blob = new Blob([response.data])
            const link = document.createElement('a')
            link.href = URL.createObjectURL(blob)
            link.download = form.filename
            link.style.display = 'none'
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
            URL.revokeObjectURL(link.href)

            if (show_massage) message.info('文件下载成功')
            return response
        })
        .catch((error) => {
            console.log(getErrorMessage(error))
            message.error('文件下载失败')
            throw error
        })
}

export default http;
export { httpGET, httpPOST, httpPUT, httpDELETE, httpFileDownload };
