import js from '@eslint/js';
import importPlugin from 'eslint-plugin-import';
import promise from 'eslint-plugin-promise';
import unicorn from 'eslint-plugin-unicorn';
import ts from 'typescript-eslint';

const srcFiles = ['src/**/*.ts'];
const configFiles = ['vite.config.ts'];
const allFiles = [...srcFiles, ...configFiles];

const browserGlobals = {
  window: 'readonly',
  document: 'readonly',
  console: 'readonly',
  setTimeout: 'readonly',
  URL: 'readonly',
  FormData: 'readonly',
  HTMLElement: 'readonly',
  HTMLInputElement: 'readonly',
  HTMLButtonElement: 'readonly',
  HTMLDivElement: 'readonly',
  MouseEvent: 'readonly',
  Node: 'readonly',
  File: 'readonly',
  Response: 'readonly',
  fetch: 'readonly',
};

const nodeGlobals = {
  process: 'readonly',
  console: 'readonly',
  __dirname: 'readonly',
};

export default [
  ...ts.configs.recommended,
  {
    ...js.configs.recommended,
    files: allFiles,
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
  },
  {
    ...unicorn.configs['flat/recommended'],
    files: allFiles,
  },
  {
    ...promise.configs['flat/recommended'],
    files: allFiles,
  },
  {
    files: srcFiles,
    languageOptions: {
      globals: browserGlobals,
    },
  },
  {
    files: configFiles,
    languageOptions: {
      globals: nodeGlobals,
      sourceType: 'module',
    },
    rules: {
      'unicorn/import-style': 'off',
      'unicorn/prefer-module': 'off',
    },
  },
  {
    files: allFiles,
    plugins: {
      import: importPlugin,
    },
    settings: {
      'import/resolver': {
        typescript: {
          project: './tsconfig.json',
        },
      },
    },
    rules: {
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
      'import/no-unresolved': 'error',
      'import/no-duplicates': 'error',
      'import/extensions': ['error', 'never', { js: 'always', mjs: 'never', ts: 'never' }],
      '@typescript-eslint/no-explicit-any': 'error',
      'import/order': [
        'error',
        {
          alphabetize: { order: 'asc', caseInsensitive: true },
          'newlines-between': 'always',
        },
      ],
      'unicorn/prevent-abbreviations': 'off',
      'unicorn/no-null': 'off',
      'unicorn/filename-case': 'off',
      'unicorn/prefer-top-level-await': 'off',
      'unicorn/expiring-todo-comments': 'off',
      'unicorn/prefer-query-selector': 'off',
      'unicorn/no-array-for-each': 'off',
      'unicorn/prefer-dom-node-append': 'off',
      'unicorn/prefer-dom-node-dataset': 'off',
      'unicorn/prefer-logical-operator-over-ternary': 'off',
      'unicorn/prefer-modern-dom-apis': 'off',
      'unicorn/prefer-type-error': 'off',
      'unicorn/consistent-function-scoping': 'off',
      'unicorn/text-encoding-identifier-case': 'off',
      'unicorn/numeric-separators-style': 'off',
    },
  },
];
