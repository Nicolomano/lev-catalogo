"""Genera el catálogo público a partir del volcado de la base de la página de stock.
Uso: python3 build_catalog.py <dir_productos> <config.json> <contacto.json> <template> <salida> <fecha dd/mm/aaaa>"""
import json, glob, math, os, sys

prod_dir, cfg_path, contacto_path, tpl, out, fecha = sys.argv[1:7]
cfg = json.load(open(cfg_path)); cfg = cfg.get('data', cfg) if 'tc' not in cfg else cfg
contacto = json.load(open(contacto_path))
tc = cfg['tc']; dec = cfg['decants']
fotos_ok = set(os.path.splitext(f)[0] for f in os.listdir(os.path.join(os.path.dirname(out), 'fotos')))

def redondear(x, step):
    return math.ceil(x / step) * step if step else round(x)

MARCAS_ARABES = ['lattafa','lattafa pride','armaf','afnan','al haramain','rasasi','maison alhambra','french avenue','rayhaan','stella dustin','bharara','fragrance world','paris corner','ard al zaafaran','zimaya','emper','khadlaj','swiss arabian','nabeel','al wataniah','ajmal','orientica','arabiyat','asdaaf','gulf orchid','al rehab','ahmed al maghribi','dumont','reef']

def cat_de(p):
    # mismo criterio que la página de stock: p.cat si está cargado, si no por marca
    if p.get('cat') in ('arabe', 'disenador'): return p['cat']
    return 'arabe' if (p.get('marca') or '').strip().lower() in MARCAS_ARABES else 'disenador'

def fijo(cat, ml):
    if dec.get('modo') != 'fijo': return None
    v = ((dec.get('fijos') or {}).get(cat) or {}).get(str(ml if ml % 1 else int(ml)))
    return None if v in (None, '') else float(v)

def env(ml):
    e = (dec.get('envases') or {}).get(str(ml if ml % 1 else int(ml)))
    return float(e) if e is not None else float(dec.get('envase') or 0)

frascos, decants = [], []
for f in glob.glob(os.path.join(prod_dir, '*.json')):
    d = json.load(open(f)); p = d.get('data', d)
    foto = ('fotos/' + p['foto'] + '.jpg') if p.get('foto') in fotos_ok else None
    base = {'nombre': p['nombre'].strip(), 'marca': (p.get('marca') or '').strip(), 'foto': foto}
    frascos.append(dict(base, ml=p.get('ml'), stock=p.get('stock') or 0, precio=p.get('precio')))
    if p.get('decant') and p.get('costoUsd') is not None and (p.get('ml') or 0) > 0:
        m = p.get('decMargen'); m = dec.get('margen', 0) if m is None else m
        tabla = []; cat = cat_de(p)
        for ml in dec['tamanos']:
            fx = fijo(cat, ml)
            if fx is not None:
                tabla.append({'ml': ml, 'precio': fx}); continue
            costo = p['costoUsd'] * tc / p['ml'] * ml + env(ml)
            tabla.append({'ml': ml, 'precio': redondear(costo * (1 + m / 100), dec.get('redondeo') or 0)})
        agot = p.get('mlDecant') is not None and p['mlDecant'] < min(dec['tamanos'])
        decants.append(dict(base, decants=tabla, agotado=agot, cat=cat))

# mismo perfume cargado dos veces (otro proveedor): se muestra una sola tarjeta con el stock sumado y el precio más alto
merged = {}
for x in frascos:
    k = (x['nombre'].lower(), x['marca'].lower(), x['ml'])
    if k in merged:
        y = merged[k]; y['stock'] += x['stock']; y['foto'] = y['foto'] or x['foto']
        if x['precio'] is not None and (y['precio'] is None or x['precio'] > y['precio']): y['precio'] = x['precio']
    else: merged[k] = dict(x)
frascos = list(merged.values())
key = lambda x: (x['marca'].lower(), x['nombre'].lower())
frascos.sort(key=lambda x: (not x['stock'] > 0,) + key(x))
decants.sort(key=lambda x: (x['agotado'],) + key(x))
promo = dec.get('promo') or {}
data = {'frascos': frascos, 'decants': decants, 'actualizado': fecha, 'promo': {'min': int(promo.get('min') or 0), 'pct': promo.get('pct') or 0}}
html = open(tpl).read().replace('__DATA__', json.dumps(data, ensure_ascii=False)).replace('__CONTACTO__', json.dumps(contacto, ensure_ascii=False))
open(out, 'w').write(html)
print('frascos', len(frascos), 'disponibles', sum(1 for x in frascos if x['stock'] > 0), 'decants', len(decants), 'con foto', sum(1 for x in frascos if x['foto']))
