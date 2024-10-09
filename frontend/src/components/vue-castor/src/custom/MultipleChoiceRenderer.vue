<script lang="ts">
  import { ControlElement, JsonFormsRendererRegistryEntry, rankWith, optionIs} from '@jsonforms/core';
  import { rendererProps, useJsonFormsControl, RendererProps} from '../../config/jsonforms';
  import { useVanillaControl } from '../util'
  import { defineComponent } from 'vue';
  import { default as CustomWrapper } from './customWrapper.vue';

  const multipleChoiceRenderer = defineComponent({
    name: 'MultipleChoiceRenderer',
    components: {
      CustomWrapper,
    },
    props: {
      ...rendererProps<ControlElement>(),
    },
    setup(props: RendererProps<ControlElement>) {
        const { control, handleChange } = useJsonFormsControl(props);

        const selectedValues = Array(control.value.data);
        handleChange(control.value.path, selectedValues);

        const onClick = (event: Event) => {
            const target = event.target as HTMLInputElement;
            const value = target.value;

            const index = selectedValues.indexOf(value);
            if (index === -1) {
                selectedValues.push(value);
            } else {
                selectedValues.splice(index, 1);
            }

            handleChange(control.value.path, selectedValues);
        };

        const editMode = props.schema['editMode']

        return {
            ...useVanillaControl({ control, handleChange }),
            onClick,
            editMode
        }
    },
  });
  export default multipleChoiceRenderer;

  export const entry: JsonFormsRendererRegistryEntry = {
    renderer: multipleChoiceRenderer,
    tester: rankWith(3, optionIs('format', 'multiple')),
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
    <label v-if="control.uischema.label" class="renderer_label renderer_label_choice">{{ control.label }}</label>
    <!-- WRAPPER CONTAINER -->
    <div class="renderer_wrapper_container"> 
      <!-- RADIO -->
      <label
        v-for="choice in control.uischema.options?.enum"
        :for="choice"
        :class="[
          'renderer_label_choice_label',
          { 'checked': control.data.includes(choice) }
        ]
      ">
          <!-- CHOICE LABEL -->
          <span>{{ choice }}</span>
          <!-- CHOICE INPUT -->
          <input
              type="checkbox"
              :id="control.id"
              :key="choice"
              :value="choice"
              :disabled="!control.enabled"
              :autofocus="appliedOptions.focus"
              :checked="control.data.includes(choice)"
              class="renderer_input renderer_input_choice"
              @click="onClick"
              @focus="isFocused = true"
              @blur="isFocused = false"
              :readonly="!control.schema.extra.editable && editMode"
            />
      </label>
    </div>
  </CustomWrapper>
</template>

