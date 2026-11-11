import sys, zipfile, re
p = sys.argv[1]
z = zipfile.ZipFile(p)
wb = z.read('xl/workbook.xml').decode('utf-8')
for m in re.finditer(r'<sheet[^>]*name="([^"]+)"', wb):
    print(m.group(1))
