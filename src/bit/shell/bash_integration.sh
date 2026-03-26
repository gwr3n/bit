__bit_widget() {
  local generated

  [[ -n "$READLINE_LINE" ]] || return 0
  generated="$(command bit --print-only "$READLINE_LINE")" || return $?
  READLINE_LINE="$generated"
  READLINE_POINT=${#READLINE_LINE}
}

bind -x '"\C-x\C-b":__bit_widget'