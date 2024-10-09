<script lang="ts">
  import { defineComponent, PropType } from 'vue';
  import { Styles } from '../styles';
  import { Options } from '../util';
  import { BookText, BookOpenText } from 'lucide-vue-next';
  
  export default defineComponent({
    name: 'CustomWrapper',
    props: {
      id: {
        required: false,
        type: String,
      },
      uitype: {
        required: true,
        type: String,
      },
      description: {
        required: false as const,
        type: String,
        default: undefined,
      },
      errors: {
        required: false as const,
        type: String,
        default: undefined,
      },
      label: {
        required: false as const,
        type: String,
        default: undefined,
      },
      appliedOptions: {
        required: false as const,
        type: Object as PropType<Options>,
        default: undefined,
      },
      visible: {
        required: false as const,
        type: Boolean,
        default: true,
      },
      required: {
        required: false as const,
        type: Boolean,
        default: false,
      },
      isFocused: {
        required: false as const,
        type: Boolean,
        default: false,
      },
      styles: {
        required: true,
        type: Object as PropType<Styles>,
      },
      rule: {
        required: false as const,
        type: Object,
        default: {},
      },
    },
    setup() {
        return {
            BookText,
            BookOpenText,
        }
    },
  });
</script>

<template>
    <div v-if="visible" :class="'renderer_wrapper' + ' renderer_wrapper_' + uitype" :id="'wrapper-' + id">
        <!-- COMPONENT -->
         <slot></slot>

        <!-- ERROR -->
        <div :class="errors ? styles.control.error : null" v-if="errors">
            {{ errors ? errors : null }}
        </div>

        <!-- DESCRIPTION -->
        <div v-if="description && visible" class="renderer_description">
            <component :is="BookText" class="renderer_description_close" color="black"/>
            <component :is="BookOpenText" class="renderer_description_open" color="#374151"/>
            <div class="renderer_description_content">
                <p :class="'renderer_description_' + uitype">{{description}}</p>
            </div>
        </div>
    </div>
</template>