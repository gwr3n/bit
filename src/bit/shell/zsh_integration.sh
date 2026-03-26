function bit() {
  if [[ ! -o interactive ]]; then
    command bit "$@"
    return $?
  fi

  case "${1-}" in
    ""|--help|-h|--setup|--print-shell-integration)
      command bit "$@"
      return $?
      ;;
  esac

  local generated
  generated="$(command bit "$@")" || return $?
  print -z -- "$generated"
}

function __bit_widget() {
  local generated

  zle -I
  [[ -n "$BUFFER" ]] || return 0
  generated="$(command bit "$BUFFER")" || return $?
  BUFFER="$generated"
  CURSOR=${#BUFFER}
}

zle -N __bit_widget
bindkey '^X^B' __bit_widget