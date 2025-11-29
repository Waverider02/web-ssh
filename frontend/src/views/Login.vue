<template>
    <div class="container" id="bg">
        <div class="center-box">
            <a-form :model="loginForm" name="basic" :label-col="{ span: 8 }" :wrapper-col="{ span: 16 }"
                autocomplete="off" :rules="rules" @finish="onFinish">
                <a-form-item label="Username" name="username">
                    <a-input v-model:value="loginForm.username" placeholder="用户名或者手机号">
                        <template #prefix>
                            <UserOutlined class="site-form-item-icon" />
                        </template>
                    </a-input>
                </a-form-item>

                <a-form-item label="Password" name="password">
                    <a-input-password v-model:value="loginForm.password" placeholder="请输入密码">
                        <template #prefix>
                            <LockOutlined class="site-form-item-icon" />
                        </template>
                    </a-input-password>
                </a-form-item>

                <a-form-item>
                    <a-form-item name="remember">
                        <a-checkbox v-model:checked="loginForm.remember">Remember me</a-checkbox>
                    </a-form-item>
                    <a class="login-form-forgot" href="">Forgot password</a>
                </a-form-item>

                <a-form-item>
                    <a-button type="primary" html-type="submit" class="login-form-button">
                        login
                    </a-button>
                    <br>
                    <span class="register-now">
                        Or
                        <a href="">register now!</a>
                    </span>
                </a-form-item>
            </a-form>
        </div>
    </div>
</template>


<script setup>
import { Modal } from 'ant-design-vue';
import http from '@/http';
import { api } from '@/settings';
import { loginForm } from '@/utils/form';
import router from '@/router';

if (localStorage.getItem("username")) {
    loginForm.username = localStorage.getItem("username")
}

const onFinish = () => {
    http.post(api.token_obtain, {
        username: loginForm.username,
        password: loginForm.password,
    }).then(response => {
        localStorage.setItem("username", loginForm.username);
        if (loginForm.remember) { // 记录登陆状态
            localStorage.setItem("token", response.data.access);
        } else {
            sessionStorage.setItem("token", response.data.access);
        }
        sessionStorage.setItem("refresh", response.data.refresh);
        router.push('/base/home');
        console.log("登录成功");
    }).catch(errorInfo => {
        Modal.error({ title: "系统提示", content: "用户名密码验证失败" });
        console.log("用户名密码验证失败");
        console.log(errorInfo);
    })
};

// 账号密码合法性验证
const validateUser = async (_rule, value) => {
    if (value === '') {
        return Promise.reject('Please input your username');
    }
    return Promise.resolve();
};

const validatePass = async (_rule, value) => {
    if (value === '') {
        return Promise.reject('Please input the password');
    }
    return Promise.resolve();
};

const rules = {
    username: [
        { required: true, validator: validateUser, trigger: 'submit' },
    ],

    password: [
        { required: true, validator: validatePass, trigger: 'submit' },
    ],
};

</script>



<style scoped>
.container {
    display: flex;
    justify-content: center;
    align-items: center;
}

#bg {
    background-color: gainsboro;
    background-image: url("../static/images/login.png");
    background-size: cover;
    background-repeat: no-repeat;
    background-position: center;
    min-width: 100vw;
    min-height: 100vh;
}

.center-box {
    padding: 60px 50px 0px;
    background-color: aliceblue;
    opacity: 0.9;
    border-radius: 5%;
}

.login-form-forgot {
    position: relative;
    left: 182px;
    top: -60px;
    font-size: 14px;
    color: rgb(28, 28, 109);
}

.login-form-button {
    width: 300px;
    position: relative;
    top: -60px;
}

.register-now {
    position: relative;
    left: 4px;
    top: -45px;
    font-size: 14px;
    color: rgb(28, 28, 109);
}

.register-now a {
    font-size: 14px;
    color: rgb(28, 28, 109);
}
</style>