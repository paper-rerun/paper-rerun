"""Dumps the authors' sampling spreadsheet so the band comes from their own dispersion.

Run it with -P and the path as an argument: the file is a download, and nothing in it
should be able to reach this script's folder.
"""
import sys
import openpyxl

wb = openpyxl.load_workbook(sys.argv[1], data_only=True)
out = []
for name in wb.sheetnames:
	ws = wb[name]
	out.append("=== sheet %r  %dx%d ===" % (name, ws.max_row, ws.max_column))
	for row in ws.iter_rows(values_only=True):
		if any(c is not None for c in row):
			out.append(" | ".join("" if c is None else str(c) for c in row))
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write("\n".join(out))
