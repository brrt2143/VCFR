# Bóveda de demostración VCFR

Esta bóveda contiene **Don Quijote** de Miguel de Cervantes, descargado en EPUB desde Project Gutenberg, y una nota de lectura capturada con VCFR. El libro está dentro de `01-Libros/Don Quijote/`; el ejemplo de nota está en `03-Notas/`.

Para repetir la demostración en Linux desde la raíz del proyecto:

```bash
.venv/bin/python -m vcfr.app \
  --book "demo-vault/01-Libros/Don Quijote/Don Quijote - Gutenberg 2000.epub" \
  --note "demo-vault/03-Notas/Don Quijote - Notas de lectura.md"
```

En Readest, abre el EPUB, inicia «Leer en voz alta» y en VCFR selecciona **Detectar lector**. Di «VCFR, guarda este párrafo». La confirmación aparece sin pausar el lector. También puedes usar el botón. En una primera ejecución, la app crea su índice privado en la caché local.

Project Gutenberg identifica la obra como española y ofrece el archivo en su colección; verifica siempre las condiciones locales antes de redistribuir una obra. El EPUB conserva su aviso de fuente y los términos incluidos por Project Gutenberg. La licencia MIT de VCFR **no cubre el libro**.

Fuente: [Project Gutenberg, eBook 2000 — Don Quijote](https://www.gutenberg.org/ebooks/2000).
