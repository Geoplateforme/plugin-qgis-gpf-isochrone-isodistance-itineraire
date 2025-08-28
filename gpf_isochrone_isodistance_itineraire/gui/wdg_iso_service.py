"""Widget to launch iso service processing"""

# standard
from pathlib import Path
from typing import Any, Dict, Optional

# PyQGIS
from qgis.core import (
    QgsApplication,
    QgsFeature,
    QgsFields,
    QgsGeometry,
    QgsProcessingContext,
    QgsProject,
    QgsVectorLayer,
)
from qgis.PyQt import uic
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QWidget

from gpf_isochrone_isodistance_itineraire.__about__ import DIR_PLUGIN_ROOT

# project
from gpf_isochrone_isodistance_itineraire.constants import ISOCHRONE_OPERATION
from gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser import (
    get_available_resources,
    get_resource_direction,
    get_resource_profiles,
)
from gpf_isochrone_isodistance_itineraire.processing.gpf_iso_service import (
    GpfIsoServiceProcessing,
)


class IsoServiceWidget(QWidget):
    """QWidget to launch iso service processing

    :param parent: dialog parent, defaults to None
    :type parent: Optional[QWidget], optional
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        ui_path = Path(__file__).resolve(True).parent / "wdg_iso_service.ui"
        uic.loadUi(ui_path, self)

        self.setWindowIcon(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/logo_isochrone.png"))
        )

        # Get list of available resource from getcap
        available_resource = get_available_resources(operation=ISOCHRONE_OPERATION)
        self.cbx_resource.clear()
        self.cbx_resource.addItems(available_resource)

        self.cbx_resource.currentIndexChanged.connect(self._resource_changed)
        self._resource_changed()

        self.btn_run.setIcon(QIcon(":images/themes/default/mActionStart.svg"))
        self.btn_run.clicked.connect(self._run_processing)
        self.rbtn_isochrone.clicked.connect(self._service_changed)
        self.rbtn_isodistance.clicked.connect(self._service_changed)
        self._service_changed()

        self.memory_layer = None

    def _service_changed(self) -> None:
        """Update labels and maximum value for max cost depending on service used"""
        if self.rbtn_isochrone.isChecked():
            label_str = self.tr("Durée maximale")
            suffix_str = self.tr(" s")
            max_value = 100000.0
        else:
            label_str = self.tr("Distance maximale")
            suffix_str = self.tr(" km")
            max_value = 500.0
        self.lbl_max_cost.setText(label_str)
        self.spb_max_cost.setSuffix(suffix_str)
        self.spb_max_cost.setMaximum(max_value)

    def _get_isoservice_processing(self) -> str:
        """Return processing name for selected isoservice

        :return: processing name
        :rtype: str
        """
        if self.rbtn_isochrone.isChecked():
            return "gpf_isochrone_isodistance_itineraire:isochrone_processing"
        return "gpf_isochrone_isodistance_itineraire:isodistance_processing"

    def _run_processing(self) -> None:
        """Run processing for selected point and algorithm parameters"""

        # Create a temporary memory layer with selected point
        # Must be stored in class to be able to use it in a QgsTask
        self.memory_layer = self._create_input_layer()

        # Get algorithm
        algo_str = self._get_isoservice_processing()
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)

        # Define parameters
        params = {
            "INPUT": self.memory_layer,
            GpfIsoServiceProcessing.ID_RESOURCE: self.cbx_resource.currentText(),
            GpfIsoServiceProcessing.PROFILE: self.cbx_profil.currentText(),
            GpfIsoServiceProcessing.DIRECTION: self.cbx_direction.currentText(),
            GpfIsoServiceProcessing.MAX_COST: self.spb_max_cost.value(),
            GpfIsoServiceProcessing.ADDITIONAL_URL_PARAM: self.txt_additionnal_request.toPlainText(),
            "OUTPUT": "TEMPORARY_OUTPUT",
        }

        # Run algorithm
        self.txt_processing_run.run_alg(alg, params, self._isoservice_computed)

    def _isoservice_computed(
        self, context: QgsProcessingContext, successful: bool, results: Dict[str, Any]
    ) -> None:
        """Load result after algorithm run

        :param context: processing context (used to get created layer)
        :type context: QgsProcessingContext
        :param successful: True if algorithm was succesful, False otherwise
        :type successful: bool
        :param results: algorithm result dict
        :type results: Dict[str, Any]
        """
        if successful:
            output_id = results["OUTPUT"]
            if isolayer := context.getMapLayer(output_id):
                QgsProject.instance().addMapLayer(isolayer)

    def _create_input_layer(self) -> QgsVectorLayer:
        """Create an input layer from selected point

        :return: input layer for algorithm
        :rtype: QgsVectorLayer
        """
        layer = QgsVectorLayer(
            f"Point?crs={self.wdg_point_selection.get_crs().authid()}",
            "Point sélectionné",
            "memory",
        )

        feature = QgsFeature(QgsFields())
        feature.setGeometry(
            QgsGeometry.fromPointXY(self.wdg_point_selection.get_displayed_point())
        )

        layer.dataProvider().addFeatures([feature])

        return layer

    def _resource_changed(self) -> None:
        """Update available profil and direction for selected resource"""
        resource = self.cbx_resource.currentText()

        # Update profiles
        profiles = get_resource_profiles(
            id_resource=resource, operation=ISOCHRONE_OPERATION
        )
        self.cbx_profil.clear()
        self.cbx_profil.addItems(profiles)

        # Update directions
        directions = get_resource_direction(id_resource=resource)

        self.cbx_direction.clear()
        self.cbx_direction.addItems(directions)
