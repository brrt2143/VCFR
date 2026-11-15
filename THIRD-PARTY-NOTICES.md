# Avisos de materiales de terceros

## Don Quijote — Project Gutenberg eBook #2000

El EPUB de demostración `demo-vault/01-Libros/Don Quijote/Don Quijote - Gutenberg 2000.epub` fue descargado de [Project Gutenberg, eBook 2000](https://www.gutenberg.org/ebooks/2000). Conserva dentro del propio EPUB la atribución, el aviso de marca y los términos de Project Gutenberg. Esos términos son independientes de la licencia MIT del software VCFR. Antes de redistribuir el EPUB, consulta la [política de derechos de Project Gutenberg](https://www.gutenberg.org/policy/permission.html) y la [licencia de los archivos](https://www.gutenberg.org/policy/license.html), además de la normativa aplicable en tu jurisdicción.

## Vosk

VCFR puede usar Vosk para reconocimiento local de voz. Vosk se distribuye bajo Apache License 2.0. El modelo de idioma español se descarga por separado y puede tener sus propios términos; revisa la licencia que acompaña al modelo elegido.

## eSpeak NG

La voz local opcional utiliza el programa instalado `espeak-ng`; VCFR no incluye ni redistribuye el binario. El audio de la demo se generó con él en el equipo. [Código y licencia](https://github.com/espeak-ng/espeak-ng).

## Dependencias y herramientas de desarrollo

- [Vosk API](https://github.com/alphacep/vosk-api): Apache-2.0. Cada modelo acústico conserva sus propios términos.
- [Requests](https://github.com/psf/requests): Apache-2.0.
- [Pillow](https://github.com/python-pillow/Pillow): HPND; se usa para dibujar las escenas de la demo.
- [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo): MIT; se ejecutó en modo local para preparar las escenas. No se copió su código al repositorio VCFR.
- [FFmpeg](https://github.com/FFmpeg/FFmpeg): se usó para codificar y unir el video. Los términos dependen de las opciones de compilación de FFmpeg instalada; VCFR no redistribuye el ejecutable.
- [Calibre](https://github.com/kovidgoyal/calibre), [Readest](https://github.com/readest/readest), [LM Studio](https://github.com/lmstudio-ai) y [Ollama](https://github.com/ollama/ollama) son aplicaciones o integraciones opcionales; VCFR no incluye sus binarios.

Las herramientas de transcripción enlazadas en el roadmap, [whisper.cpp](https://github.com/ggml-org/whisper.cpp) y [faster-whisper](https://github.com/SYSTRAN/faster-whisper), no forman parte de esta versión y no se redistribuye código suyo.
