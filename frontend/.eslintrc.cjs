/* eslint-env node */
require("@rushstack/eslint-patch/modern-module-resolution");

module.exports = {
    root: true,
    env: {
        node: true,
    },
    extends: [
        "plugin:vue/vue3-essential",
        "eslint:recommended",
        "@vue/eslint-config-prettier",
    ],
    rules: {
        // "indent": ["error", 4],
        // "vue/html-indent": ["error", 4],
        // "vue/script-indent": ["error", 4],
        'prettier/prettier': 0,
        'vue/multi-word-component-names': 'off',
    }
};
