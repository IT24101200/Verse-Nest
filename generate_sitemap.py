from pathlib import Path
import argparse
from html import escape
from datetime import date
parser=argparse.ArgumentParser(description="Build sitemap.xml after choosing a public URL")
parser.add_argument("--base-url",required=True,help="e.g. https://www.example.com")
a=parser.parse_args()
base=a.base_url.rstrip('/')
root=Path(__file__).parent
paths=sorted(root.rglob('*.html'))
xml=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for p in paths:
 rel=p.relative_to(root).as_posix()
 xml.append('  <url><loc>'+escape(base+'/'+rel,quote=False)+'</loc></url>')
xml.append('</urlset>')
(root/'sitemap.xml').write_text('\n'.join(xml)+'\n',encoding='utf-8')
(root/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+base+'/sitemap.xml\n',encoding='utf-8')
print('Created sitemap.xml and updated robots.txt for',base)
