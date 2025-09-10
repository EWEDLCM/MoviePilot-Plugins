import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-pcqpp-6-.js';

const {defineComponent:_defineComponent} = await importShared('vue');

const {resolveComponent:_resolveComponent,createVNode:_createVNode,createElementVNode:_createElementVNode,normalizeClass:_normalizeClass,createTextVNode:_createTextVNode,withCtx:_withCtx,toDisplayString:_toDisplayString,openBlock:_openBlock,createElementBlock:_createElementBlock,createCommentVNode:_createCommentVNode,mergeProps:_mergeProps} = await importShared('vue');

const _hoisted_1 = { class: "cloudimg123-config" };
const _hoisted_2 = { class: "page-header text-center mb-6" };
const _hoisted_3 = { class: "d-flex align-center justify-center mb-2" };
const _hoisted_4 = { class: "tabs-container" };
const _hoisted_5 = { class: "tabs-header" };
const _hoisted_6 = { class: "config-section mb-4 d-flex flex-column justify-start" };
const _hoisted_7 = { class: "config-section-title" };
const _hoisted_8 = { class: "switch-group" };
const _hoisted_9 = { class: "switch-container" };
const _hoisted_10 = { class: "switch-group" };
const _hoisted_11 = { class: "switch-container" };
const _hoisted_12 = { class: "config-section mb-4 d-flex flex-column justify-start" };
const _hoisted_13 = { class: "config-section-title" };
const _hoisted_14 = { class: "config-section mb-4" };
const _hoisted_15 = { class: "config-section-title" };
const _hoisted_16 = { class: "slider-section d-flex flex-column justify-center flex-grow-1" };
const _hoisted_17 = { class: "d-flex align-center justify-center" };
const _hoisted_18 = { class: "slider-label" };
const _hoisted_19 = { class: "slider-container flex-grow-1" };
const _hoisted_20 = { class: "config-section-title" };
const _hoisted_21 = { class: "token-status-section flex-grow-1" };
const _hoisted_22 = { class: "token-status-content" };
const _hoisted_23 = {
  key: 0,
  class: "token-status-item"
};
const _hoisted_24 = {
  key: 1,
  class: "token-status-detailed"
};
const _hoisted_25 = { class: "token-status-row" };
const _hoisted_26 = { class: "token-status-half" };
const _hoisted_27 = { class: "token-status-value success" };
const _hoisted_28 = { class: "token-status-half" };
const _hoisted_29 = { class: "token-status-row" };
const _hoisted_30 = { class: "token-status-half" };
const _hoisted_31 = { class: "token-status-value" };
const _hoisted_32 = { key: 0 };
const _hoisted_33 = {
  key: 1,
  class: "error-text"
};
const _hoisted_34 = { class: "token-status-half" };
const _hoisted_35 = { class: "token-status-value" };
const _hoisted_36 = { class: "d-flex align-center justify-space-between" };
const _hoisted_37 = { class: "d-flex align-center" };
const _hoisted_38 = { class: "d-flex align-center justify-space-between" };
const _hoisted_39 = { class: "d-flex align-center" };
const _hoisted_40 = { class: "features-list" };
const _hoisted_41 = { class: "feature-item" };
const _hoisted_42 = { class: "feature-item" };
const _hoisted_43 = { class: "feature-item" };
const _hoisted_44 = { class: "feature-item" };
const _hoisted_45 = { class: "d-flex align-center justify-space-between" };
const _hoisted_46 = { class: "d-flex align-center" };
const _hoisted_47 = { class: "link-list d-flex flex-wrap gap-2" };
const _hoisted_48 = { class: "d-flex align-center" };
const _hoisted_49 = { class: "d-flex align-center justify-space-between" };
const _hoisted_50 = { class: "d-flex align-center" };
const _hoisted_51 = { class: "token-display-section" };
const _hoisted_52 = { class: "token-info-item mb-3" };
const _hoisted_53 = { class: "token-info-value success--text" };
const _hoisted_54 = { class: "token-info-item mb-3" };
const _hoisted_55 = {
  key: 0,
  class: "token-info-item mb-4"
};
const _hoisted_56 = { class: "token-info-value" };
const _hoisted_57 = { class: "token-content-section" };
const _hoisted_58 = { class: "token-content-label d-flex align-center mb-2" };
const _hoisted_59 = {
  key: 0,
  class: "token-text"
};
const _hoisted_60 = {
  key: 1,
  class: "token-placeholder"
};
const {ref,onMounted,watch} = await importShared('vue');

