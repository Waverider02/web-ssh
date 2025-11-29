<template>
    <BaseUpload v-model:fileList="fileList" :before-upload="beforeUpload"></BaseUpload>
</template>

<script setup>
import BaseUpload from './BaseUpload.vue';

const fileList = defineModel('fileList', { default: [] });

// 始终返回false以阻止自动上传
const beforeUpload = file => {
    fileList.value.push(file);
    return false;
};

</script>