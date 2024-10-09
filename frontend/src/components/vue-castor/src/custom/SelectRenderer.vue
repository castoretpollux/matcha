<script lang="ts">
  import { ControlElement, JsonFormsRendererRegistryEntry, rankWith, optionIs} from '@jsonforms/core';
  import { rendererProps, useJsonFormsControl, RendererProps} from '../../config/jsonforms';
  import { useVanillaControl } from '../util'
  import { defineComponent } from 'vue';
  import { default as CustomWrapper } from './customWrapper.vue';


  const selectRenderer = defineComponent({
    name: 'SelectRenderer',
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
              ...useVanillaControl(useJsonFormsControl(props), target => target?.value || null ),
              editMode
          }
      },
  });
  export default selectRenderer;

  export const entry: JsonFormsRendererRegistryEntry = {
    renderer: selectRenderer,
    tester: rankWith(3, optionIs('format', 'select')),
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
    <!-- SELECT -->
    <label class="renderer_label renderer_label_select">

      <!-- SELECT LABEL -->
      <span v-if="control.uischema.label">{{ control.uischema.label }}<sup v-if="control.uischema.required">*</sup></span>
      
      <!-- SELECT INPUT-->
      <select
            @change="onChange"
            @focus="isFocused = true"
            @blur="isFocused = false"
            class="renderer_input renderer_input_select"
            :required="control.uischema?.options?.required ? true : false"
            :id="control.id"
            :disabled="!control.schema.extra.editable && editMode"
      >
        <!-- SELECT OPTION (empty) -->
        <option
          v-if="!control.uischema?.options?.required"
          value="">
        </option>

        <!-- SELECT OPTIONS -->
        <option
          v-for="option in control.uischema.options?.enum"
          :selected="option.value === control.data"
          :value="option.value"
          class="renderer_input_select_option"
          >
            {{option.label}}
        </option>

      </select>
    </label>
  </CustomWrapper>
</template>

