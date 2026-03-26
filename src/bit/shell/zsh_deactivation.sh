bindkey -r '^X^B' 2>/dev/null || true
zle -D __bit_widget 2>/dev/null || true
unfunction __bit_widget 2>/dev/null || true
unfunction bit 2>/dev/null || true