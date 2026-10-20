# Catálogo Lev Importados

Sitio público del catálogo: https://nicolomano.github.io/lev-catalogo/

Se genera a partir de la página privada de stock (en Claude) y se actualiza solo dos veces por día.
No editar `index.html` a mano: se pisa en cada actualización. Para cambiar el diseño, editar `build/template.html`.

- `index.html` — el catálogo generado.
- `fotos/` — fotos de los productos (copiadas de la página de stock, máx. 800 px).
- `build/template.html` — plantilla del sitio.
- `build/build_catalog.py` — arma `index.html` desde los datos de stock:
  `python3 build/build_catalog.py <dir_productos> <config.json> build/contacto.json build/template.html <salida/index.html> <dd/mm/aaaa>`
  (busca las fotos disponibles en `<salida>/fotos/`).
- `build/contacto.json` — WhatsApp e Instagram para los botones de consulta.
