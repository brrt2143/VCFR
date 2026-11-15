# Video de demostración

`VCFR-Demo.mp4` presenta las funciones principales de VCFR con escenas gráficas hechas para el proyecto y narración sintética en español. No utiliza imágenes de stock ni audio grabado de una persona.

El texto está en [`narration-es.txt`](narration-es.txt); las imágenes fuente se generan con [`build_demo_scenes.py`](build_demo_scenes.py). [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) ayudó a preparar las escenas iniciales; [`build_video.sh`](build_video.sh) y [FFmpeg](https://github.com/FFmpeg/FFmpeg) componen y codifican el MP4. La narración se generó localmente con [Piper](https://github.com/OHF-Voice/piper1-gpl), usando la voz neural de español mexicano `es_MX-claude-high`; las ilustraciones se dibujaron con [Pillow](https://github.com/python-pillow/Pillow). No se usaron claves de API ni servicios remotos para producirlo.

Para regenerar el audio y el MP4, instala `piper-tts` con `python3 -m pip install piper-tts`, instala FFmpeg y ejecuta [`build_video.sh`](build_video.sh). El script descarga el modelo de voz de alta calidad (aprox. 63 MB) a `demo/.models/`; los pesos no se incluyen en el repositorio. Las siete imágenes fuente ya están en `frames/`. Puedes escoger otra voz de español en el catálogo de [Piper Voices](https://huggingface.co/rhasspy/piper-voices/tree/main/es).

Las herramientas mencionadas conservan sus licencias y marcas originales; la licencia MIT de VCFR se aplica al código propio del proyecto.
