# standard

# PyQGIS
from qgis.core import (
    QgsProcessingAlgorithm,
)
from qgis.PyQt.QtCore import QCoreApplication

# project
from gpf_isochrone_isodistance_itineraire.processing.gpf_iso_service import (
    GpfIsoServiceProcessing,
)


class IsochroneProcessing(GpfIsoServiceProcessing):
    def __init__(self) -> None:
        """Processing for isochrone generation"""
        super().__init__()

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def helpUrl(self) -> str:
        """Returns a localised help string for the algorithm. Algorithm subclasses should implement either `helpString()` or `helpUrl()`

        :return: help url
        :rtype: str
        """
        # TODO : add url for help
        return ""

    def shortHelpString(self) -> str:
        """Returns a localised short helper string for the algorithm. This string should provide a basic description about what the algorithm does and the parameters and outputs associated with it.

        :return: short help string
        :rtype: str
        """
        # TODO : add url for help
        return ""

    def name(self) -> str:
        """Returns the algorithm name, used for identifying the algorithm.
        This string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider.
        Names should contain lowercase alphanumeric characters only and no spaces or other formatting characters.

        :return: processing name
        :rtype: str
        """
        return "isochrone_processing"

    def displayName(self) -> str:
        """Returns the translated algorithm name, which should be used for any user-visible display of the algorithm name.

        :return: display name
        :rtype: str
        """
        return self.tr("Isochrone")

    def group(self) -> str:
        """Returns the name of the group this algorithm belongs to. This string should be localised.

        :return: group
        :rtype: str
        """
        return ""

    def groupId(self) -> str:
        """Returns the unique ID of the group this algorithm belongs to.
        This string should be fixed for the algorithm, and must not be localised. The group id should be unique within each provider.
        Group id should contain lowercase alphanumeric characters only and no spaces or other formatting characters.

        :return: group id
        :rtype: str
        """
        return ""

    def createInstance(self) -> QgsProcessingAlgorithm:
        """Creates a new instance of the algorithm class.

        :return: isochrone processing
        :rtype: QgsProcessingAlgorithm
        """
        return IsochroneProcessing()

    def get_max_cost_display_string(self) -> str:
        return self.tr("Durée maximale (secondes)")

    def get_max_cost_attribute_string(self) -> str:
        return "max_duration"

    def get_max_cost_maximum_value(self) -> float:
        return 3600.0

    def get_cost_type(self) -> str:
        return "time"

    def get_cost_unit_request_str(self) -> str:
        return "&timeUnit=second"

    def outputName(self) -> str:
        """Returns the translated, user visible name for any layers created by this algorithm.

        :return: _description_
        :rtype: str
        """
        return self.tr("Isochrones")
