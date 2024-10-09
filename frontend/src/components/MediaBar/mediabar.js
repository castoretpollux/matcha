import { useChatStore } from "@/stores/chat";

class MediaBar {
    constructor() {
        this.chatStore = useChatStore()
    }

    toggle(forced=false) {
        let mediabar = document.querySelector('.mediabar')
        if (forced) {
            mediabar.classList.add('open')
        } else {
            mediabar.classList.toggle('open')
        }
    }
}

export default MediaBar;

