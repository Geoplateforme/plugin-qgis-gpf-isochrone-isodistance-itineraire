# standard

# PyQGIS
from qgis.core import QgsProcessingAlgorithm
from qgis.PyQt.QtCore import QCoreApplication

# project
from gpf_isochrone_isodistance_itineraire.processing.gpf_iso_service import (
    GpfIsoServiceProcessing,
)
from gpf_isochrone_isodistance_itineraire.processing.utils import (
    get_short_string,
    get_user_manual_url,
)


class IsodistanceProcessing(GpfIsoServiceProcessing):
    def __init__(self) -> None:
        """Processing for isodistance generation"""
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
        return get_user_manual_url(self.name())

    def shortHelpString(self) -> str:
        """Returns a localised short helper string for the algorithm. This string should provide a basic description about what the algorithm does and the parameters and outputs associated with it.

        :return: short help string
        :rtype: str
        """
        return get_short_string(self.name(), self.displayName())

    def name(self) -> str:
        """Returns the algorithm name, used for identifying the algorithm.
        This string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider.
        Names should contain lowercase alphanumeric characters only and no spaces or other formatting characters.

        :return: processing name
        :rtype: str
        """
        return "isodistance_processing"

    def displayName(self) -> str:
        """Returns the translated algorithm name, which should be used for any user-visible display of the algorithm name.

        :return: display name
        :rtype: str
        """
        return self.tr("Isodistance")

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
        return IsodistanceProcessing()

    def get_max_cost_display_string(self) -> str:
        """Define display string for max cost value

        :return: display string for max cost
        :rtype: str
        """
        return self.tr("Distance maximale (km)")

    def get_max_cost_attribute_string(self) -> str:
        """Define attribute string for max cost value

        :return: attribute string for max cost
        :rtype: str
        """
        return "max_distance"

    def get_max_cost_default_value(self) -> float:
        """Define default value for max cost value

        :return: maximum value for max cost
        :rtype: float
        """
        return 100.0

    def get_cost_type(self) -> str:
        """Define cost type for request (time or distance)

        :return: cost type for request
        :rtype: str
        """
        return "distance"

    def get_cost_unit_request_str(self) -> str:
        """Define request parameter for cost type unit

        :return: cost type unit request
        :rtype: str
        """
        return "&distanceUnit=kilometer"

    def outputName(self) -> str:
        """Returns the translated, user visible name for any layers created by this algorithm.

        :return: _description_
        :rtype: str
        """
        return self.tr("Isodistance")
