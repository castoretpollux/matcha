<script lang="ts">
  import { ControlElement, JsonFormsRendererRegistryEntry, rankWith, optionIs} from '@jsonforms/core';
  import { rendererProps, useJsonFormsControl, RendererProps} from '../../config/jsonforms';
  import { useVanillaControl } from '../util'
  import { defineComponent } from 'vue';
  import { default as CustomWrapper } from './customWrapper.vue';

  
  const inputRenderer = defineComponent({
    name: 'InputRenderer',
    components: {
      CustomWrapper,
    },
    props: {
      ...rendererProps<ControlElement>(),
    },
    setup(props: RendererProps<ControlElement>) {
        const { control, handleChange } = useJsonFormsControl(props);
        // add password here
        const editMode = props.schema['editMode']
        return {
            ...useVanillaControl({ control, handleChange }),
            editMode
        }
      },
  });

  export default inputRenderer;

  export const entry: JsonFormsRendererRegistryEntry = {
    renderer: inputRenderer,
    tester: rankWith(3, optionIs('format', 'input')),
  };

</script>

<template>

  <!-- WRAPPER -->
  <CustomWrapper
    :styles="styles"
    :is-focused="isFocused"
    :applied-options="appliedOptions"
    :description="control.description"
    :uitype="control.uischema.options?.uitype"
    :id="control.id"
  >
    <!-- TEXT -->
    <label :class="'renderer_label renderer_label_' + control.uischema?.options?.type">
          <!-- TEXT LABEL -->
          <span v-if="control.uischema?.label">{{ control.uischema?.label }}
            <sup v-if="control.uischema?.options?.required">*</sup>
          </span>
          <!-- TEXT INPUT -->
          <input
              :id="control.id"
              :type="control.uischema?.options?.type"
              :value="control.data"
              :autofocus="appliedOptions.focus"
              @change="onChange"
              @focus="isFocused = true"
              @blur="isFocused = false"
              :class="'renderer_input renderer_input_' + control.uischema?.options?.type"
              :maxlength="control.uischema?.options?.max_length"
              :minlength="control.uischema?.options?.min_length"
              :placeholder="control.uischema?.options?.placeholder"
              :required="control.uischema?.options?.required ? true : false"
              :readonly="!control.schema.extra.editable && editMode"
          />
          <button type="button" class="renderer_input_password_button"
            v-if="control.uischema?.options?.type == 'password'">
              <svg style="pointer-events: none;" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><g fill="none" stroke="currentColor"><path d="M12 5c-5.444 0-8.469 4.234-9.544 6.116c-.221.386-.331.58-.32.868c.013.288.143.476.402.852C3.818 14.694 7.294 19 12 19c4.706 0 8.182-4.306 9.462-6.164c.26-.376.39-.564.401-.852c.012-.288-.098-.482-.319-.868C20.47 9.234 17.444 5 12 5Z"/><circle cx="12" cy="12" r="3"/></g></svg>
          </button>
  
    </label>

  </CustomWrapper>

</template>