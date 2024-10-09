<script setup>
import { ref } from "vue";

import UserManager from "@/helpers/userManager.js";

// Reactive references for username and password inputs using v-model
const usernameModel = ref('');
const usernameNode = ref(null);

const passwordModel = ref('');
const passwordNode = ref(null);


// userManager
const userManager = new UserManager();


// Function to handle form submission
const handleSubmit = (e) => {
    e.preventDefault();

    const usernameData = {
        value: usernameModel.value,
        node: usernameNode.value
    }
    const passwordData = {
        value: passwordModel.value,
        node: passwordNode.value
    }

    const data = {
        username: usernameData,
        password: passwordData
    }

    userManager.login(data)
};

</script>

<template>
  <main>
    <section class="login">
            <a href="/" class="login__image">
                <img src="@/assets/img/aisystem.webp" alt="Vite logo" class="login__image__content" />
            </a>

            <h1 class="login__title">
                {{ $t('login_msg') }}
            </h1>

            <div class="login__card">
                <form class="login__card__form" @submit.prevent="handleSubmit">
                    <div class="login__card__form__input">
                        <label for="username" class="">{{ $t('username') }}</label>
                        <input ref="usernameNode" type="text" id="username" v-model="usernameModel" required>
                        <span class="error-msg">{{ $t('login_error') }}</span>
                    </div>
                    <div class="login__card__form__input">
                        <label tabindex="1" for="password" class="">
                            {{ $t('password') }}
                        </label>
                        <input ref="passwordNode" type="password" id="password" v-model="passwordModel" required>
                        <span class="error-msg">{{ $t('login_error') }}</span>
                    </div>
                    <button type="submit" class="login__card__form__submit">{{ $t('login') }}</button>
                </form>
            </div>

    </section>
  </main>
</template>

<style lang="scss">
  @import "./login.scss";
</style>