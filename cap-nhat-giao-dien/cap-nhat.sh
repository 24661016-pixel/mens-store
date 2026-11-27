#!/usr/bin/env bash
set -euo pipefail
project="${1:-/workspaces/mens-store/mens-store}"
ref="${2:-FETCH_HEAD}"
cd "$project"
if [[ ! -f pom.xml || ! -f compose.yaml || ! -d src/main/resources ]]; then
  echo "Khong tim thay du an Maven/Docker tai $PWD" >&2; exit 1
fi
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
git show "$ref:cap-nhat-giao-dien/mens-store-cap-nhat-giao-dien.zip" > "$work/update.zip"
printf '%s  %s\n' 'ceea426298b4dd8decf1e8e92b50cd291fd390c92a4ece85cf22dbb3e83454e2' "$work/update.zip" | sha256sum -c -
unzip -tq "$work/update.zip"
backup="$(mktemp -d "$HOME/mens-store-backup-XXXXXXXX")"
cp -a src/main/resources "$backup/resources"
if [[ -f HUONG_DAN_GIAO_DIEN_MOI.md ]]; then cp -a HUONG_DAN_GIAO_DIEN_MOI.md "$backup/"; fi
echo "Da sao luu giao dien: $backup"
if grep -Fq "customers.findByEmail(username)" src/main/java/com/example/mens_store/config/SecurityConfig.java; then
  unzip -o "$work/update.zip" -d "$PWD"
else
  echo "Chua xac nhan backend dang nhap Gmail. Chi cap nhat anh/CSS, giu nguyen form dang nhap."
  unzip -o "$work/update.zip" -x "src/main/resources/templates/home.mens.html" "HUONG_DAN_GIAO_DIEN_MOI.md" -d "$PWD"
fi
echo "Da cap nhat 20 anh va CSS. Khong sua SQL, Java, .env hay volume MySQL."
docker compose up -d --build web
docker compose ps
echo "Kiem tra docker compose logs --tail=100 web; tai lai trang bang Ctrl+F5."
