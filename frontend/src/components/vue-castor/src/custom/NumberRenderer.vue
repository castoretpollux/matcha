<script lang="ts">
  import { ControlElement, JsonFormsRendererRegistryEntry, rankWith, optionIs} from '@jsonforms/core';
  import { rendererProps, useJsonFormsControl, RendererProps} from '../../config/jsonforms';
  import { useVanillaControl } from '../util'
  import { defineComponent } from 'vue';
  import { default as CustomWrapper } from './customWrapper.vue';

  const numberRenderer = defineComponent({
    name: 'NumberRenderer',
    components: {
      CustomWrapper,
    },
    props: {
      ...rendererProps<ControlElement>(),
    },
    setup(props: RendererProps<ControlElement>) {
          const { control, handleChange } = useJsonFormsControl(props);
          const onChange = (event: Event) => {
              // HandleChange control data
              const target = event.target as HTMLInputElement;

              if (target.max && target.value > target.max) target.value = target.max
              if (target.min && target.value < target.min) target.value = target.min

              handleChange(control.value.path, Number(target?.value));
          }
          const onInput = onChange

          const editMode = props.schema['editMode']

          return {
            ...useVanillaControl({ control, handleChange }),
            onChange,
            onInput,
            editMode
          }
      },
  });

  export default numberRenderer;

  export const entry: JsonFormsRendererRegistryEntry = {
    renderer: numberRenderer,
    tester: rankWith(3, optionIs('format', 'numeric')),
  };

</script>

<template>

    <!-- WRAPPER -->
    <CustomWrapper
      :styles="styles"
      :is-focused="isFocused"
      :applied-options="appliedOptions"
      :description="control.description"
      :uitype="control.uischema.options?.variant"
      :id="control.id"
    >
        <label
          :class="'renderer_label renderer_label_' + control.uischema.options?.variant"
        >
          <!-- LABEL -->
          <span v-if="control.uischema.label">{{ control.uischema.label }}
            <sup v-if="control.uischema.options?.required">*</sup> <em>[{{control.data}}]</em>
          </span> 
          <span v-else>{{ control.data }}
            <sup v-if="control.uischema.options?.required">*</sup>
          </span> 

          <!-- INPUT (Number/Slider) -->
          <input
            :class="'renderer_input renderer_input_' + control.uischema.options?.variant"
            :id="control.id"
            :type="
              control.uischema.options?.variant == 'numeric' ? 'number' :
              control.uischema.options?.variant == 'slider' ? 'range' : 'number'
            "
            :inputmode="control.uischema.options?.input_mode"
            :value="control.data"
            :default="control.uischema.default || null"
            :min="control.uischema.options?.min || 0"
            :max="control.uischema.options?.max || control.uischema.default"
            :step="
              control.uischema.options?.step ? control.uischema.options?.step :
              control.uischema.options?.input_mode == 'decimal' ? 0.1 : 1
            "
            :required="control.uischema.options?.required ? true : false"
            :autofocus="appliedOptions.focus"
            @change="onChange"
            @input="onInput"
            @focus="isFocused = true"
            @blur="isFocused = false"
            :readonly="!control.schema.extra.editable && editMode"
          />
        </label>
    </CustomWrapper>
</template>

