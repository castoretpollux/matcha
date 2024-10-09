<script setup>
    import { ref, defineEmits, defineExpose } from 'vue';
    import { useUserStore } from "@/stores/user";
    import { X } from 'lucide-vue-next';
    import UserManager from "@/helpers/userManager.js"
    
    import { useI18n } from "vue-i18n";
    const { t } = useI18n();

    const emits = defineEmits(['handleRegistredPrompt', 'openRegistredPromptPanel', 'addIntoPrompt'])
    const userStore = useUserStore()
    const userManager = new UserManager()

    const active = ref(false)
    const selectedPrompt = ref('id')

    const handleSelectRegisteredPrompt = (prompt) => {
        selectedPrompt.value = prompt.id
        emits('handleRegistredPrompt', prompt.content)
        setTimeout(() => {
            selectedPrompt.value = ''
        }, 2000);
    }

    const handleDeleteRegisteredPrompt = (prompt) => {
        userManager.deletePromptToUserPreferences(prompt.message)
        emits('updateInfo', `${t('the')} ${t('prompt')} ${t('has_been')} ${t('deleted')}`);
    }


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
    <div class="registred-prompt__panel" v-show="active">
        <ul class="registred-prompt__panel__list">
            <li
                class="registred-prompt__panel__list__noprompt"
                v-if="!userStore.preferences.prompts?.length">
                    {{ $t('registredprompt_noprompt')}}
            </li>

            <li
                :class="[
                    'registred-prompt__panel__list__item',
                    {'active': selectedPrompt == prompt.id},
                ]"
                v-for="prompt in userStore.preferences.prompts"
                @click="handleSelectRegisteredPrompt(prompt)"
            >
                <p class="registred-prompt__panel__list__item__text">
                    "{{ prompt.content }}"
                    <span>[{{ $t('add')}} {{ $t('to')}} {{ $t('prompt')}}]</span>
                </p>
                <button class="delete" @click.stop.prevent="handleDeleteRegisteredPrompt(prompt)">
                    <X color="black"/>
                </button>
            </li>
        </ul>
    </div>
</template>

<style lang="scss">@import "./registredprompt.scss";</style>
