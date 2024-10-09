import { entry as entryInputRenderer }           from "./InputRenderer.vue";
import { entry as entrySelectRenderer }          from "./SelectRenderer.vue";
import { entry as entryTextareaRenderer }        from "./TextareaRenderer.vue";
import { entry as entryCheckboxRenderer }        from "./CheckboxRenderer.vue";
import { entry as entryAutoCompleteRenderer }    from "./AutoCompleteRenderer.vue";
import { entry as entryNumberRenderer }          from "./NumberRenderer.vue";
import { entry as entryRadioRenderer }           from "./RadioRenderer.vue";
import { entry as entryMultipleChoiceRenderer }  from "./MultipleChoiceRenderer.vue";
import { entry as entryDynamicListRenderer }     from "./DynamicListRenderer.vue";


export { default as InputRenderer }           from "./InputRenderer.vue";
export { default as SelectRenderer }          from "./SelectRenderer.vue";
export { default as TextareaRenderer }        from "./TextareaRenderer.vue";
export { default as CheckboxRenderer }        from "./CheckboxRenderer.vue";
export { default as AutoCompleteRenderer }    from "./AutoCompleteRenderer.vue";
export { default as NumberRenderer }          from "./NumberRenderer.vue";
export { default as RadioRenderer }           from "./RadioRenderer.vue";
export { default as MultipleChoiceRenderer }  from "./MultipleChoiceRenderer.vue";
export { default as DynamicListRenderer }     from "./DynamicListRenderer.vue";


export const customRenderers = [
    entryInputRenderer,
    entrySelectRenderer,
    entryTextareaRenderer,
    entryCheckboxRenderer,
    entryAutoCompleteRenderer,
    entryNumberRenderer,
    entryRadioRenderer,
    entryMultipleChoiceRenderer,
    entryDynamicListRenderer
]
