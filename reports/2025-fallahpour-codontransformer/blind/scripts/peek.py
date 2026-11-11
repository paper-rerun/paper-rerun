import sys, openpyxl
wb = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True)
for ws in wb.worksheets:
    print("=== SHEET:", ws.title, " dims:", ws.max_row, "x", ws.max_column)
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        cells = ["" if c is None else (str(c)[:38] + ("..." if len(str(c)) > 38 else "")) for c in row[:12]]
        print(i, " | ".join(cells))
        if i >= 3:
            break
