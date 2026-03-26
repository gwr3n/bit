__bit_widget() {
  local instruction
  local generated

  printf '\n'
  IFS= read -r -e -p 'bit> ' instruction || return 1
  [[ -n "$instruction" ]] || return 0

  generated="$(command bit "$instruction")" || return $?
  READLINE_LINE="$generated"
  READLINE_POINT=${#READLINE_LINE}
}

bind -x '"\C-x\C-b":__bit_widget'