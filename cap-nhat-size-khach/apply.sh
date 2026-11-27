#!/usr/bin/env bash
set -euo pipefail
project="$(realpath "${1:-/workspaces/mens-store/mens-store}")"
ref="${2:-FETCH_HEAD}"
[[ -f "$project/pom.xml" && -f "$project/compose.yaml" ]] || { echo "Khong tim thay du an: $project" >&2; exit 1; }
repo="$(git -C "$project" rev-parse --show-toplevel)"
ref="$(git -C "$repo" rev-parse "$ref")"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
for n in 1 2 3 4; do
  git -C "$repo" show "$ref:cap-nhat-size-khach/patch.part$n" >> "$tmp/patch.json.gz"
done
printf '%s  %s\n' 'd59b67503c34af2f9ec1976f49aadcffd8d16fee06f8375f2448c176970bc89c' "$tmp/patch.json.gz" | sha256sum -c -
git -C "$repo" show "$ref:cap-nhat-size-khach/apply.py" > "$tmp/apply.py"
prereq() {
  local folder="$1"
  local marker="$2"
  if [[ ! -f "$project/$marker" ]]; then
    echo "Cap nhat dieu kien: $folder"
    git -C "$repo" show "$ref:$folder/apply.py.gz" > "$tmp/prereq.gz"
    gzip -dc "$tmp/prereq.gz" > "$tmp/prereq.py"
    python3 "$tmp/prereq.py" "$project"
  fi
}
prereq cap-nhat-mua-ngay src/main/java/com/example/mens_store/controller/DirectCheckoutController.java
prereq cap-nhat-ton-kho src/main/resources/static/assets/js/stock-quantity.js
prereq cap-nhat-bang-size src/main/java/com/example/mens_store/model/SizeGuide.java
python3 "$tmp/apply.py" "$project" "$tmp/patch.json.gz" d59b67503c34af2f9ec1976f49aadcffd8d16fee06f8375f2448c176970bc89c
cd "$project"
docker compose build web
docker compose up -d --no-deps web
docker compose ps
echo "Kiem tra: docker compose logs --tail=100 web"
