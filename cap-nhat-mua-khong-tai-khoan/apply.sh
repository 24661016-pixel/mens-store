#!/usr/bin/env bash
set -euo pipefail
project="$(realpath "${1:-/workspaces/mens-store/mens-store}")"
ref="${2:-FETCH_HEAD}"
[[ -f "$project/pom.xml" && -f "$project/compose.yaml" && -d "$project/src" ]] || { echo "Khong tim thay du an: $project" >&2; exit 1; }
repo="$(git -C "$project" rev-parse --show-toplevel)"
ref="$(git -C "$repo" rev-parse "$ref")"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/initial" "$tmp/staged" "$tmp/stage-backup"
cp -a "$project/src" "$tmp/initial/"
cp -a "$tmp/initial/src" "$tmp/staged/"
cp "$project/pom.xml" "$project/compose.yaml" "$tmp/staged/"
for n in 1 2 3 4; do
  git -C "$repo" show "$ref:cap-nhat-size-khach/patch.part$n" >> "$tmp/patch.json.gz"
done
printf '%s  %s\n' 'd59b67503c34af2f9ec1976f49aadcffd8d16fee06f8375f2448c176970bc89c' "$tmp/patch.json.gz" | sha256sum -c -
for name in apply.py sync.py verify.py; do
  git -C "$repo" show "$ref:cap-nhat-mua-khong-tai-khoan/$name" > "$tmp/$name"
done
prereq() {
  local folder="$1"
  local marker="$2"
  if [[ ! -f "$tmp/staged/$marker" ]]; then
    echo "Kiem tra cap nhat dieu kien: $folder"
    git -C "$repo" show "$ref:$folder/apply.py.gz" > "$tmp/prereq.gz"
    gzip -dc "$tmp/prereq.gz" > "$tmp/prereq.py"
    HOME="$tmp/stage-backup" python3 -E "$tmp/prereq.py" "$tmp/staged"
  fi
}
prereq cap-nhat-mua-ngay src/main/java/com/example/mens_store/controller/DirectCheckoutController.java
prereq cap-nhat-ton-kho src/main/resources/static/assets/js/stock-quantity.js
prereq cap-nhat-bang-size src/main/java/com/example/mens_store/model/SizeGuide.java
HOME="$tmp/stage-backup" python3 -E "$tmp/apply.py" "$tmp/staged" "$tmp/patch.json.gz" d59b67503c34af2f9ec1976f49aadcffd8d16fee06f8375f2448c176970bc89c
if command -v node >/dev/null; then
  node --check "$tmp/staged/src/main/resources/static/assets/js/home-store.js"
fi
python3 -E "$tmp/sync.py" "$project" "$tmp/staged" "$tmp/initial"
cd "$project"
docker compose build web
docker compose up -d web
docker compose ps
if ! python3 -E "$tmp/verify.py"; then
  echo 'Chua xac nhan duoc web dang chay. Gui loi KIEM TRA CHUA DAT cho ChatGPT. Khong xoa SQL.' >&2
  exit 1
fi
