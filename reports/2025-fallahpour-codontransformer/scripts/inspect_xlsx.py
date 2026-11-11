"""List the sheets, headers and first rows of a Source Data workbook."""
import sys
import openpyxl

for path in sys.argv[1:]:
    print("=" * 70)
    print(path)
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    for ws in wb.worksheets:
        print(f"\nSHEET {ws.title!r}  rows={ws.max_row} cols={ws.max_column}")
        for i, row in enumerate(ws.iter_rows(max_row=3, values_only=True)):
            cells = [(str(c)[:45] if c is not None else None) for c in row[:14]]
            print(f"  r{i}: {cells}")
    wb.close()
