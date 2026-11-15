"""Small Calibre library action that launches the separate VCFR app."""
import os
import shutil
import tempfile
from pathlib import Path

from calibre.gui2.actions import InterfaceAction
from qt.core import QMessageBox, QProcess


class VCFRAction(InterfaceAction):
    name = "VCFR"
    action_spec = (
        "Open with VCFR",
        None,
        "Open the selected EPUB in the VCFR voice companion",
        "Ctrl+Shift+Alt+V",
    )

    def genesis(self):
        self.qaction.triggered.connect(self.open_selected_book)
        self._vcfr_temporary_copies = []

    def open_selected_book(self):
        selected = self.gui.library_view.get_selected_ids()
        if len(selected) != 1:
            QMessageBox.information(
                self.gui, "VCFR", "Select one book in the Calibre library first."
            )
            return
        db = self.gui.current_db.new_api
        book_id = selected[0]
        formats = db.formats(book_id) or []
        if "EPUB" not in formats:
            QMessageBox.warning(
                self.gui,
                "VCFR",
                "This first connector needs an EPUB format for the selected book.",
            )
            return
        copied_book = Path(tempfile.mkdtemp(prefix="vcfr-calibre-")) / "book.epub"
        with copied_book.open("wb") as output:
            db.copy_format_to(book_id, "EPUB", output)
            output.flush()
        self._vcfr_temporary_copies.append(copied_book)
        book_path = str(copied_book)
        executable = os.environ.get("VCFR_COMMAND") or shutil.which("vcfr")
        if not executable:
            QMessageBox.warning(
                self.gui,
                "VCFR is not installed on PATH",
                "Install VCFR and add its launcher to PATH, or set VCFR_COMMAND to the launcher path.",
            )
            return
        ok, process_id = QProcess.startDetached(executable, ["--book", book_path])
        if not ok:
            QMessageBox.warning(
                self.gui,
                "Could not start VCFR",
                "Check that VCFR_COMMAND points to the VCFR launcher.",
            )
