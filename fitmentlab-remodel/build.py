"""Build site.html (artifact body) and index.html (standalone page) from src.html."""
import json, pathlib, re
root = pathlib.Path(__file__).parent
data = json.dumps(json.load(open(root / 'assets/fitment-data.json')), separators=(',', ':'))
src = (root / 'src.html').read_text().replace('__FITMENT_DATA__', data)
(root / 'site.html').write_text(src)
head, body = src.split('</style>', 1)
(root / 'index.html').write_text(
    '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    '<meta name="description" content="Custom wheels and tires with guaranteed fitment for your exact vehicle. $0 down financing, 100 days no interest.">\n'
    + head + '</style>\n</head>\n<body>' + body + '</body>\n</html>\n')
