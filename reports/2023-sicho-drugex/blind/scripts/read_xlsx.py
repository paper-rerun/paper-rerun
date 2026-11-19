import sys, openpyxl
wb = openpyxl.load_workbook(sys.argv[1], data_only=True)
for ws in wb.worksheets:
    print("=== SHEET:", ws.title, ws.dimensions)
    for row in ws.iter_rows(values_only=True):
        if any(c is not None for c in row):
            print(row)
