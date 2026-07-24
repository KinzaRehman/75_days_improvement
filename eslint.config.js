'use strict';

// Flat config format (ESLint 9+). Kept intentionally minimal - this
// project has zero runtime dependencies by design, so the lint config
// stays dependency-light too.
module.exports = [
  {
    files: ['src/**/*.js', 'tests/**/*.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      globals: {
        module: 'readonly',
        require: 'readonly',
        process: 'readonly',
        console: 'readonly',
      },
    },
    rules: {
      'no-unused-vars': 'warn',
      'no-undef': 'error',
      eqeqeq: ['warn', 'smart'],
      'prefer-const': 'warn',
    },
  },
];
