import openpyxl, sys
wb = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True)
print(wb.sheetnames)
for name in wb.sheetnames:
    if not name.startswith('Fig2b'): continue
    ws = wb[name]
    rows = list(ws.iter_rows(values_only=True))
    print('###', name, 'rows=', len(rows))
    for r in rows[:8]: print(r)
    print('...')
    for r in rows[-4:]: print(r)
