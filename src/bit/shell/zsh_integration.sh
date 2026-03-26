function __bit_widget() {
  local generated

  zle -I
  [[ -n "$BUFFER" ]] || return 0
  generated="$(command bit --print-only "$BUFFER")" || return $?
  BUFFER="$generated"
  CURSOR=${#BUFFER}
}

zle -N __bit_widget
bindkey '^X^B' __bit_widget