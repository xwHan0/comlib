module.exports = {
    "globals": {
        "console": true,
        "module": true,
        "require": true
    },

    parserOptions: {
      sourceType: 'module'
    },
    rules: {
        parser: "vue-eslint-parser"
    },

    env: {
        browser: true,
        node: true,
        // jquery: true
    }
};
