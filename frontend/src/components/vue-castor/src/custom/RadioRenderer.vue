<script lang="ts">
  import { ControlElement, JsonFormsRendererRegistryEntry, rankWith, optionIs} from '@jsonforms/core';
  import { rendererProps, useJsonFormsControl, RendererProps} from '../../config/jsonforms';
  import { useVanillaControl } from '../util'
  import { defineComponent } from 'vue';
  import { default as CustomWrapper } from './customWrapper.vue';

  const radioRenderer = defineComponent({
    name: 'RadioRenderer',
    components: {
      CustomWrapper,
    },
    props: {
      ...rendererProps<ControlElement>(),
    },
    setup(props: RendererProps<ControlElement>) {
          const editMode = props.schema['editMode']

          return {
              ...useVanillaControl(useJsonFormsControl(props), target => target.value || undefined),
              editMode
          }
      },
  });
  export default radioRenderer;

  export const entry: JsonFormsRendererRegistryEntry = {
    renderer: radioRenderer,
    tester: rankWith(3, optionIs('format', 'radio')),
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
    <!-- MAIN LABEL -->
    <label v-if="control.uischema.label" class="renderer_label renderer_label_radio">
      <span>
        {{ control.label }}
        <sup v-if="control.uischema.options?.required">*</sup>
      </span>
    </label>
    <!-- WRAPPER CONTAINER -->
    <div class="renderer_wrapper_container"> 
        <!-- RADIO -->
        <label
          v-for="radio in control.uischema.options?.enum"
          :for="radio.value"
          :class="[
            'renderer_label_radio_label',
            { 'checked': radio.value == control.data }
          ]
        ">
            <!-- RADIO LABEL -->
            <span>{{ radio.label }}</span>

            <!-- RADIO INPUT -->
            <input
                type="radio"
                :id="radio.value"
                :key="radio.value"
                :value="radio.value"
                :checked="radio.value == control.data"
                :disabled="!control.enabled"
                :autofocus="appliedOptions.focus"
                :readonly="!control.schema.extra.editable && editMode"
                class="renderer_input renderer_input_radio"
                @change="onChange"
                @focus="isFocused = true"
                @blur="isFocused = false"
              />
        </label>
    </div>

  </CustomWrapper>

</template>

