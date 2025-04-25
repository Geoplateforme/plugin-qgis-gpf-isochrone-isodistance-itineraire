# standard
from functools import partial
from typing import Any, Callable, Dict, Optional

# pyQGIS
from qgis.core import (
    QgsApplication,
    QgsProcessingAlgorithm,
    QgsProcessingAlgRunnerTask,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsTask,
)
from qgis.PyQt.QtWidgets import QMessageBox, QTextEdit, QWidget

# project
from gpf_isochrone_isodistance_itineraire.toolbelt.processing_feedback import (
    QTextEditProcessingFeedBack,
)


class ProcessingRunTextEdit(QTextEdit):
    def __init__(self, parent: Optional[QWidget] = None):
        """Text edit to run QgsProcessingAlgorithm and display feedback

        :param parent: widget parent, defaults to None
        :type parent: Optional[QWidget], optional
        """
        super().__init__(parent)
        self.task: Optional[QgsTask] = None
        self._feedback: Optional[QgsProcessingFeedback] = None
        self.context: Optional[QgsProcessingContext] = None
        self.setReadOnly(True)
        self.setUndoRedoEnabled(False)

    def run_alg(
        self,
        alg: QgsProcessingAlgorithm,
        params: Dict[str, Any],
        executed_callback: Optional[Callable],
        *args,
    ):
        """Run algorithm and display feedback in text edit.

        If executed_callback is defined it must have arguments for context and task return

        Example:
            def _isoservice_computed(self, context : QgsProcessingContext, successful :bool, results : Dict[str,Any]) -> None:

        :param alg: algorithm to run
        :type alg: QgsProcessingAlgorithm
        :param params: algorithm parameters
        :type params: Dict[str,Any]
        :param executed_callback: callback to call after execution
        :type executed_callback: Callable
        """

        self.context = QgsProcessingContext()
        res, error = alg.checkParameterValues(params, self.context)
        if res:
            self.clear()
            self._feedback = QTextEditProcessingFeedBack(self)
            self._task = QgsProcessingAlgRunnerTask(
                alg, params, self.context, self._feedback
            )
            if executed_callback:
                self._task.executed.connect(
                    partial(executed_callback, self.context, *args)
                )
            QgsApplication.taskManager().addTask(self._task)
        else:
            QMessageBox.critical(
                self,
                self.tr("Can't run {0}".format(alg.name())),
                self.tr("Invalid parameters : {0}.".format(error)),
            )
