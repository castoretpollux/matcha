<script lang="ts">
  import { ControlElement, JsonFormsRendererRegistryEntry, rankWith, optionIs} from '@jsonforms/core';
  import { rendererProps, useJsonFormsControl, RendererProps} from '../../config/jsonforms';
  import { useVanillaControl } from '../util'
  import { defineComponent, ref } from 'vue';
  import { default as CustomWrapper } from './customWrapper.vue';
  import { Plus, Trash2, ChevronUp } from 'lucide-vue-next';


  const dynamicListRenderer = defineComponent({
    name: 'DynamicListRenderer',
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

        const schemaItem = Object();
        props.uischema.options?.enum.forEach((item: any[]) => {
            schemaItem[item[0]] = {
                value: null,
                extra: item[1],
                type: item[2],
                size: item[3],
                required: item[4],
            };
        });

        const listItems = ref(Array())
        const addItem = () => {
            listItems.value.push(JSON.parse(JSON.stringify(schemaItem)));
        }
        listItems.value.push(JSON.parse(JSON.stringify(schemaItem)));

        const onInput = (event: Event) => {
            const target = event.target as HTMLInputElement;
            const listIndex = Number(target.getAttribute('data-index'))
            const key = String(target.getAttribute('data-key'))
            const value = target.value;
            listItems.value[listIndex][key].value = value
            onChange()
        }

        const deleteItem = (index: any) => {
            listItems.value.splice(index, 1);
            onChange()
        }

        const toggleList = (index: any) => {
            document.querySelector(`#list-${index}`)?.classList.toggle('hide')
        }

        const onChange = () => {
            const dynamiclist = listItems.value.map(item => {
                const simplifiedItem = Object();
                for (const [key, valueObj] of Object.entries(item)) {
                    const typedValueObj = valueObj as { value: any; };
                    simplifiedItem[key] = typedValueObj.value;
                }
                return simplifiedItem;
            });
            handleChange(control.value.path, dynamiclist);
        }

        const editMode = props.schema['editMode']

        return {
            ...useVanillaControl({ control, handleChange }),
            onInput,
            listItems,
            addItem,
            schemaItem,
            deleteItem,
            toggleList,
            Plus,
            Trash2,
            ChevronUp,
            editMode
        }
    },
  });
  export default dynamicListRenderer;

  export const entry: JsonFormsRendererRegistryEntry = {
    renderer: dynamicListRenderer,
    tester: rankWith(3, optionIs('format', 'dynamiclist')),
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
    <label 
        class="renderer_label renderer_label_list">
            <span>{{ control.uischema.label }}</span>
    </label>


    <!-- WRAPPER CONTAINER -->
    <div class="renderer_wrapper_box">        
        <!-- FOR ITEM IN LIST -->
        <div v-for="(item, index) in listItems" class="renderer_input_list" :id="'list-' + index">
            <div class="renderer_input_list_toggle" @click="toggleList(index)">
                <div class="renderer_input_list_toggle-bar"></div>
                <button class="renderer_input_list_toggle_button" >
                    <component :is="ChevronUp" color="white"/>
                </button>
            </div>
            <!-- BUILD ROW LAYOUT -->
            <div v-for="row in control.uischema.options?.layout" class="renderer_input_list_row">
                <!-- BUILD LAYOUT ROW FIELDS -->
                <div v-for="field in row" class="renderer_input_list_row_field" :style="'flex:' + listItems[index][field].size + ';'">
                    <!-- BUILD FIELD -->
                     <label
                        :class="[
                        'renderer_label renderer_input_list_label',
                        {'is_required': listItems[index][field].required}
                        ]"
                     >
                        <input
                            v-if="listItems[index][field].type == 'input'"
                            :id="field + '-' + index"
                            class="renderer_input renderer_input_list_item"
                            :data-index="index"
                            :data-key="field"
                            :autofocus="appliedOptions.focus"
                            :value="listItems[index][field].value"
                            :placeholder="listItems[index][field].extra"
                            :required="listItems[index][field].required ? true : false"
                            @focus="isFocused = true"
                            @blur="isFocused = false"
                            @input="onInput"
                            :readonly="!control.schema.extra.editable && editMode"
                        />
                        <textarea 
                            v-if="listItems[index][field].type == 'textarea'"
                            :id="field + '-' + index"
                            class="renderer_input renderer_input_list_item"
                            :data-index="index"
                            :data-key="field"
                            :autofocus="appliedOptions.focus"
                            :placeholder="listItems[index][field].extra"
                            :required="listItems[index][field].required ? true : false"
                            rows="3"
                            @input="onInput"
                            @focus="isFocused = true"
                            @blur="isFocused = false"
                            :readonly="!control.schema.extra.editable && editMode"
                            >{{ listItems[index][field].value }}</textarea>
                        <select
                            v-if="listItems[index][field].type == 'select'"
                            :id="field + '-' + index"
                            class="renderer_input renderer_input_list_item"
                            :data-index="index"
                            :data-key="field"
                            :autofocus="appliedOptions.focus"
                            :default="listItems[index][field].extra[0]"
                            @focus="isFocused = true"
                            @blur="isFocused = false"
                            @change="onInput"
                            :readonly="!control.schema.extra.editable && editMode"
                        >
                            <option v-for="opt, opt_index in listItems[index][field].extra" :selected="opt_index == 0 ? true : false">
                                {{ opt }}
                            </option>

                        </select>
                     </label>
                </div>
            </div>

            <button class="renderer_input_list_item_button" @click="deleteItem(index)"><component :is="Trash2" color="red"/></button>


        </div>

        <!-- BUTTON ADD -->
        <button class="renderer_label_list__button" @click="addItem">
            <component :is="Plus" color="white"/>
        </button>
    </div>

  </CustomWrapper>
</template>

