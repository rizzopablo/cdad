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
  # basic: SIN modelos fijos — los agentes heredan el modelo por default del
  # runtime (portable entre providers; útil cuando el provider principal se
  # agota y se switch a otro, o con un solo modelo disponible). Trade-off
  # documentado en ADR-007: el anti-bias reviewer≠implementer NO es garantizado
  # por el instalador en este perfil (configuración manual si se necesita).
  [ "$perfil" = "basic" ] && return 0
  case "$perfil|$rol" in
    # --- variantes Odoo (*-odoo): modelos FIJOS por rol (ADR-007), iguales en
    # cualquier perfil (stack="odoo" en docs/.cdad-state.json delega a estas
    # variantes). Puestos PRIMERO a propósito: son los patrones más específicos
    # (sufijo "-odoo" exacto) e independientes del perfil, así el orden de los
    # bloques genéricos de abajo NO es load-bearing — ningún patrón genérico
    # (p.ej. *\|reviewer) puede sombrearlos aunque se reordene el case.
    *\|architect-odoo)
      echo "mofgw/deepseek-v4-pro";;
    *\|test-writer-odoo)
      echo "mofgw/glm-5.2";;
    *\|implementer-odoo)
      echo "mofgw/deepseek-v4-flash";;
    *\|reviewer-odoo)
      echo "mofgw/qwen3.7-plus";;
    *\|scribe-odoo)
      echo "mofgw/deepseek-v4-pro";;

    # --- economical (enmienda 2026-08-24): ejecución barata con calidad en
    # los puntos críticos — architect sube a deepseek-v4-pro (la precisión
    # del spec es la carga crítica del ciclo), roles de ejecución en
    # deepseek-v4-flash, reviewer en minimax-m3 (familia DISTINTA a
    # deepseek; reemplaza a qwen3.7-plus — reporte del dueño: fallas
    # recurrentes; minimax-m3 además 25% más barato: 0.30/1.20 vs 0.40/1.60).
    economical\|architect)
      echo "mofgw/deepseek-v4-pro";;
    economical\|reviewer)
      echo "mofgw/minimax-m3";;
    economical\|test-writer|economical\|implementer|economical\|scribe)
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
    # iguale lo rechaza el guard anti-bias del validator). Por la regla
    # first-match de case, colocado DESPUÉS de las variantes -odoo y de los
    # perfiles explícitos: no genera falso default para reviewer-odoo (el
    # patrón *\|reviewer no hace full-match de "…reviewer-odoo").
    *\|reviewer)
      echo "mofgw/qwen3.7-plus";;
  esac
}

# cdad_model_claude <perfil> <rol> → imprime "alias o model-id" para Claude Code.
# Claude Code no tiene mofgw gateway (solo Anthropic-native models), así que
# devolvemos alias (haiku/sonnet/opus/fable).
# Invariante: reviewer ≠ implementer (debilitado respecto a OpenCode pero
# igualmente exigido).
cdad_model_claude() {
  local perfil="$1" rol="$2"
  # basic: SIN modelos fijos — mismos trade-offs que cdad_model (ADR-007).
  [ "$perfil" = "basic" ] && return 0
  case "$perfil|$rol" in
    # --- economical: haiku para todo salvo reviewer (que sube a opus para
    # family diversity). NOTA: en Claude Code, economical|reviewer=haiku rompe
    # el invariante "familia distinta" si lo combinamos con economical|implementer=haiku
    # (ambos son modelo Anthropic). ADR-008 documenta esto como limitación aceptada.
    economical\|architect|economical\|test-writer|economical\|implementer|economical\|scribe)
      echo "haiku";;

    # --- optimus (perfil de diseño para Claude Code): sonnet architect/scribe
    # (análogo a deepseek-v4-pro de costo-balance), sonnet test-writer (análogo
    # a glm-5.2 specialized), haiku implementer (fast/cheap), opus reviewer
    # (distinta familia, análogo a qwen3.7-plus).
    optimus\|architect|optimus\|scribe|optimus\|test-writer)
      echo "sonnet";;
    optimus\|implementer)
      echo "haiku";;

    # --- premium: opus architect/scribe/reviewer, sonnet test-writer, opus implementer.
    premium\|architect|premium\|scribe|premium\|reviewer|premium\|implementer)
      echo "opus";;
    premium\|test-writer)
      echo "opus";;  # mejora respecto a optimus

    # --- default del reviewer: opus (distinto a implementer en cualquier perfil).
    *\|reviewer)
      echo "opus";;
  esac
}

# cdad_valid_profile <perfil> → 0 si es soportado, 1 si no (fail fast en el
# borde: flag/env/marker). No imprime; el caller da el mensaje descriptivo.
cdad_valid_profile() {
  case "$1" in
    economical|optimus|premium|basic) return 0 ;;
    *) return 1 ;;
  esac
}
