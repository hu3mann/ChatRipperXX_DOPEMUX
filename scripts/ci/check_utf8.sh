    #!/usr/bin/env bash
    set -euo pipefail

    # Validate that all tracked text files are valid UTF-8.
    # Excludes common binary extensions.
    mapfile -d '' files < <(git ls-files -z)
    bad=()
    for f in "${files[@]}"; do
      case "$f" in
        *.png|*.jpg|*.jpeg|*.gif|*.ico|*.pdf|*.zip|*.gz|*.7z|*.bz2|*.xz|*.tar|*.tgz|*.woff|*.woff2|*.ttf|*.otf|*.mp4|*.mov|*.webm|*.so|*.dylib|*.a|*.bin|*.ico|*.icns)
          continue
          ;;
      esac
      if ! iconv -f UTF-8 -t UTF-8 "$f" >/dev/null 2>&1; then
        bad+=("$f")
      fi
    done

    if ((${#bad[@]})); then
      echo "❌ Non-UTF-8 files detected:"
      printf '%s
' "${bad[@]}"
      exit 1
    fi
    echo "✅ UTF-8 check passed."
