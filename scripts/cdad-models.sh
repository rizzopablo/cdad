#!/usr/bin/env bash
# Perfiles de modelos CDAD — fuente única del mapa (duplica ADR-001/005 y la
# tabla §2 del Contrato de roles para el perfil optimus; los perfiles
# economical/premium son opt-in del deploy). Sourced por install.sh y
# validate-subagents.sh.
#
# Uso: bash install.sh --economical | --optimus | --premium

# Perfiles: economical | optimus | premium
# (antebias innegociable en los 3: reviewer en familia distinta al implementer)

# cdad_model <perfil> <rol> → imprime "mofgw/<modelo>" (rol sin match → vacío).
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

    # --- premium: máxima calidad — architect+reviewer qwen3.7-max,
    # implementer+scribe deepseek-v4-pro, test-writer glm-5.2.
    premium\|architect|premium\|reviewer)
      echo "mofgw/qwen3.7-max";;
    premium\|implementer|premium\|scribe)
      echo "mofgw/deepseek-v4-pro";;
    premium\|test-writer)
      echo "mofgw/glm-5.2";;

    # --- default del reviewer: qwen3.7-plus en cualquier perfil (familia
    # siempre distinta a la del implementer de ese perfil).
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
