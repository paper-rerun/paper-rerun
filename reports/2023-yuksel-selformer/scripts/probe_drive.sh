#!/bin/bash
# Ask Google Drive for the name and size behind each file id in the finetuned-models folder
set -u
for id in 1O1LfFaisE029wuGY3ajR9mkpGMt04vLz 14jLOvTQxzJfkhpY1j9OAzT1qgv8v8CFd; do
	echo "== $id"
	curl -sL "https://drive.usercontent.google.com/download?id=${id}&export=download" -o /tmp/conf_${id}.html
	grep -o -E '(classification_models|regression_models)\.zip' /tmp/conf_${id}.html | sort -u
	grep -o -E '\([0-9.]+[MG]\)' /tmp/conf_${id}.html | sort -u
	grep -o -E 'name="(confirm|uuid|at)" value="[^"]*"' /tmp/conf_${id}.html | sort -u
done
