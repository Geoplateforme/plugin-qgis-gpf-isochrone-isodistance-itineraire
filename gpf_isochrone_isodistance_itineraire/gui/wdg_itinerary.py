"""Widget to launch itinerary processing"""

# standard
from pathlib import Path
from typing import Any, Dict, Optional

# PyQGIS
from qgis.core import QgsApplication, QgsProcessingContext, QgsProject
from qgis.PyQt import uic
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import QWidget

from gpf_isochrone_isodistance_itineraire.__about__ import DIR_PLUGIN_ROOT

# project
from gpf_isochrone_isodistance_itineraire.constants import ROUTE_OPERATION
from gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser import (
    get_available_resources,
    get_resource_optimization,
    get_resource_profiles,
)
from gpf_isochrone_isodistance_itineraire.processing.itinerary import (
    ItineraryProcessing,
)


class ItineraryWidget(QWidget):
    """QWidget to launch itinerary processing

    :param parent: dialog parent, defaults to None
    :type parent: Optional[QWidget], optional
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        ui_path = Path(__file__).resolve(True).parent / "wdg_itinerary.ui"
        uic.loadUi(ui_path, self)

        self.setWindowIcon(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/logo_isoservices.svg"))
        )

        # Get list of available resource from getcap
        available_resource = get_available_resources(operation=ROUTE_OPERATION)
        self.cbx_resource.clear()
        self.cbx_resource.addItems(available_resource)

        self.cbx_resource.currentIndexChanged.connect(self._resource_changed)
        self._resource_changed()

        self.btn_run.setIcon(QIcon(":images/themes/default/mActionStart.svg"))
        self.btn_run.clicked.connect(self._run_processing)

        self.wdg_start_selection.set_marker_color(QColor("green"))
        self.wdg_end_selection.set_marker_color(QColor("red"))

    def _run_processing(self) -> None:
        """Run processing for selected point and algorithm parameters"""

        # Get algorithm
        algo_str = "gpf_isochrone_isodistance_itineraire:itinerary"
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)

        # Define parameters
        params = {
            ItineraryProcessing.ID_RESOURCE: self.cbx_resource.currentText(),
            ItineraryProcessing.START: self.wdg_start_selection.get_referenced_displayed_point(),
            ItineraryProcessing.END: self.wdg_end_selection.get_referenced_displayed_point(),
            # TODO gestion intermédiares
            # ItineraryProcessing.INTERMEDIATES: self.cbx_resource.currentText(),
            ItineraryProcessing.PROFILE: self.cbx_profil.currentText(),
            ItineraryProcessing.OPTIMIZATION: self.cbx_optimization.currentText(),
            ItineraryProcessing.ADDITIONAL_URL_PARAM: self.txt_additionnal_request.toPlainText(),
            "OUTPUT": "TEMPORARY_OUTPUT",
        }

        # Run algorithm
        self.txt_processing_run.run_alg(alg, params, self._itinerary_computed)

    def _itinerary_computed(
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

    def _resource_changed(self) -> None:
        """Update available profil and direction for selected resource"""
        resource = self.cbx_resource.currentText()

        # Update profiles
        profiles = get_resource_profiles(
            id_resource=resource, operation=ROUTE_OPERATION
        )
        self.cbx_profil.clear()
        self.cbx_profil.addItems(profiles)

        # Update directions
        optimizations = get_resource_optimization(id_resource=resource)

        self.cbx_optimization.clear()
        self.cbx_optimization.addItems(optimizations)