const _sfc_main = /* @__PURE__ */ _defineComponent({
  __name: "Config",
  props: {
    initialConfig: {},
    api: {}
  },
  emits: ["save", "close", "switch"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const activeTab = ref("config");
    const tabHover = ref("");
    const config = ref({
      ...props.initialConfig,
      _previous_limit: props.initialConfig._previous_limit || 50
    });
    if (config.value.history_limit === 0) {
      config.value.history_limit = 200;
    }
    const isFormValid = ref(false);
    const showSecret = ref(false);
    const saving = ref(false);
    const testing = ref(false);
    const tokenInfo = ref(null);
    const showTokenDialog = ref(false);
    const formRef = ref();
    const stepsCard = ref(null);
    const featuresCard = ref(null);
    const linksCard = ref(null);
    const snackbar = ref({
      show: false,
      message: "",
      color: "success",
      icon: "mdi-check",
      timeout: 3e3
    });
    const clientIdRules = [
      (v) => !!v || "Client ID不能为空",
      (v) => v.length >= 10 || "Client ID格式不正确"
    ];
    const clientSecretRules = [
      (v) => !!v || "Client Secret不能为空",
      (v) => v.length >= 20 || "Client Secret格式不正确"
    ];
    function showMessage(message, color = "success", icon = "mdi-check") {
      snackbar.value = {
        show: true,
        message,
        color,
        icon,
        timeout: 3e3
      };
    }
    function getSliderLabel(value) {
      if (value >= 200) {
        return "∞";
      }
      return value.toString();
    }
    async function copyTokenFromDialog() {
      if (tokenInfo.value?.token) {
        try {
          await navigator.clipboard.writeText(tokenInfo.value.token);
          showMessage("Token已复制到剪贴板", "success", "mdi-check");
        } catch (error) {
          showMessage("复制失败，请手动复制", "error", "mdi-alert-circle");
        }
      } else {
        showMessage("Token内容不可用", "warning", "mdi-alert");
      }
    }
    function highlightCard(cardRef) {
      if (cardRef.value) {
        cardRef.value.$el.style.boxShadow = "0 8px 24px rgba(0, 0, 0, 0.15)";
        setTimeout(() => {
          if (cardRef.value) {
            cardRef.value.$el.style.boxShadow = "";
          }
        }, 3e3);
      }
    }
    async function testConnection() {
      if (!config.value.client_id || !config.value.client_secret) {
        showMessage("请先填写Client ID和Client Secret", "warning", "mdi-alert");
        return;
      }
      try {
        testing.value = true;
        const response = await props.api.post("plugin/CloudImg123/test_connection", {
          client_id: config.value.client_id,
          client_secret: config.value.client_secret
        });
        if (response?.success) {
          showMessage("连接测试成功", "success");
          await loadTokenInfo();
        } else {
          showMessage(response?.message || "连接测试失败", "error", "mdi-alert-circle");
        }
      } catch (error) {
        showMessage(error.message || "连接测试失败", "error", "mdi-alert-circle");
      } finally {
        testing.value = false;
      }
    }
    async function saveConfig() {
      if (!isFormValid.value) {
        showMessage("请检查配置信息", "warning", "mdi-alert");
        return;
      }
      try {
        saving.value = true;
        const configToSave = { ...config.value };
        if (configToSave.history_limit >= 200) {
          configToSave.history_limit = 0;
        }
        emit("save", configToSave);
        showMessage("配置保存成功", "success");
        await loadTokenInfo();
      } catch (error) {
        showMessage(error.message || "配置保存失败", "error", "mdi-alert-circle");
      } finally {
        saving.value = false;
      }
    }
    async function loadTokenInfo() {
      console.log("[Config] loadTokenInfo called");
      console.log("[Config] props.api:", !!props.api);
      console.log("[Config] config.value.client_id:", config.value.client_id);
      console.log("[Config] config.value.client_secret:", config.value.client_secret ? "***" : "empty");
      try {
        if (props.api && config.value.client_id && config.value.client_secret) {
          console.log("[Config] Calling token_info API...");
          const response = await props.api.get("plugin/CloudImg123/token_info");
          console.log("[Config] API response:", response);
          if (response?.success && response.data) {
            tokenInfo.value = response.data;
            console.log("[Config] Token info loaded:", tokenInfo.value);
          } else {
            tokenInfo.value = {
              has_token: false,
              is_valid: false,
              should_refresh: true
            };
            console.log("[Config] API failed, using default state");
          }
        } else {
          console.log("[Config] Missing required parameters for API call");
        }
      } catch (error) {
        console.warn("无法获取Token信息:", error);
        tokenInfo.value = {
          has_token: false,
          is_valid: false,
          should_refresh: true
        };
      }
      console.log("[Config] Final tokenInfo.value:", tokenInfo.value);
    }
    watch(() => props.initialConfig, (newConfig) => {
      config.value = { ...newConfig };
      if (config.value.history_limit === 0) {
        config.value.history_limit = 200;
      }
    }, { deep: true });
    onMounted(() => {
      console.log("[Config] onMounted called");
      loadTokenInfo();
    });
    return (_ctx, _cache) => {
      const _component_v_icon = _resolveComponent("v-icon");
      const _component_v_divider = _resolveComponent("v-divider");
      const _component_v_switch = _resolveComponent("v-switch");
      const _component_v_col = _resolveComponent("v-col");
      const _component_v_row = _resolveComponent("v-row");
      const _component_v_text_field = _resolveComponent("v-text-field");
      const _component_v_btn = _resolveComponent("v-btn");
      const _component_v_slider = _resolveComponent("v-slider");
      const _component_v_form = _resolveComponent("v-form");
      const _component_v_card_text = _resolveComponent("v-card-text");
      const _component_v_spacer = _resolveComponent("v-spacer");
      const _component_v_card_actions = _resolveComponent("v-card-actions");
      const _component_v_window_item = _resolveComponent("v-window-item");
      const _component_v_tooltip = _resolveComponent("v-tooltip");
      const _component_v_card_title = _resolveComponent("v-card-title");
      const _component_v_card = _resolveComponent("v-card");
      const _component_v_window = _resolveComponent("v-window");
      const _component_v_snackbar = _resolveComponent("v-snackbar");
      const _component_v_dialog = _resolveComponent("v-dialog");
      const _component_v_container = _resolveComponent("v-container");
      return _openBlock(), _createElementBlock("div", _hoisted_1, [
        _createVNode(_component_v_container, {
          fluid: "",
          class: "pa-3"
        }, {
          default: _withCtx(() => [
            _createElementVNode("div", _hoisted_2, [
              _createElementVNode("div", _hoisted_3, [
                _createVNode(_component_v_icon, {
                  icon: "mdi-cloud-upload",
                  size: "32",
                  class: "me-3",
                  color: "primary"
                }),
                _cache[23] || (_cache[23] = _createElementVNode("h1", { class: "text-h4 font-weight-bold text-primary" }, "123云盘图床", -1))
              ]),
              _cache[24] || (_cache[24] = _createElementVNode("p", { class: "text-subtitle-1 text-medium-emphasis" }, "配置您的图床服务，享受便捷的图片上传体验", -1))
            ]),
            _createVNode(_component_v_row, { align: "stretch" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_col, { cols: "12" }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_card, {
                      class: "config-card",
                      elevation: "4"
                    }, {
                      default: _withCtx(() => [
                        _createElementVNode("div", _hoisted_4, [
                          _createElementVNode("div", _hoisted_5, [
                            _createElementVNode("button", {
                              class: _normalizeClass(["tab-btn", { active: activeTab.value === "config" }]),
                              onClick: _cache[0] || (_cache[0] = ($event) => activeTab.value = "config"),
                              onMouseenter: _cache[1] || (_cache[1] = ($event) => tabHover.value = "config"),
                              onMouseleave: _cache[2] || (_cache[2] = ($event) => tabHover.value = "")
                            }, [
                              _createVNode(_component_v_icon, {
                                icon: "mdi-cog",
                                size: "16"
                              }),
                              _cache[25] || (_cache[25] = _createElementVNode("span", null, "图床配置", -1)),
                              _createElementVNode("div", {
                                class: _normalizeClass(["tab-indicator", { "show": activeTab.value === "config" || tabHover.value === "config" }])
                              }, null, 2)
                            ], 34),
                            _createElementVNode("button", {
                              class: _normalizeClass(["tab-btn", { active: activeTab.value === "help" }]),
                              onClick: _cache[3] || (_cache[3] = ($event) => activeTab.value = "help"),
                              onMouseenter: _cache[4] || (_cache[4] = ($event) => tabHover.value = "help"),
                              onMouseleave: _cache[5] || (_cache[5] = ($event) => tabHover.value = "")
                            }, [
                              _createVNode(_component_v_icon, {
                                icon: "mdi-information",
                                size: "16"
                              }),
                              _cache[26] || (_cache[26] = _createElementVNode("span", null, "配置说明", -1)),
                              _createElementVNode("div", {
                                class: _normalizeClass(["tab-indicator", { "show": activeTab.value === "help" || tabHover.value === "help" }])
                              }, null, 2)
                            ], 34)
                          ])
                        ]),
                        _createVNode(_component_v_divider),
                        _createVNode(_component_v_window, {
                          modelValue: activeTab.value,
                          "onUpdate:modelValue": _cache[18] || (_cache[18] = ($event) => activeTab.value = $event)
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_window_item, { value: "config" }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_card_text, { class: "pt-4" }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_v_form, {
                                      ref_key: "formRef",
                                      ref: formRef,
                                      modelValue: isFormValid.value,
                                      "onUpdate:modelValue": _cache[13] || (_cache[13] = ($event) => isFormValid.value = $event)
                                    }, {
                                      default: _withCtx(() => [
                                        _createVNode(_component_v_row, { align: "start" }, {
                                          default: _withCtx(() => [
                                            _createVNode(_component_v_col, {
                                              cols: "12",
                                              lg: "6"
                                            }, {
                                              default: _withCtx(() => [
                                                _createElementVNode("div", _hoisted_6, [
                                                  _createElementVNode("h3", _hoisted_7, [
                                                    _createVNode(_component_v_icon, {
                                                      icon: "mdi-cog",
                                                      size: "20",
                                                      class: "mr-2"
                                                    }),
                                                    _cache[27] || (_cache[27] = _createTextVNode(" 基础设置 ", -1))
                                                  ]),
                                                  _createVNode(_component_v_row, null, {
                                                    default: _withCtx(() => [
                                                      _createVNode(_component_v_col, {
                                                        cols: "12",
                                                        class: "pt-2"
                                                      }, {
                                                        default: _withCtx(() => [
                                                          _createElementVNode("div", _hoisted_8, [
                                                            _createElementVNode("div", _hoisted_9, [
                                                              _createVNode(_component_v_switch, {
                                                                modelValue: config.value.enabled,
                                                                "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => config.value.enabled = $event),
                                                                label: "启用插件",
                                                                color: "primary",
                                                                "hide-details": "",
                                                                inset: "",
                                                                class: "align-switch"
                                                              }, {
                                                                prepend: _withCtx(() => [
                                                                  _createVNode(_component_v_icon, { icon: "mdi-power" })
                                                                ]),
                                                                _: 1
                                                              }, 8, ["modelValue"])
                                                            ]),
                                                            _cache[28] || (_cache[28] = _createElementVNode("p", { class: "text-caption text-medium-emphasis switch-desc" }, " 启用插件后才可以进行图片上传 ", -1))
                                                          ])
                                                        ]),
                                                        _: 1
                                                      }),
                                                      _createVNode(_component_v_col, {
                                                        cols: "12",
                                                        class: "pt-1"
                                                      }, {
                                                        default: _withCtx(() => [
                                                          _createElementVNode("div", _hoisted_10, [
                                                            _createElementVNode("div", _hoisted_11, [
                                                              _createVNode(_component_v_switch, {
                                                                modelValue: config.value.debug,
                                                                "onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => config.value.debug = $event),
                                                                label: "详细日志",
                                                                color: "info",
                                                                "hide-details": "",
                                                                inset: "",
                                                                class: "align-switch"
                                                              }, {
                                                                prepend: _withCtx(() => [
                                                                  _createVNode(_component_v_icon, { icon: "mdi-bug" })
                                                                ]),
                                                                _: 1
                                                              }, 8, ["modelValue"])
                                                            ]),
                                                            _cache[29] || (_cache[29] = _createElementVNode("p", { class: "text-caption text-medium-emphasis switch-desc" }, " 启用后将输出详细的调试日志 ", -1))
                                                          ])
                                                        ]),
                                                        _: 1
                                                      })
                                                    ]),
                                                    _: 1
                                                  })
                                                ])
                                              ]),
                                              _: 1
                                            }),
                                            _createVNode(_component_v_col, {
                                              cols: "12",
                                              lg: "6"
                                            }, {
                                              default: _withCtx(() => [
                                                _createElementVNode("div", _hoisted_12, [
                                                  _createElementVNode("h3", _hoisted_13, [
                                                    _createVNode(_component_v_icon, {
                                                      icon: "mdi-api",
                                                      size: "20",
                                                      class: "mr-2"
                                                    }),
                                                    _cache[30] || (_cache[30] = _createTextVNode(" API配置 ", -1))
                                                  ]),
                                                  _createVNode(_component_v_row, null, {
                                                    default: _withCtx(() => [
                                                      _createVNode(_component_v_col, { cols: "12" }, {
                                                        default: _withCtx(() => [
                                                          _createVNode(_component_v_text_field, {
                                                            modelValue: config.value.client_id,
                                                            "onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => config.value.client_id = $event),
                                                            label: "Client ID",
                                                            "prepend-inner-icon": "mdi-identifier",
                                                            variant: "outlined",
                                                            density: "comfortable",
                                                            rules: clientIdRules,
                                                            placeholder: "请输入123云盘的Client ID",
                                                            clearable: "",
                                                            class: "align-textfield"
                                                          }, null, 8, ["modelValue"]),
                                                          _cache[31] || (_cache[31] = _createElementVNode("p", { class: "text-caption text-medium-emphasis" }, " 请输入在123云盘开放平台申请获得的Client ID ", -1))
                                                        ]),
                                                        _: 1
                                                      }),
                                                      _createVNode(_component_v_col, { cols: "12" }, {
                                                        default: _withCtx(() => [
                                                          _createVNode(_component_v_text_field, {
                                                            modelValue: config.value.client_secret,
                                                            "onUpdate:modelValue": _cache[10] || (_cache[10] = ($event) => config.value.client_secret = $event),
                                                            label: "Client Secret",
                                                            "prepend-inner-icon": "mdi-key",
                                                            variant: "outlined",
                                                            density: "comfortable",
                                                            type: showSecret.value ? "text" : "password",
                                                            rules: clientSecretRules,
                                                            placeholder: "请输入123云盘的Client Secret",
                                                            clearable: "",
                                                            class: "align-textfield"
                                                          }, {
                                                            "append-inner": _withCtx(() => [
                                                              _createVNode(_component_v_btn, {
                                                                icon: showSecret.value ? "mdi-eye-off" : "mdi-eye",
                                                                variant: "text",
                                                                size: "small",
                                                                onClick: _cache[9] || (_cache[9] = ($event) => showSecret.value = !showSecret.value)
                                                              }, null, 8, ["icon"])
                                                            ]),
                                                            _: 1
                                                          }, 8, ["modelValue", "type"]),
                                                          _cache[32] || (_cache[32] = _createElementVNode("p", { class: "text-caption text-medium-emphasis textfield-desc" }, " 请输入在123云盘开放平台申请获得的Client Secret，务必妥善保管 ", -1))
                                                        ]),
                                                        _: 1
                                                      })
                                                    ]),
                                                    _: 1
                                                  })
                                                ])
                                              ]),
                                              _: 1
                                            })
                                          ]),
                                          _: 1
                                        }),
                                        _createElementVNode("div", _hoisted_14, [
                                          _createVNode(_component_v_row, null, {
                                            default: _withCtx(() => [
                                              _createVNode(_component_v_col, {
                                                cols: "12",
                                                lg: "6",
                                                class: "d-flex flex-column"
                                              }, {
                                                default: _withCtx(() => [
                                                  _createElementVNode("h3", _hoisted_15, [
                                                    _createVNode(_component_v_icon, {
                                                      icon: "mdi-history",
                                                      size: "20",
                                                      class: "mr-2"
                                                    }),
                                                    _cache[33] || (_cache[33] = _createTextVNode(" 历史记录设置 ", -1))
                                                  ]),
                                                  _createElementVNode("div", _hoisted_16, [
                                                    _createElementVNode("div", _hoisted_17, [
                                                      _createElementVNode("div", _hoisted_18, [
                                                        _createVNode(_component_v_icon, {
                                                          icon: "mdi-database",
                                                          size: "20",
                                                          class: "mb-1"
                                                        }),
                                                        _cache[34] || (_cache[34] = _createElementVNode("span", { class: "text-caption" }, "存储数量", -1))
                                                      ]),
                                                      _createElementVNode("div", _hoisted_19, [
                                                        _createVNode(_component_v_slider, {
                                                          modelValue: config.value.history_limit,
                                                          "onUpdate:modelValue": _cache[11] || (_cache[11] = ($event) => config.value.history_limit = $event),
                                                          min: 20,
                                                          max: 200,
                                                          step: 20,
                                                          "show-ticks": "always",
                                                          "tick-size": "4",
                                                          color: "primary",
                                                          "track-color": "grey-lighten-3",
                                                          "thumb-label": "always",
                                                          class: "flex-grow-1"
                                                        }, {
                                                          "thumb-label": _withCtx(({ modelValue }) => [
                                                            _createTextVNode(_toDisplayString(getSliderLabel(modelValue)), 1)
                                                          ]),
                                                          _: 1
                                                        }, 8, ["modelValue"])
                                                      ])
                                                    ])
                                                  ])
                                                ]),
                                                _: 1
                                              }),
                                              _createVNode(_component_v_col, {
                                                cols: "12",
                                                lg: "6",
                                                class: "d-flex flex-column"
                                              }, {
                                                default: _withCtx(() => [
                                                  _createElementVNode("h3", _hoisted_20, [
                                                    _createVNode(_component_v_icon, {
                                                      icon: "mdi-key",
                                                      size: "24",
                                                      class: "mr-2"
                                                    }),
                                                    _cache[35] || (_cache[35] = _createTextVNode(" Token状态 ", -1))
                                                  ]),
                                                  _createElementVNode("div", _hoisted_21, [
                                                    _createElementVNode("div", _hoisted_22, [
                                                      !tokenInfo.value?.has_token ? (_openBlock(), _createElementBlock("div", _hoisted_23, [
                                                        _createVNode(_component_v_icon, {
                                                          icon: "mdi-alert-circle",
                                                          color: "error",
                                                          size: "20"
                                                        }),
                                                        _cache[36] || (_cache[36] = _createElementVNode("div", { class: "token-status-text" }, [
                                                          _createElementVNode("span", { class: "token-status-desc" }, "获取状态：未获取")
                                                        ], -1))
                                                      ])) : (_openBlock(), _createElementBlock("div", _hoisted_24, [
                                                        _createElementVNode("div", _hoisted_25, [
                                                          _createElementVNode("div", _hoisted_26, [
                                                            _cache[38] || (_cache[38] = _createElementVNode("span", { class: "token-status-label" }, "获取状态：", -1)),
                                                            _createElementVNode("span", _hoisted_27, [
                                                              _createVNode(_component_v_icon, {
                                                                icon: "mdi-check-circle",
                                                                size: "16",
                                                                color: "success",
                                                                class: "mr-1"
                                                              }),
                                                              _cache[37] || (_cache[37] = _createTextVNode(" 已获取 ", -1))
                                                            ])
                                                          ]),
                                                          _createElementVNode("div", _hoisted_28, [
                                                            _cache[39] || (_cache[39] = _createElementVNode("span", { class: "token-status-label" }, "Token状态：", -1)),
                                                            _createElementVNode("span", {
                                                              class: _normalizeClass(["token-status-value", tokenInfo.value?.is_valid ? "success" : "error"])
                                                            }, [
                                                              _createVNode(_component_v_icon, {
                                                                icon: tokenInfo.value?.is_valid ? "mdi-check-circle" : "mdi-alert-circle",
                                                                size: "16",
                                                                color: tokenInfo.value?.is_valid ? "success" : "error",
                                                                class: "mr-1"
                                                              }, null, 8, ["icon", "color"]),
                                                              _createTextVNode(" " + _toDisplayString(tokenInfo.value?.is_valid ? "有效" : "无效"), 1)
                                                            ], 2)
                                                          ])
                                                        ]),
                                                        _createElementVNode("div", _hoisted_29, [
                                                          _createElementVNode("div", _hoisted_30, [
                                                            _cache[40] || (_cache[40] = _createElementVNode("span", { class: "token-status-label" }, "剩余时间：", -1)),
                                                            _createElementVNode("span", _hoisted_31, [
                                                              _createVNode(_component_v_icon, {
                                                                icon: "mdi-clock-outline",
                                                                size: "16",
                                                                color: "primary",
                                                                class: "mr-1 align-icon-center"
                                                              }),
                                                              tokenInfo.value?.is_valid && tokenInfo.value?.remaining_days !== void 0 ? (_openBlock(), _createElementBlock("span", _hoisted_32, _toDisplayString(tokenInfo.value.remaining_days) + " 天 ", 1)) : !tokenInfo.value?.is_valid ? (_openBlock(), _createElementBlock("span", _hoisted_33, " 已过期 ")) : _createCommentVNode("", true)
                                                            ])
                                                          ]),
                                                          _createElementVNode("div", _hoisted_34, [
                                                            _cache[42] || (_cache[42] = _createElementVNode("span", { class: "token-status-label" }, "操作：", -1)),
                                                            _createElementVNode("span", _hoisted_35, [
                                                              _createVNode(_component_v_btn, {
                                                                size: "x-small",
                                                                variant: "outlined",
                                                                color: "primary",
                                                                onClick: _cache[12] || (_cache[12] = ($event) => showTokenDialog.value = true),
                                                                title: "查看Token",
                                                                class: "token-view-btn"
                                                              }, {
                                                                default: _withCtx(() => [
                                                                  _createVNode(_component_v_icon, {
                                                                    icon: "mdi-eye",
                                                                    size: "14",
                                                                    class: "mr-1 align-icon-center"
                                                                  }),
                                                                  _cache[41] || (_cache[41] = _createTextVNode(" 查看Token ", -1))
                                                                ]),
                                                                _: 1
                                                              })
                                                            ])
                                                          ])
                                                        ])
                                                      ]))
                                                    ])
                                                  ])
                                                ]),
                                                _: 1
                                              })
                                            ]),
                                            _: 1
                                          })
                                        ])
                                      ]),
                                      _: 1
                                    }, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_v_divider),
                                _createVNode(_component_v_card_actions, { class: "px-4 py-3" }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_v_spacer),
                                    _createVNode(_component_v_btn, {
                                      "prepend-icon": "mdi-test-tube",
                                      variant: "outlined",
                                      color: "info",
                                      onClick: testConnection,
                                      loading: testing.value,
                                      disabled: !config.value.client_id || !config.value.client_secret,
                                      class: "px-4 py-2"
                                    }, {
                                      default: _withCtx(() => [..._cache[43] || (_cache[43] = [
                                        _createTextVNode(" 测试连接 ", -1)
                                      ])]),
                                      _: 1
                                    }, 8, ["loading", "disabled"]),
                                    _createVNode(_component_v_btn, {
                                      "prepend-icon": "mdi-arrow-left",
                                      variant: "outlined",
                                      onClick: _cache[14] || (_cache[14] = ($event) => _ctx.$emit("switch")),
                                      class: "px-4 py-2"
                                    }, {
                                      default: _withCtx(() => [..._cache[44] || (_cache[44] = [
                                        _createTextVNode(" 返回详情 ", -1)
                                      ])]),
                                      _: 1
                                    }),
                                    _createVNode(_component_v_btn, {
                                      "prepend-icon": "mdi-content-save",
                                      color: "primary",
                                      variant: "outlined",
                                      onClick: saveConfig,
                                      loading: saving.value,
                                      disabled: !isFormValid.value,
                                      class: "px-6 py-2"
                                    }, {
                                      default: _withCtx(() => [..._cache[45] || (_cache[45] = [
                                        _createTextVNode(" 保存配置 ", -1)
                                      ])]),
                                      _: 1
                                    }, 8, ["loading", "disabled"])
                                  ]),
                                  _: 1
                                })
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_v_window_item, { value: "help" }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_card_text, { class: "pt-4" }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_v_row, null, {
                                      default: _withCtx(() => [
                                        _createVNode(_component_v_col, {
                                          cols: "12",
                                          md: "6"
                                        }, {
                                          default: _withCtx(() => [
                                            _createVNode(_component_v_card, {
                                              ref_key: "stepsCard",
                                              ref: stepsCard,
                                              class: "steps-card mb-3",
                                              elevation: "2",
                                              onClick: _cache[15] || (_cache[15] = ($event) => highlightCard(stepsCard.value))
                                            }, {
                                              default: _withCtx(() => [
                                                _createVNode(_component_v_card_title, { class: "pa-3 pb-2" }, {
                                                  default: _withCtx(() => [
                                                    _createElementVNode("div", _hoisted_36, [
                                                      _createElementVNode("div", _hoisted_37, [
                                                        _createVNode(_component_v_icon, {
                                                          icon: "mdi-format-list-numbered",
                                                          size: "20",
                                                          class: "mr-2",
                                                          color: "primary"
                                                        }),
                                                        _cache[46] || (_cache[46] = _createElementVNode("span", { class: "text-subtitle-1 font-weight-bold" }, "配置步骤", -1))
                                                      ]),
                                                      _createVNode(_component_v_tooltip, {
                                                        text: "这个按钮没啥用",
                                                        location: "top"
                                                      }, {
                                                        activator: _withCtx(({ props: props2 }) => [
                                                          _createVNode(_component_v_icon, _mergeProps(props2, {
                                                            icon: "mdi-information-outline",
                                                            size: "16",
                                                            color: "primary",
                                                            class: "opacity-50"
                                                          }), null, 16)
                                                        ]),
                                                        _: 1
                                                      })
                                                    ])
                                                  ]),
                                                  _: 1
                                                }),
                                                _createVNode(_component_v_card_text, { class: "pa-3 pt-2" }, {
                                                  default: _withCtx(() => [..._cache[47] || (_cache[47] = [
                                                    _createElementVNode("div", { class: "steps-list" }, [
                                                      _createElementVNode("div", { class: "step-item" }, [
                                                        _createElementVNode("div", { class: "step-number" }, "1"),
                                                        _createElementVNode("div", { class: "step-content" }, [
                                                          _createElementVNode("div", { class: "step-title" }, "访问123云盘开放平台"),
                                                          _createElementVNode("div", { class: "step-desc" }, "申请成为开发者")
                                                        ])
                                                      ]),
                                                      _createElementVNode("div", { class: "step-item" }, [
                                                        _createElementVNode("div", { class: "step-number" }, "2"),
                                                        _createElementVNode("div", { class: "step-content" }, [
                                                          _createElementVNode("div", { class: "step-title" }, "邮箱通知"),
                                                          _createElementVNode("div", { class: "step-desc" }, "接收邮件获取Client ID和Client Secret")
                                                        ])
                                                      ]),
                                                      _createElementVNode("div", { class: "step-item" }, [
                                                        _createElementVNode("div", { class: "step-number" }, "3"),
                                                        _createElementVNode("div", { class: "step-content" }, [
                                                          _createElementVNode("div", { class: "step-title" }, "填写配置信息"),
                                                          _createElementVNode("div", { class: "step-desc" }, "在插件配置页面中填写获取的凭证信息")
                                                        ])
                                                      ]),
                                                      _createElementVNode("div", { class: "step-item" }, [
                                                        _createElementVNode("div", { class: "step-number" }, "4"),
                                                        _createElementVNode("div", { class: "step-content" }, [
                                                          _createElementVNode("div", { class: "step-title" }, "测试连接"),
                                                          _createElementVNode("div", { class: "step-desc" }, "启用插件并点击测试链接验证配置是否正确")
                                                        ])
                                                      ])
                                                    ], -1)
                                                  ])]),
                                                  _: 1
                                                })
                                              ]),
                                              _: 1
                                            }, 512)
                                          ]),
                                          _: 1
                                        }),
                                        _createVNode(_component_v_col, {
                                          cols: "12",
                                          md: "6"
                                        }, {
                                          default: _withCtx(() => [
                                            _createVNode(_component_v_card, {
                                              ref_key: "featuresCard",
                                              ref: featuresCard,
                                              class: "features-card mb-3",
                                              elevation: "2",
                                              onClick: _cache[16] || (_cache[16] = ($event) => highlightCard(featuresCard.value))
                                            }, {
                                              default: _withCtx(() => [
                                                _createVNode(_component_v_card_title, { class: "pa-3 pb-2" }, {
                                                  default: _withCtx(() => [
                                                    _createElementVNode("div", _hoisted_38, [
                                                      _createElementVNode("div", _hoisted_39, [
                                                        _createVNode(_component_v_icon, {
                                                          icon: "mdi-cog",
                                                          size: "20",
                                                          class: "mr-2",
                                                          color: "primary"
                                                        }),
                                                        _cache[48] || (_cache[48] = _createElementVNode("span", { class: "text-subtitle-1 font-weight-bold" }, "功能说明", -1))
                                                      ]),
                                                      _createVNode(_component_v_tooltip, {
                                                        text: "这个按钮没啥用",
                                                        location: "top"
                                                      }, {
                                                        activator: _withCtx(({ props: props2 }) => [
                                                          _createVNode(_component_v_icon, _mergeProps(props2, {
                                                            icon: "mdi-information-outline",
                                                            size: "16",
                                                            color: "primary",
                                                            class: "opacity-50"
                                                          }), null, 16)
                                                        ]),
                                                        _: 1
                                                      })
                                                    ])
                                                  ]),
                                                  _: 1
                                                }),
                                                _createVNode(_component_v_card_text, { class: "pa-3 pt-2" }, {
                                                  default: _withCtx(() => [
                                                    _createElementVNode("div", _hoisted_40, [
                                                      _createElementVNode("div", _hoisted_41, [
                                                        _createVNode(_component_v_icon, {
                                                          icon: "mdi-power",
                                                          size: "20",
                                                          color: "primary",
                                                          class: "mr-3"
                                                        }),
                                                        _cache[49] || (_cache[49] = _createElementVNode("div", null, [
                                                          _createElementVNode("div", { class: "feature-title" }, "启用插件"),
                                                          _createElementVNode("div", { class: "feature-desc" }, "启用后才能获取Token使用图片上传功能")
                                                        ], -1))
                                                      ]),
                                                      _createElementVNode("div", _hoisted_42, [
                                                        _createVNode(_component_v_icon, {
                                                          icon: "mdi-key",
                                                          size: "20",
                                                          color: "warning",
                                                          class: "mr-3"
                                                        }),
                                                        _cache[50] || (_cache[50] = _createElementVNode("div", null, [
                                                          _createElementVNode("div", { class: "feature-title" }, "Token管理"),
                                                          _createElementVNode("div", { class: "feature-desc" }, "可在Token状态处查看相关内容，到期前自动更新")
                                                        ], -1))
                                                      ]),
                                                      _createElementVNode("div", _hoisted_43, [
                                                        _createVNode(_component_v_icon, {
                                                          icon: "mdi-bug",
                                                          size: "20",
                                                          color: "info",
                                                          class: "mr-3"
                                                        }),
                                                        _cache[51] || (_cache[51] = _createElementVNode("div", null, [
                                                          _createElementVNode("div", { class: "feature-title" }, "详细日志"),
                                                          _createElementVNode("div", { class: "feature-desc" }, "排查问题时开启，会增加大量日志输出")
                                                        ], -1))
                                                      ]),
                                                      _createElementVNode("div", _hoisted_44, [
                                                        _createVNode(_component_v_icon, {
                                                          icon: "mdi-database",
                                                          size: "20",
                                                          color: "success",
                                                          class: "mr-3"
                                                        }),
                                                        _cache[52] || (_cache[52] = _createElementVNode("div", null, [
                                                          _createElementVNode("div", { class: "feature-title" }, "本地化数据存储"),
                                                          _createElementVNode("div", { class: "feature-desc" }, "数据均存储于\\config\\plugins\\cloudimg123\\")
                                                        ], -1))
                                                      ])
                                                    ])
                                                  ]),
                                                  _: 1
                                                })
                                              ]),
                                              _: 1
                                            }, 512)
                                          ]),
                                          _: 1
                                        })
                                      ]),
                                      _: 1
                                    }),
                                    _createVNode(_component_v_card, {
                                      ref_key: "linksCard",
                                      ref: linksCard,
                                      class: "links-card mt-3",
                                      elevation: "2",
                                      onClick: _cache[17] || (_cache[17] = ($event) => highlightCard(linksCard.value))
                                    }, {
                                      default: _withCtx(() => [
                                        _createVNode(_component_v_card_title, { class: "pa-3 pb-2" }, {
                                          default: _withCtx(() => [
                                            _createElementVNode("div", _hoisted_45, [
                                              _createElementVNode("div", _hoisted_46, [
                                                _createVNode(_component_v_icon, {
                                                  icon: "mdi-link-variant",
                                                  size: "20",
                                                  class: "mr-2",
                                                  color: "accent"
                                                }),
                                                _cache[53] || (_cache[53] = _createElementVNode("span", { class: "text-subtitle-1 font-weight-bold" }, "相关链接", -1))
                                              ]),
                                              _createVNode(_component_v_tooltip, {
                                                text: "这个按钮没啥用",
                                                location: "top"
                                              }, {
                                                activator: _withCtx(({ props: props2 }) => [
                                                  _createVNode(_component_v_icon, _mergeProps(props2, {
                                                    icon: "mdi-information-outline",
                                                    size: "16",
                                                    color: "accent",
                                                    class: "opacity-50"
                                                  }), null, 16)
                                                ]),
                                                _: 1
                                              })
                                            ])
                                          ]),
                                          _: 1
                                        }),
                                        _createVNode(_component_v_card_text, { class: "pa-3 pt-2" }, {
                                          default: _withCtx(() => [
                                            _createElementVNode("div", _hoisted_47, [
                                              _createVNode(_component_v_btn, {
                                                variant: "outlined",
                                                size: "small",
                                                "prepend-icon": "mdi-open-in-new",
                                                href: "https://www.123pan.com/",
                                                target: "_blank",
                                                class: "px-3 py-1"
                                              }, {
                                                default: _withCtx(() => [..._cache[54] || (_cache[54] = [
                                                  _createTextVNode(" 123云盘官网 ", -1)
                                                ])]),
                                                _: 1
                                              }),
                                              _createVNode(_component_v_btn, {
                                                variant: "outlined",
                                                size: "small",
                                                "prepend-icon": "mdi-api",
                                                href: "https://www.123pan.com/developer",
                                                target: "_blank",
                                                class: "px-3 py-1"
                                              }, {
                                                default: _withCtx(() => [..._cache[55] || (_cache[55] = [
                                                  _createTextVNode(" 开放平台 ", -1)
                                                ])]),
                                                _: 1
                                              }),
                                              _createVNode(_component_v_btn, {
                                                variant: "outlined",
                                                size: "small",
                                                "prepend-icon": "mdi-book",
                                                href: "https://123yunpan.yuque.com/org-wiki-123yunpan-muaork/cr6ced",
                                                target: "_blank",
                                                class: "px-3 py-1"
                                              }, {
                                                default: _withCtx(() => [..._cache[56] || (_cache[56] = [
                                                  _createTextVNode(" API文档 ", -1)
                                                ])]),
                                                _: 1
                                              })
                                            ])
                                          ]),
                                          _: 1
                                        })
                                      ]),
                                      _: 1
                                    }, 512)
                                  ]),
                                  _: 1
                                })
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        }, 8, ["modelValue"])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }),
            _createVNode(_component_v_snackbar, {
              modelValue: snackbar.value.show,
              "onUpdate:modelValue": _cache[19] || (_cache[19] = ($event) => snackbar.value.show = $event),
              color: snackbar.value.color,
              timeout: snackbar.value.timeout,
              location: "top"
            }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_48, [
                  _createVNode(_component_v_icon, {
                    icon: snackbar.value.icon,
                    class: "me-2"
                  }, null, 8, ["icon"]),
                  _createTextVNode(" " + _toDisplayString(snackbar.value.message), 1)
                ])
              ]),
              _: 1
            }, 8, ["modelValue", "color", "timeout"]),
            _createVNode(_component_v_dialog, {
              modelValue: showTokenDialog.value,
              "onUpdate:modelValue": _cache[22] || (_cache[22] = ($event) => showTokenDialog.value = $event),
              "max-width": "500px",
              persistent: ""
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_card, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_card_title, { class: "text-h6 pa-4" }, {
                      default: _withCtx(() => [
                        _createElementVNode("div", _hoisted_49, [
                          _createElementVNode("div", _hoisted_50, [
                            _createVNode(_component_v_icon, {
                              icon: "mdi-key",
                              class: "mr-2",
                              color: "primary"
                            }),
                            _cache[57] || (_cache[57] = _createTextVNode(" Token详细信息 ", -1))
                          ]),
                          _createVNode(_component_v_btn, {
                            icon: "mdi-close",
                            variant: "text",
                            size: "small",
                            onClick: _cache[20] || (_cache[20] = ($event) => showTokenDialog.value = false)
                          })
                        ])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_divider),
                    _createVNode(_component_v_card_text, { class: "pa-4" }, {
                      default: _withCtx(() => [
                        _createElementVNode("div", _hoisted_51, [
                          _createElementVNode("div", _hoisted_52, [
                            _cache[59] || (_cache[59] = _createElementVNode("span", { class: "token-info-label font-weight-bold" }, "获取状态：", -1)),
                            _createElementVNode("span", _hoisted_53, [
                              _createVNode(_component_v_icon, {
                                icon: "mdi-check-circle",
                                size: "16",
                                color: "success",
                                class: "mr-1"
                              }),
                              _cache[58] || (_cache[58] = _createTextVNode(" 已获取 ", -1))
                            ])
                          ]),
                          _createElementVNode("div", _hoisted_54, [
                            _cache[60] || (_cache[60] = _createElementVNode("span", { class: "token-info-label font-weight-bold" }, "Token状态：", -1)),
                            _createElementVNode("span", {
                              class: _normalizeClass(["token-info-value", tokenInfo.value?.is_valid ? "success--text" : "error--text"])
                            }, [
                              _createVNode(_component_v_icon, {
                                icon: tokenInfo.value?.is_valid ? "mdi-check-circle" : "mdi-alert-circle",
                                size: "16",
                                color: tokenInfo.value?.is_valid ? "success" : "error",
                                class: "mr-1"
                              }, null, 8, ["icon", "color"]),
                              _createTextVNode(" " + _toDisplayString(tokenInfo.value?.is_valid ? "有效" : "无效"), 1)
                            ], 2)
                          ]),
                          tokenInfo.value?.is_valid && tokenInfo.value?.remaining_days !== void 0 ? (_openBlock(), _createElementBlock("div", _hoisted_55, [
                            _cache[61] || (_cache[61] = _createElementVNode("span", { class: "token-info-label font-weight-bold" }, "剩余时间：", -1)),
                            _createElementVNode("span", _hoisted_56, [
                              _createVNode(_component_v_icon, {
                                icon: "mdi-clock-outline",
                                size: "16",
                                color: "primary",
                                class: "mr-1"
                              }),
                              _createTextVNode(" " + _toDisplayString(tokenInfo.value.remaining_days) + " 天 ", 1)
                            ])
                          ])) : _createCommentVNode("", true),
                          _createElementVNode("div", _hoisted_57, [
                            _createElementVNode("div", _hoisted_58, [
                              _createVNode(_component_v_icon, {
                                icon: "mdi-key",
                                size: "16",
                                class: "mr-1",
                                color: "primary"
                              }),
                              _cache[62] || (_cache[62] = _createElementVNode("span", { class: "font-weight-bold" }, "Token内容：", -1))
                            ]),
                            _createVNode(_component_v_card, {
                              variant: "outlined",
                              class: "token-display-card"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_card_text, { class: "pa-3" }, {
                                  default: _withCtx(() => [
                                    tokenInfo.value?.token ? (_openBlock(), _createElementBlock("div", _hoisted_59, _toDisplayString(tokenInfo.value.token), 1)) : (_openBlock(), _createElementBlock("div", _hoisted_60, " Token内容不可用 "))
                                  ]),
                                  _: 1
                                })
                              ]),
                              _: 1
                            })
                          ])
                        ])
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_divider),
                    _createVNode(_component_v_card_actions, { class: "pa-4" }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_spacer),
                        _createVNode(_component_v_btn, {
                          color: "primary",
                          variant: "outlined",
                          onClick: copyTokenFromDialog,
                          class: "mr-2"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_icon, {
                              icon: "mdi-content-copy",
                              size: "16",
                              class: "mr-1"
                            }),
                            _cache[63] || (_cache[63] = _createTextVNode(" 复制Token ", -1))
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_v_btn, {
                          color: "grey",
                          variant: "text",
                          onClick: _cache[21] || (_cache[21] = ($event) => showTokenDialog.value = false)
                        }, {
                          default: _withCtx(() => [..._cache[64] || (_cache[64] = [
                            _createTextVNode(" 关闭 ", -1)
                          ])]),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }, 8, ["modelValue"])
          ]),
          _: 1
        })
      ]);
    };
  }
});

const Config = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-d17adfc8"]]);

export { Config as default };
