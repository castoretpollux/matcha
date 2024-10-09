<script setup>
    import { defineEmits } from 'vue';
    import { SessionStore } from "@/stores/session";

    const emits = defineEmits(['updateInfo', 'back'])
    const session = SessionStore();

    const deleteAll = () => {
        session.deleteChat('all')
        emits('back', null)
    }

    const back = (_subpopin) => {
        emits('back', null)
    }

</script>

<template>
    <div class="subpopin">
        <div class="subpopin__content">
            <div class="subpopin__content__title">
                <span>{{  $t('delete') }} {{ $t('all') }} {{  $t('chats') }} ?</span>
            </div>
            <div class="subpopin__content__text">
                <span>{{  $t('delete_msg') }} {{ $t('all_plural') }} {{  $t('chats') }}</span>
            </div>
            <div class="subpopin__content__buttons" >
                <button class="back" @click="back">
                    <span>{{ $t('back') }}</span>
                </button>
                <button class="delete" @click="deleteAll">
                    <span>{{ $t('delete') }} {{ $t('all') }}</span>
                </button>
            </div>
        </div>
    </div>
</template>

<style lang="scss">@import "./deletechats.scss";</style>
