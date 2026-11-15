# VCFR connector for Calibre

This Calibre library action adds **Open with VCFR** and `Ctrl+Shift+Alt+V`. Select exactly one EPUB book in Calibre and activate the action. VCFR indexes the selected EPUB locally, opens its companion window, and uses the Markdown note configured in VCFR.

This is a **Calibre library connector**: it starts the companion with the selected file. It does not inject controls into Calibre's separate ebook-viewer window. If that viewer advertises MPRIS playback metadata, you may choose it in VCFR; compatibility depends on the viewer/version.

Requirements: install VCFR's `vcfr` launcher on PATH or set `VCFR_COMMAND` to its absolute launcher path; Calibre 6 or later; selected book has an EPUB format.

Install the packaged `VCFR-Calibre.zip` from Calibre → Preferences → Plugins → Load plugin from file. Restart Calibre after installation. The shortcut can be changed in Calibre's Keyboard shortcuts preferences.
