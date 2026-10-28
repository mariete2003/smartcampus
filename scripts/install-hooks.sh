#!/bin/sh
# Ejecutar una vez después de clonar: sh scripts/install-hooks.sh
git config core.hooksPath hooks
chmod +x hooks/* 2>/dev/null
git config alias.publish '!f() { git push "$@" && sh hooks/post-push; }; f'
echo "✅ Hooks instalados. Usa 'git publish' en lugar de 'git push'."