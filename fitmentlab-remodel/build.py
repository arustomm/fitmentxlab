"""Build each concept from its src*.html into <name>.html (artifact body) and <name>-standalone page.

src.html            -> site.html + index.html
src-showroom.html   -> showroom.html + showroom/index.html
src-stance.html     -> stance.html + stance/index.html
"""
import json, pathlib
root = pathlib.Path(__file__).parent
data = json.dumps(json.load(open(root / 'assets/fitment-data.json')), separators=(',', ':'))
DESC = '<meta name="description" content="Custom wheels and tires with guaranteed fitment for your exact vehicle. $0 down financing, 100 days no interest.">\n'

def standalone(src, assets_prefix):
    head, body = src.split('</style>', 1)
    page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + DESC + head + '</style>\n</head>\n<body>' + body + '</body>\n</html>\n')
    return page.replace('"assets/', f'"{assets_prefix}assets/') if assets_prefix else page

for src_name, out, index in [('src.html', 'site.html', 'index.html'),
                             ('src-showroom.html', 'showroom.html', 'showroom/index.html'),
                             ('src-stance.html', 'stance.html', 'stance/index.html')]:
    src = (root / src_name).read_text().replace('__FITMENT_DATA__', data)
    (root / out).write_text(src)
    idx = root / index
    idx.parent.mkdir(exist_ok=True)
    page = standalone(src, '' if idx.parent == root else '../')
    idx.write_text(page)
