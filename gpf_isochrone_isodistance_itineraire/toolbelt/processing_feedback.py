import sys
from typing import Optional

from qgis.core import QgsProcessingFeedback
from qgis.PyQt.QtCore import pyqtSignal, pyqtSlot
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QTextEdit


class QTextEditProcessingFeedBack(QgsProcessingFeedback):
    insert_text_color = pyqtSignal(str, QColor)

    def __init__(self, text_edit: QTextEdit):
        """QgsProcessingFeedback to display feedback in a QTextEdit

        :param text_edit: text edit to display feedback
        :type text_edit: QTextEdit
        """
        super().__init__()
        self._text_edit = text_edit

        # Define font depending on platform
        if sys.platform.startswith("win"):
            self._text_edit.setFontFamily("Courier New")
        else:
            self._text_edit.setFontFamily("monospace")

        self._text_edit.setReadOnly(True)
        self._text_edit.setUndoRedoEnabled(False)

        self.insert_text_color.connect(self._change_color_and_insert_text)

    def setProgressText(self, text: Optional[str]):
        """Sets a progress report text string. This can be used in conjunction with setProgress() to provide detailed progress reports, such as “Transformed 4 of 5 layers”.

        :param text: progress text
        :type text: Optional[str]
        """
        super().setProgressText(text)
        self.pushInfo(text)

    def pushWarning(self, warning: Optional[str]):
        """Pushes a warning informational message from the algorithm. This should only be used sparsely as to maintain the importance of visual queues associated to this type of message.

        :param warning: warning text
        :type warning: Optional[str]
        """
        super().pushWarning(warning)
        self.insert_text_color.emit(warning, QColor("orange"))

    def pushInfo(self, info: Optional[str]):
        """Pushes a general informational message from the algorithm. This can be used to report feedback which is neither a status report or an error, such as “Found 47 matching features”.

        :param info: info text
        :type info: Optional[str]
        """
        super().pushInfo(info)
        self.insert_text_color.emit(info, QColor("black"))

    def pushCommandInfo(self, info: str):
        """Pushes an informational message containing a command from the algorithm. This is usually used to report commands which are executed in an external application or as subprocesses.

        :param info: info text
        :type info: Optional[str]
        """
        super().pushCommandInfo(info)
        self.pushInfo(info)

    def pushDebugInfo(self, info: Optional[str]):
        """Pushes an informational message containing debugging helpers from the algorithm.

        :param info: info text
        :type info: Optional[str]
        """
        super().pushDebugInfo(info)
        self.pushInfo(info)

    def pushConsoleInfo(self, info: Optional[str]):
        """Pushes a console feedback message from the algorithm. This is used to report the output from executing an external command or subprocess.

        :param info: info text
        :type info: Optional[str]
        """
        super().pushConsoleInfo(info)
        self.pushInfo(info)

    def reportError(self, error: Optional[str], fatalError=False):
        """Reports that the algorithm encountered an error while executing.

           If fatalError is True then the error prevented the algorithm from executing.

        :param error: error text
        :type error: Optional[str]
        :param fatalError: fatal error bool, defaults to False
        :type fatalError: bool, optional
        """
        super().reportError(error, fatalError)
        self.insert_text_color.emit(error, QColor("red"))

    @pyqtSlot(str, QColor)
    def _change_color_and_insert_text(self, text: Optional[str], color: QColor):
        """Change current text edit color and insert text

        :param text: text to insert
        :type text: Optional[str]
        :param color: color
        :type color: QColor
        """
        if text:
            self._text_edit.setTextColor(color)
            self._text_edit.append(text)
            sb = self._text_edit.verticalScrollBar()
            sb.setValue(sb.maximum())
