<script lang="ts">
  import { ControlElement, JsonFormsRendererRegistryEntry, rankWith, optionIs} from '@jsonforms/core';
  import { rendererProps, useJsonFormsControl, RendererProps} from '../../config/jsonforms';
  import { useVanillaControl } from '../util'
  import { defineComponent } from 'vue';
  import { default as CustomWrapper } from './customWrapper.vue';

  const textareaRenderer = defineComponent({
    name: 'TextareaRenderer',
    components: {
      CustomWrapper,
    },
    props: {
      ...rendererProps<ControlElement>(),
    },
    setup(props: RendererProps<ControlElement>) {
          useJsonFormsControl(props);
          const editMode = props.schema['editMode']
          return {
              ...useVanillaControl(useJsonFormsControl(props), target => target.value || undefined),
              editMode
          }
      },
  });

  export default textareaRenderer;

  export const entry: JsonFormsRendererRegistryEntry = {
    renderer: textareaRenderer,
    tester: rankWith(3, optionIs('multi', true)),
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

    <!-- TEXTAREA -->
    <label class="renderer_label renderer_label_textarea">
      <!-- TEXTAREA LABEL -->  
      <span v-if="control.uischema.label">{{ control.uischema.label }}<sup v-if="control.uischema.options?.required">*</sup></span>
      <!-- TEXTAREA INPUT -->  
      <textarea
          :id="control.id"
          :autofocus="appliedOptions.focus"
          :placeholder="control.uischema.options?.placeholder"
          @change="onChange"
          @focus="isFocused = true"
          @blur="isFocused = false"
          class="renderer_input renderer_input_textarea"
          :maxlength="control.uischema.options?.max_length"
          :minlength="control.uischema.options?.min_length"
          :rows="control.uischema.options?.rows"
          :required="control.uischema.options?.required ? true : false"
          :readonly="!control.schema.extra.editable && editMode"
        >{{ control.data }}</textarea>
    </label>

  </CustomWrapper>

</template>

