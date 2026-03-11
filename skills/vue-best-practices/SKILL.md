---
name: vue-best-practices
description: Vue 3 + TypeScript best practices (vue-tsc, Volar, props, routing, Pinia). Use when writing, reviewing, or refactoring Vue components.
---

## Capability Rules

| Rule | Keywords | Description |
|------|----------|-------------|
| [extract-component-props](references/extract-component-props.md) | get props type, wrapper component, extend props, inherit props, ComponentProps | Extract types from .vue components |
| [vue-tsc-strict-templates](references/vue-tsc-strict-templates.md) | undefined component, template error, strictTemplates | Catch undefined components in templates |
| [fallthrough-attributes](references/fallthrough-attributes.md) | fallthrough, $attrs, wrapper component | Type-check fallthrough attributes |
| [strict-css-modules](references/strict-css-modules.md) | css modules, $style, typo | Catch CSS module class typos |
| [data-attributes-config](references/data-attributes-config.md) | data-*, strictTemplates, attribute | Allow data-* attributes |
| [volar-3-breaking-changes](references/volar-3-breaking-changes.md) | volar, vue-language-server, editor | Fix Volar 3.0 upgrade issues |
| [module-resolution-bundler](references/module-resolution-bundler.md) | cannot find module, @vue/tsconfig, moduleResolution | Fix module resolution errors |
| [define-model-update-event](references/define-model-update-event.md) | defineModel, update event, undefined | Fix model update errors |
| [with-defaults-union-types](references/with-defaults-union-types.md) | withDefaults, union type, default | Fix union type defaults |
| [deep-watch-numeric](references/deep-watch-numeric.md) | watch, deep, array, Vue 3.5 | Efficient array watching |
| [vue-directive-comments](references/vue-directive-comments.md) | @vue-ignore, @vue-skip, template | Control template type checking |
| [vue-router-typed-params](references/vue-router-typed-params.md) | route params, typed router, unplugin | Fix route params typing |

## Efficiency Rules

| Rule | Keywords | Description |
|------|----------|-------------|
| [hmr-vue-ssr](references/hmr-vue-ssr.md) | hmr, ssr, hot reload | Fix HMR in SSR apps |
| [pinia-store-mocking](references/pinia-store-mocking.md) | pinia, mock, vitest, store | Mock Pinia stores |

## Reference

- [Vue Language Tools](https://github.com/vuejs/language-tools)
- [vue-component-type-helpers](https://github.com/vuejs/language-tools/tree/master/packages/component-type-helpers)
- [Vue 3 Documentation](https://vuejs.org/)
