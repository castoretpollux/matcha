<script setup>
</script>

<template>
  <header>

  </header>

  <router-view v-slot="{ Component }">
    <transition name="fade">
      <component :is="Component" />
    </transition>
  </router-view>
</template>

<style lang="scss">
  @import "./assets/scss/app.scss";
</style>
