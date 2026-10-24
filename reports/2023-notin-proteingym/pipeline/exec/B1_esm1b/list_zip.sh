#!/bin/bash
# Show the layout of the authors' scores zip: entry count and the header of one file
Z=/mnt/e/Ciencia/pipeline/2023-notin-proteingym/data/zero_shot_substitutions_scores.zip
zipinfo -1 "$Z" | wc -l
zipinfo -1 "$Z" | grep -v '\.csv$' | head
unzip -p "$Z" B2L11_HUMAN_Dutta_2010_binding-Mcl-1.csv | head -2
