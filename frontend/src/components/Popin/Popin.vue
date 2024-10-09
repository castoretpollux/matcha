<script setup>
    import { defineProps, defineEmits } from 'vue';
    import { X } from "lucide-vue-next";

    const emits = defineEmits(['closePopin'])
    const props = defineProps({
        popinOpen: {
            type: Boolean,
            required: true,
        },
        customClass: {
            type: String,
        },
        customContainerClass: {
            type: String,
        },
        title: {
            type: String,
            required: false
        },
        embedCloseButton: {
            type: Boolean,
        },
    })

    const closePopin = (e) => {
        if (e.target.classList.contains('popin') || e.target.classList.contains('popin__container__title__close')) {
            props.popinOpen = false
            emits('closePopin', null)
        }
    }

</script>

<template>
    <div :class="['popin', customClass]" v-show="popinOpen" @click="closePopin">
        <div :class="['popin__container', customContainerClass]">
            <p v-if="title" class="popin__container__title">
                <span>{{ title }}</span>
                <button v-if="embedCloseButton" class="popin__container__title__close" @click="closePopin">
                    <X color="white"/>
                </button>
            </p>
            <div class="popin__container__content">
                <slot></slot>
            </div>
        </div>
    </div>
</template>

<style lang="scss">@import "./popin.scss";</style>
