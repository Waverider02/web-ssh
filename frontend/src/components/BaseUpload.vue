<template>
    <a-upload-dragger v-model="fileList" name="file" :multiple="true" :before-upload="beforeUpload">
        <p class="ant-upload-drag-icon">
            <inbox-outlined />
        </p>
        <p class="ant-upload-text">Click or drag file to this area to upload</p>
        <p class="ant-upload-hint">
            Support for a single or bulk upload. Strictly prohibit from uploading company data or other
            band files
        </p>
        <template #itemRender></template>
    </a-upload-dragger>
    <div v-for="file in fileList">
        <a-space :size="20">
            <span style="cursor:default;color:#9CA3AF;">
                <PaperClipOutlined /> {{ file.name }}
            </span>
            <span @click="removeFile(file.uid)" style="cursor: pointer;color:#9CA3AF;">
                <DeleteOutlined /> clear
            </span>
        </a-space>
    </div>
</template>

<script setup>
const fileList = defineModel('fileList', { default: [] });
defineProps({ beforeUpload: Function })

const removeFile = (uid) => {
    const idx = fileList.value.findIndex(f => f.uid === uid)
    if (idx > -1) fileList.value.splice(idx, 1)
}

</script>