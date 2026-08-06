#!/usr/bin/env bash
# Perfiles de modelos CDAD — fuente única del mapa (duplica ADR-001/005 y la
# tabla §2 del Contrato de roles para el perfil optimus; los perfiles
# economical/premium son opt-in del deploy). Sourced por install.sh y
# validate-subagents.sh.
#
# Uso: bash install.sh --economical | --optimus | --premium

# Perfiles: economical | optimus | premium
# (antebias innegociable en los 3: reviewer en modelo distinto al implementer)
#
# Premium — top-tier configurable por env (multi-provider por diseño). Cada rol
# es overrideable con una env; sin env, usa el default top-tier de los providers
# configurados (mofgw). El valor de env acepta CUALQUIER formato provider/model
# (p.ej. anthropic/claude-opus-4-5, openai/gpt-5.2-codex) y NO lleva prefijo
# mofgw forzado. Requisito para el override: el provider de destino debe estar
# configurado en el runtime (p.ej. opencode.jsonc).
#
#   CDAD_PREMIUM_MODEL_ARCHITECT    default mofgw/qwen3.7-max
#   CDAD_PREMIUM_MODEL_TEST_WRITER  default mofgw/glm-5.2
#   CDAD_PREMIUM_MODEL_IMPLEMENTER  default mofgw/deepseek-v4-pro
#   CDAD_PREMIUM_MODEL_REVIEWER     default mofgw/qwen3.7-max
#   CDAD_PREMIUM_MODEL_SCRIBE       default mofgw/qwen3.7-max
#
# Ejemplo: CDAD_PREMIUM_MODEL_REVIEWER=anthropic/claude-sonnet-4-5
#   (requiere tener el provider anthropic configurado en el runtime).

# cdad_model <perfil> <rol> → imprime "provider/modelo" (rol sin match → vacío).
# El orquestador NUNCA lleva model: → cdad_model devuelve vacío para ese rol.
# Ojo: en patrones case, "|" es OR — el separador literal perfil|rol se escapa
# como "\|" (cada alternativa es un (perfil, rol) explícito).
cdad_model() {
  local perfil="$1" rol="$2"
  case "$perfil|$rol" in
    # --- economical: mínimo costo — todo deepseek-v4-flash (productivo
    # barato); el reviewer cae al default qwen3.7-plus (familia DISTINTA).
    economical\|architect|economical\|test-writer|economical\|implementer|economical\|scribe)
      echo "mofgw/deepseek-v4-flash";;

    # --- optimus (perfil de diseño, default del repo): espeja la tabla §2 del
    # Contrato de roles y ADR-001/005 — architect+scribe deepseek-v4-pro,
    # test-writer glm-5.2, implementer deepseek-v4-flash; reviewer default.
    optimus\|architect|optimus\|scribe)
      echo "mofgw/deepseek-v4-pro";;
    optimus\|test-writer)
      echo "mofgw/glm-5.2";;
    optimus\|implementer)
      echo "mofgw/deepseek-v4-flash";;

    # --- premium: top-tier configurable por env — cada rol es overrideable
    # vía CDAD_PREMIUM_MODEL_<ROL> (cualquier provider/model, p.ej.
    # anthropic/openai); sin env, usa el default top-tier de los providers
    # configurados (mofgw).
    premium\|architect)
      echo "${CDAD_PREMIUM_MODEL_ARCHITECT:-mofgw/qwen3.7-max}";;
    premium\|test-writer)
      echo "${CDAD_PREMIUM_MODEL_TEST_WRITER:-mofgw/glm-5.2}";;
    premium\|implementer)
      echo "${CDAD_PREMIUM_MODEL_IMPLEMENTER:-mofgw/deepseek-v4-pro}";;
    premium\|reviewer)
      echo "${CDAD_PREMIUM_MODEL_REVIEWER:-mofgw/qwen3.7-max}";;
    premium\|scribe)
      echo "${CDAD_PREMIUM_MODEL_SCRIBE:-mofgw/qwen3.7-max}";;

    # --- default del reviewer: qwen3.7-plus en cualquier perfil (modelo
    # distinto al del implementer de ese perfil; un override de env que lo
    # iguale lo rechaza el guard anti-bias del validator).
    *\|reviewer)
      echo "mofgw/qwen3.7-plus";;
  esac
}

# cdad_valid_profile <perfil> → 0 si es soportado, 1 si no (fail fast en el
# borde: flag/env/marker). No imprime; el caller da el mensaje descriptivo.
cdad_valid_profile() {
  case "$1" in
    economical|optimus|premium) return 0 ;;
    *) return 1 ;;
  esac
}
