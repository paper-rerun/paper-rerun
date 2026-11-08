#!/bin/bash
# Download classification_models.zip (3.0 G) from the Drive folder the README links.
# Plain HTTPS, no account: the file is shared with anyone, so the confirm form is all it takes.
# regression_models.zip (4.8 G) is not downloaded: the regression targets are only a note in the report.
set -eu
DL=/mnt/e/Ciencia/noturno/2023-yuksel-selformer/dl
ID=14jLOvTQxzJfkhpY1j9OAzT1qgv8v8CFd
mkdir -p "$DL"
cd "$DL"
# Fresh confirm page, because the uuid token is short lived
curl -sL "https://drive.usercontent.google.com/download?id=${ID}&export=download" -o confirm.html
UUID=$(grep -o -E 'name="uuid" value="[^"]*"' confirm.html | head -1 | sed -E 's/.*value="([^"]*)".*/\1/')
echo "uuid=${UUID}"
curl -L --fail -o classification_models.zip \
	"https://drive.usercontent.google.com/download?id=${ID}&export=download&confirm=t&uuid=${UUID}"
ls -l classification_models.zip
sha256sum classification_models.zip | tee classification_models.zip.sha256
unzip -l classification_models.zip | tail -5
