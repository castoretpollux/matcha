<script setup>
import Toolbar from "@/components/Toolbar/Toolbar.vue";
import ChatBox from "@/components/ChatBox/ChatBox.vue";
import { useUserStore } from "@/stores/user";
import { SessionStore } from "@/stores/session";

const userStore = new useUserStore;
const session = SessionStore();

// Initialize the chat session
session.init();

</script>

<template>
	<main>
		<section class="dashboard" v-if="userStore.showDashboard">
			<Toolbar />
			<ChatBox />
		</section>
	</main>
</template>

<style lang="scss">
@import "./dashboard.scss";
</style>