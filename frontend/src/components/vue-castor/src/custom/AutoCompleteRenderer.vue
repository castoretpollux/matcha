<script lang="ts">
  import { ControlElement, JsonFormsRendererRegistryEntry, rankWith, optionIs} from '@jsonforms/core';
  import { rendererProps, useJsonFormsControl, RendererProps} from '../../config/jsonforms';
  import { useVanillaControl } from '../util'
  import { defineComponent, ref } from 'vue';
  import { default as CustomWrapper } from './customWrapper.vue';


  const autoCompleteRenderer = defineComponent({
    name: 'AutoCompleteRenderer',
    components: {
      CustomWrapper,
    },
    props: {
      ...rendererProps<ControlElement>(),
    },
    setup(props: RendererProps<ControlElement>) {
        const { control, handleChange } = useJsonFormsControl(props);

        const globalList = ref(Array());
        const listOptions: any = ref(null);        
        const inputSearch: any = ref(null);

        globalList.value = [...props.uischema.options?.enum]; 


        function getCookie(name: any) {
          let cookieValue = "";
          if (document.cookie && document.cookie !== '') {
              const cookies = document.cookie.split(';');
              for (const cookie of cookies) {
                  const cookieTrimmed = cookie.trim();
                  // Does this cookie string begin with the name we want?
                  if (cookieTrimmed.substring(0, name.length + 1) === (name + '=')) {
                      cookieValue = decodeURIComponent(cookieTrimmed.substring(name.length + 1));
                      break;
                  }
              }
          }
          return cookieValue;
        }

        function getHeadersToken() {
            return {
                'X-CSRFToken': getCookie('csrftoken'),
                'Authorization': `Token ${getCookie('token')}`
            }
        }

        const headers = {'Content-Type': 'application/json'}
        const tokenHeaders = getHeadersToken();

        const fetchQuery = (inputValue: any) => {
            const base_url = props.uischema.options?.api_url
            const url_params = JSON.stringify(props.uischema.options?.api_params)

            let base_params = { query: inputValue }
            if (url_params) base_params = {...base_params, ...JSON.parse(url_params)}

            const params = new URLSearchParams(base_params);
            const url = base_url + `?${params.toString()}`

            fetch(url, {
                method: 'GET',
                credentials: 'include',
                headers: {...headers, ...tokenHeaders},
            }).then(response => {
              return response.json()
            }).then(data => {
              globalList.value = []
              data.results.forEach((result: any) => {
                const item = {label: result[0], value: result[1], active: true} 
                globalList.value.push(item)
              });
            })
        }

        const onInput = (_event: Event) => {
          const inputValue = inputSearch.value.value.toLowerCase();

          // API URL
          if (props.uischema.options?.api_url) {
            fetchQuery(inputValue)
          }
          // OPTION LIST
          else if (inputValue.length > 1) {
              const matches = globalList.value.filter((item: any) => item.label.toLowerCase().includes(inputValue));
              const noMatches = globalList.value.filter((item: any) => !matches.includes(item));

              // active matches
              matches.forEach((match: any) => {
                  const itemMatch = listOptions.value.querySelector(`[data-value="${match.value}"`);
                  itemMatch.classList.add('active');
              });

              // desactive no matches
              noMatches.forEach((nomatch: any) => {
                  const itemNoMatch = listOptions.value.querySelector(`[data-value="${nomatch.value}"`);
                  itemNoMatch.classList.remove('active');
              });
          }
          // REMOVE ITEMS
          else {
            disableAllItems()
          }
        }

        const onClick = (event: Event) => {
          const target = event.target as HTMLElement;

          // Get value selected
          const valueSelected = target?.getAttribute('data-value');
          const labelSelected = target?.textContent

          // Set value selected into inputSearch
          inputSearch.value.value = labelSelected;

          // desactive all items
          disableAllItems()

          // HandleChange control data
          handleChange(control.value.path, valueSelected);
        }

        const setItem = (defaultId: any) => {
          fetchQuery('all')
          setTimeout(() => {
            const targetFolder = listOptions.value.querySelector(`[data-value="${defaultId}"`);
            inputSearch.value.value = targetFolder.textContent;
            disableAllItems()
            handleChange(control.value.path, defaultId);
          }, 200);
        }

        const extra = control.value.schema['extra'];
        if (extra.default != null) {
          setItem(extra.default)
        }

        const disableAllItems = () => {
            globalList.value.forEach((item: any) => {
                const itemElement = listOptions.value.querySelector(`[data-value="${item.value}"`);
                itemElement.classList.remove('active');
            });
        }

        const editMode = props.schema['editMode']

        return {
            ...useVanillaControl({ control, handleChange }),
            onInput,
            onClick,
            globalList,
            listOptions,
            inputSearch,
            editMode
        }
      },
  });

  export default autoCompleteRenderer;

  export const entry: JsonFormsRendererRegistryEntry = {
    renderer: autoCompleteRenderer,
    tester: rankWith(3, optionIs('format', 'autocomplete')),
  };

</script>

<template>

  <!-- WRAPPER -->
  <CustomWrapper
    :id="control.id"
    :styles="styles"
    :is-focused="isFocused"
    :applied-options="appliedOptions"
    :description="control.description"
    :uitype="control.uischema.options?.uitype"
    :visible="control.uischema.options?.visible"
  >
      <!-- AUTOCOMPLETE -->
      <label class="renderer_label renderer_label_autocomplete">
          <!-- AUTOCOMPLETE LABEL -->
          <span v-if="control.uischema.label">{{ control.uischema.label }}<sup v-if="control.uischema.options?.required == true">*</sup></span>
          <!-- AUTOCOMPLETE WRAPPER -->
          <div class="renderer_input_autocomplete_wrapper">
              <!-- AUTOCOMPLETE INPUT -->
              <input
                  type="text"
                  ref="inputSearch"
                  class="renderer_input renderer_input_autocomplete"
                  :id="control.id"
                  :placeholder="control.uischema.options?.placeholder"
                  @input="onInput"
                  @focus="isFocused = true"
                  :autofocus="appliedOptions.focus"
                  :required="control.uischema.options?.required ? true : false"
                  :readonly="!control.schema.extra.editable && editMode"
              />
              <!-- AUTOCOMPLETE LIST ITEMS -->
              <ul class="renderer_input_autocomplete_list" ref="listOptions">
                <li 
                  v-for="option in globalList"
                  :class="[
                    'renderer_input_autocomplete_list_item',
                    {'active': option.active}
                  ]"
                  :data-value="option.value"
                  @click.prevent="onClick"
                >
                  {{ option.label }}
                </li>
              </ul>

          </div>
      </label>
  </CustomWrapper>
</template>
