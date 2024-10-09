<script setup>
import { ref, defineEmits, defineModel } from 'vue';
import { Trash2, Save } from "lucide-vue-next";

import { useUserStore } from "@/stores/user";
import UserManager from "@/helpers/userManager.js"

import { useI18n } from "vue-i18n";
const { t } = useI18n();

const userStore = useUserStore()
const userManager = new UserManager()
const emits = defineEmits(['updateInfo'])

const confirm = ref({})
const addingNewPrompt = ref(false)
const deletePopinOpen = ref(false)
const newPrompt = defineModel()


const updatePromptList = (promptId) => {
    deletePopinOpen.value = !deletePopinOpen.value

    const active = !confirm.value[promptId]
    
    confirm.value = {}
    confirm.value[promptId] = active
}

const deletePrompt = (prompt) => {
    userManager.deletePromptToUserPreferences(prompt.message)
    emits('updateInfo', `${t('the')} ${t('prompt')} ${t('has_been')} ${t('deleted')}`);
    deletePopinOpen.value = false
}

const addPrompt = () => {
    userManager.addPromptToUserPreferences(newPrompt.value)
    addingNewPrompt.value = false
    emits('updateInfo', `${t('the')} ${t('prompt')} ${t('has_been')} ${t('added')}`);
}

</script>

<template>

    <!-- LIST -->
    <div class="registredpromptlist" v-if="userStore.preferences?.prompts?.length && !addingNewPrompt">

        <div class="registredpromptlist__grid-container header">
            <div class="registredpromptlist__grid-item grid-header">{{ $t('prompt') }}</div>
            <div class="registredpromptlist__grid-item grid-header">{{ $t('action_plural') }}</div>
        </div>

        <div class="registredpromptlist__grid-container body" v-for="prompt in userStore.preferences?.prompts">
            <div class="registredpromptlist__grid-item">{{ prompt.content }}</div>
            <div class="registredpromptlist__grid-item">
                <button class="registredpromptlist__grid-item__button" @click="updatePromptList(prompt.id)">
                    <Trash2 color="red"/>
                </button>
            </div>
        </div>
    </div>

    <!-- BUTTON ADD -->
    <button class="registredpromptlist__add" @click="() => addingNewPrompt = true" v-if="userStore.preferences?.prompts?.length && !addingNewPrompt">
        {{ $t('add_one') }} {{ $t('prompt') }}
    </button>

    <!-- IF NO PROMPT -->
    <div class="registredpromptlist__message" v-if="!userStore.preferences?.prompts?.length && !addingNewPrompt">
        <img src="@/assets/img/aisystem.webp" alt="AI System">
        <h2 class="registredpromptlist__message__text">
            
            {{ $t('registredpromptlist_message_text_1_1') }}
            <button @click="() => addingNewPrompt = true" class="registredpromptlist__message__button">{{ $t('here') }}</button>
            {{ $t('registredpromptlist_message_text_1_2') }}

            <span>
                {{ $t('registredpromptlist_message_text_2') }}
                <Save color="white"/>
            </span>
        </h2>
    </div>

    <!-- VIEW ADD NEW PROMPT -->
    <div class="registredpromptlist__add-prompt" v-if="addingNewPrompt">
        <h2 class="registredpromptlist__add-prompt__title">{{ $t('grap') }} {{ $t('your') }} {{ $t('prompt') }} {{ $t('here') }} :</h2>
        <textarea placeholder="" rows="15" v-model="newPrompt"></textarea>
        <div class="registredpromptlist__add-prompt__buttons">
            <button @click="() => addingNewPrompt = false" class="factoryform__buttons__reset">{{ $t('back') }}</button>
            <button class="registredpromptlist__add-prompt__submit" @click="addPrompt">{{ $t('add') }}</button>
        </div>
    </div>

    <!-- POPIN DELETE -->
    <div class="registredpromptlist__confirm-deletion" v-show="deletePopinOpen">
        <div v-for="prompt in userStore.preferences?.prompts"
            :key="prompt" 
            class="registredpromptlist__confirm-deletion__content"
            v-show="confirm[prompt.id]"
            >
            <div class="registredpromptlist__confirm-deletion__content__title">
                <span>{{  $t('delete') }} {{ $t('this') }} {{  $t('prompt') }} ?</span>
            </div>
            <div class="registredpromptlist__confirm-deletion__content__text">
                <span>{{  $t('delete_msg') }} "{{ prompt.content }}"</span>
            </div>
            <div class="registredpromptlist__confirm-deletion__content__buttons" >
                <button class="back" @click="updatePromptList(prompt.id)">
                    <span>{{ $t('back') }}</span>
                </button>
                <button class="delete" @click="deletePrompt(prompt)">
                    <span>{{ $t('delete') }}</span>
                </button>
            </div>
        </div>
    </div>

</template>

<style lang="scss">@import "./registredpromptlist.scss";</style>
