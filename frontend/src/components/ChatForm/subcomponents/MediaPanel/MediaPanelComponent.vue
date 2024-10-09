<script setup>
    import { defineExpose, ref } from 'vue';
    import { ArrowUpFromLine } from 'lucide-vue-next';

    import { useChatStore } from "@/stores/chat";
    import { SessionStore } from "@/stores/session";

    import FileManager from "@/helpers/fileManager.js";
    import { getUrlType } from "@/helpers/utils.js";

    const session = SessionStore();
    const chatStore = useChatStore();

    const fileManager = new FileManager()

    const active = ref(false)

    const display = (state) => {
        switch (state) {
            case 'toggle':
                active.value = !active.value
                break;
            case 'close':
                active.value = false
                break;
            case 'open':
                active.value = true
                break;
        }
    }

    defineExpose({
        display
    })

</script>

<template>
    <div class="chatform__medias" v-show="active">
        <div class="chatform__medias__item upload-file">
            <label for="uploadfile">
                <ArrowUpFromLine color="black"/>
                {{ $t('add_one') }} {{ $t('new') }} {{ $t('file') }}
                <input id="uploadfile" type="file" @change="fileManager.uploadFile" multiple :disabled="chatStore.isRunning ? true : false"/>
            </label>
        </div>
        <div class="chatform__medias__item" v-for="file, index in session.getChat()?.files" :key="index">
            <label class="chatform__medias__item__label" :class="{ checked: file.favorite }">
                <input type="checkbox" :checked="file.favorite" @change="fileManager.setFileFavorite(index)"/>
                <img :src="file.url" v-if="getUrlType(file.url) == 'image'" alt="" />
                <img src="https://cdn-icons-png.flaticon.com/512/337/337946.png"
                    v-if="getUrlType(file.url) == 'pdf'" alt="" />
                <img src="https://cdn-icons-png.flaticon.com/512/3979/3979406.png"
                    v-if="getUrlType(file.url) == 'doc'" alt="" />
                <!-- {{ file.name }} -->
            </label>
        </div>
    </div>
</template>