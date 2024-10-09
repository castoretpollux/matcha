<script setup>
    import { Loader } from 'lucide-vue-next';
    import { ref, defineExpose } from 'vue';

    const loader = ref(null)
    
    const load = (state) => {
        if (state) loader.value.classList.add('load')
        if (!state) loader.value.classList.remove('load')
    }

    defineExpose({
        load
    })

</script>

<template>
    <div class="admin__loader" ref="loader">
        <Loader color="white"/>
    </div>
</template>

<style lang="scss">@import "./adminloader.scss";</style>
