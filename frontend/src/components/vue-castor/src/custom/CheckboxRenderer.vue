<script lang="ts">
  import { ControlElement, JsonFormsRendererRegistryEntry, rankWith, optionIs} from '@jsonforms/core';
  import { rendererProps, useJsonFormsControl, RendererProps} from '../../config/jsonforms';
  import { useVanillaControl } from '../util'
  import { defineComponent } from 'vue';
  import { default as CustomWrapper } from './customWrapper.vue';

  const checkboxRenderer = defineComponent({
    name: 'CheckboxRenderer',
    components: {
      CustomWrapper,
    },
    props: {
      ...rendererProps<ControlElement>(),
    },
    setup(props: RendererProps<ControlElement>) {
          const { control, handleChange } = useJsonFormsControl(props);
          const extra = control.value.schema['extra'];
          if (extra.default != null) {
            handleChange(control.value.path, extra.default);
          }

          const editMode = props.schema['editMode']

          return {
            ...useVanillaControl({ control, handleChange }, target => target.checked),
            editMode
          }
      },
  });

  export default checkboxRenderer;

  export const entry: JsonFormsRendererRegistryEntry = {
    renderer: checkboxRenderer,
    tester: rankWith(3, optionIs('format', 'checkbox')),
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
      <!-- BASIC -->
      <label
        v-if="control.uischema.options?.variant != 'toggle'"
        :class="[
          'renderer_label renderer_label_checkbox renderer_label_checkbox_base',
          { 'checked': control.data}
          ]"
        
      >
        <!-- BASIC LABEL -->
        <span v-if="control.uischema.label">{{ control.uischema.label }}</span> 
        <!-- BASIC INPUT -->
        <input
          type="checkbox"
          :id="control.id"
          :checked="control.data"
          :autofocus="appliedOptions.focus"
          @change="onChange"
          @focus="isFocused = true"
          @blur="isFocused = false"
          :disabled="!control.schema.extra.editable && editMode"
          class="renderer_input renderer_input_checkbox"
        />
      </label>

      <!-- TOGGLE -->
      <label
        v-if="control.uischema.label && control.uischema.options?.variant == 'toggle'"
        class="renderer_label renderer_label_checkbox renderer_label_checkbox_toggle"
      >
          <span>{{ control.uischema.label }}</span>
      </label>
      <label
        v-if="control.uischema.options?.variant == 'toggle'"
        class="renderer_label_toggle_switch renderer_label_toggle"
      >
          <input
            type="checkbox"
            :id="control.id"
            :checked="control.data = control.uischema.default"
            :autofocus="appliedOptions.focus"
            @change="onChange"
            @focus="isFocused = true"
            @blur="isFocused = false"
            class="renderer_input renderer_input_toggle"
            :readonly="!control.schema.extra.editable && editMode"
            :required="control.uischema.options?.required ? true : false"
            :disabled="!control.schema.extra.editable && editMode"
          />
          <span class="renderer_input_toggle_slider"></span>
      </label>
  
  </CustomWrapper>

</template>