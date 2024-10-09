<script setup>
import { useChatStore } from "@/stores/chat";
import { SessionStore } from "@/stores/session";
import UserManager from "@/helpers/userManager.js";
import VueMarkdown from 'vue-markdown-render';
import MarkdownItHighlightjs from 'markdown-it-highlightjs';
import { html5Media } from 'markdown-it-html5-media';
import MarkdownItEmphasisAlt from 'markdown-it-emphasis-alt';
import { ThumbsUp, ThumbsDown, Save, SquareCheck, Square } from 'lucide-vue-next';
import { watch, ref } from 'vue';

const plugins = [MarkdownItEmphasisAlt, MarkdownItHighlightjs, html5Media];
const markdownOptions = {
    breaks: true,
}

const chatStore = useChatStore();
const session = SessionStore();

const userManager = new UserManager();

const messages = ref([])
watch(() => [chatStore.currentChatId, session.getChat()?.messages], () => {
    messages.value = session.getChat()?.messages || []
}, { deep: true });


// on message.content change, scroll to bottom
watch(() =>  messages.value, () => {
    const messagesElem = document.querySelector('.chatmessages');
    messagesElem.scrollTop = messagesElem.scrollHeight;
}, { deep: true });


</script>

<template>
    <div class="chatmessages">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/monokai-sublime.css">
        <div class="chatmessages__item" v-for="message, index in messages" :key="index">
            <div class="chatmessages__item__content">
                <img v-if="message.kind == 'request'" src="@/assets/img/profile.webp" alt="Profile" class="chatmessages__item__content__img">
                <img v-else src="@/assets/img/aisystem.webp" alt="Profile" class="chatmessages__item__content__img">
                <div class="chatmessages__item__content__box">
                    <!-- HEAD MESSAGE -->
                    <div class="chatmessages__item__content__box__container">
                        <!-- USER MESSAGE HEADER -->
                        <p class="chatmessages__item__content__box__kind" v-if="message.kind == 'request'">
                            {{ message.username }} [{{ message.pipeline_label }}]
                            <span>{{ message.created_on }}</span>
                        </p>
                        <!-- SYSTEM MESSAGE HEADER -->
                        <p class="chatmessages__item__content__box__kind" v-else>
                            A.I System [{{ message.pipeline_label }}]
                            <span>{{ message.created_on }}</span>
                        </p>

                        <!-- MESSAGE ACTIONS -->
                        <div :class="'chatmessages__item__actions' + (message.favorite ? ' keep' : '')">
                            <!-- SAVE-->
                            <div
                            v-if="message.kind == 'request' && message.is_prompt == false"
                            @click="userManager.addPromptToUserPreferences(message.content, message);"
                            class="chatmessages__item__actions__icon save"
                            >
                                <Save color="white"/>
                            </div>
                            <div 
                            v-if="message.kind == 'request' && message.is_prompt == true" 
                            @click="userManager.deletePromptToUserPreferences(message);"
                            class="chatmessages__item__actions__icon save"
                            >
                                <Save color="green"/>
                            </div>

                            <!-- SELECTED -->
                            <div
                            v-if="message.selected"
                            @click="session.setMessageAction(message, 'selected', !message.selected); message.selected = false"
                            class="chatmessages__item__actions__icon selected"
                            >
                                <SquareCheck color="white"/>
                            </div>
                            <div
                            v-else
                            @click="session.setMessageAction(message, 'selected', !message.selected); message.selected = true"
                            class="chatmessages__item__actions__icon selected"
                            >
                                <Square color="white"/>
                            </div>
                            <!-- LIKE -->
                            <div
                            v-if="message.kind != 'request'"
                            @click="session.setMessageAction(message, 'valid', true)"
                            :class="'chatmessages__item__actions__icon like' + (message.valid === true ? ' selected ' : '')"
                            >
                                <ThumbsUp color="white"/>
                            </div>
                            <!-- UNLIKE -->
                            <div
                            v-if="message.kind != 'request'"
                            @click="session.setMessageAction(message, 'valid', false)"
                            :class="'chatmessages__item__actions__icon unlike' + (message.valid === false ? ' selected ' : '')"
                            >
                                <ThumbsDown color="white"/>
                            </div>

                        </div>
                    </div>
                    <!-- END OF HEAD MESSAGE -->

                    <!-- MESSAGE CONTENT -->
                    <div :class="'chatmessages__item__content__box__message ' + message.kind">

                        <div v-if="message.renderer != 'html'" class="markdown_renderer">
                            <vue-markdown :source="message.content" :plugins="plugins" :options="markdownOptions"></vue-markdown>
                        </div>
                        <div v-else class="html_renderer">
                            <div v-html="message.content"></div> <!-- NOSONAR -->
                        </div>

                        <span v-if="message.inProgress && message.kind != 'request'"
                            :class="'chatmessages__item__content__box__message__inprogress ' + session.getChat().pipeline_type?.split('->')[1]"></span>
                    </div>
                    <!-- END OF MESSAGE CONTENT -->
                </div>

                
            </div>

        </div>
    </div>
</template>

<style lang="scss">@import "./chatmessage.scss";</style>