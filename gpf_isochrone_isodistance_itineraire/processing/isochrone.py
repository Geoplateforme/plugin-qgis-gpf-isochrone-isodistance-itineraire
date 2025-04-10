# standard
import json
from typing import Any, Dict, List, Optional

# PyQGIS
from qgis.core import (
    Qgis,
    QgsBlockingNetworkRequest,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsPointXY,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeatureBasedAlgorithm,
    QgsProcessingFeedback,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
    QgsProcessingParameterString,
)
from qgis.PyQt.Qt import QUrl
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtNetwork import QNetworkRequest


class IsochroneProcessing(QgsProcessingFeatureBasedAlgorithm):
    URL_SERVICE = "URL_SERVICE"
    ID_RESOURCE = "ID_RESOURCE"
    PROFILE = "PROFILE"
    DIRECTION = "DIRECTION"
    MAX_DURATION = "MAX_DURATION"
    ADDITIONAL_URL_PARAM = "ADDITIONAL_URL_PARAM"

    DIRECTION_ENUM = ["departure", "arrival"]

    def __init__(self) -> None:
        """Processing for isochrone generation"""
        super().__init__()
        self._url_service = ""
        self._id_resource = ""
        self._profile = ""
        self._direction = ""
        self._max_duration = 0.0
        self._additional_url_param = ""
        self._input_crs = QgsCoordinateReferenceSystem()

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

    def initParameters(self, configuration: Dict[str, Any] = {}) -> None:
        """Initializes any extra parameters added by the algorithm subclass.
        There is no need to declare the input source or output sink, as these are automatically created by QgsProcessingFeatureBasedAlgorithm.

        :param configuration: configuration, defaults to {}
        :type configuration: Dict[str, Any], optional
        """

        self.addParameter(
            QgsProcessingParameterString(
                name=self.URL_SERVICE,
                description=self.tr("Url service"),
                defaultValue="https://data.geopf.fr/navigation/",
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.ID_RESOURCE,
                description=self.tr("Identifiant ressource"),
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.PROFILE, description=self.tr("Profil")
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.DIRECTION,
                self.tr("Direction"),
                options=self.DIRECTION_ENUM,
                defaultValue=self.DIRECTION_ENUM[0],
                usesStaticStrings=True,
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.MAX_DURATION,
                description=self.tr("Durée maximale (secondes)"),
                defaultValue=3600.0,
                type=QgsProcessingParameterNumber.Type.Double,
            )
        )

        param = QgsProcessingParameterString(
            name=self.ADDITIONAL_URL_PARAM,
            description=self.tr("Paramètres additionnels pour la requête"),
            optional=True,
        )

        param.setFlags(
            param.flags() | QgsProcessingParameterDefinition.Flag.FlagAdvanced
        )
        self.addParameter(param)

    def prepareAlgorithm(
        self,
        parameters: Dict[str, Any],
        context: QgsProcessingContext,
        feedback: Optional[QgsProcessingFeedback],
    ) -> bool:
        """Prepares the algorithm to run using the specified parameters.

        :param parameters: input parameter
        :type parameters: Dict[str, Any]
        :param context: processing context
        :type context: QgsProcessingContext
        :param feedback: processing feedback
        :type feedback: Optional[QgsProcessingFeedback]
        :return: True if the parameter are valid, False otherwise
        :rtype: bool
        """
        self._url_service = ""
        self._id_resource = ""
        self._profile = ""
        self._direction = ""
        self._max_duration = 0.0
        self._additional_url_param = ""

        self._url_service = self.parameterAsString(
            parameters, self.URL_SERVICE, context
        )
        self._id_resource = self.parameterAsString(
            parameters, self.ID_RESOURCE, context
        )
        self._profile = self.parameterAsString(parameters, self.PROFILE, context)

        self._direction = self.parameterAsString(parameters, self.DIRECTION, context)

        self._max_duration = self.parameterAsDouble(
            parameters, self.MAX_DURATION, context
        )
        self._additional_url_param = self.parameterAsString(
            parameters, self.ADDITIONAL_URL_PARAM, context
        )

        # TODO check url getCapabilities to return false if url invalid
        return True

    def processFeature(
        self,
        feature: QgsFeature,
        context: QgsProcessingContext,
        feedback: Optional[QgsProcessingFeedback],
    ) -> List[QgsFeature]:
        """Processes an individual input feature from the source

        :param feature: feature to process
        :type feature: QgsFeature
        :param context: processing context
        :type context: QgsProcessingContext
        :param feedback: processing feedback
        :type feedback: Optional[QgsProcessingFeedback]
        :return: list of created QgsFeature
        :rtype: List[QgsFeature]
        """

        # TODO : for now only use EPSG:4326 crs
        geometry = feature.geometry()
        output_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        authid: str = output_crs.authid()
        transform = QgsCoordinateTransform(
            self._input_crs,
            output_crs,
            context.transformContext(),
        )
        geometry.transform(transform)
        geom: QgsPointXY = geometry.asPoint()

        # TODO : get bounding box of GetCapabilites and check x/y
        request = f"{self._url_service}/isochrone?point={geom.x()},{geom.y()}"
        request += f"&resource={self._id_resource}"
        request += f"&costValue={self._max_duration}&costType=time&timeUnit=second"
        request += f"&profile={self._profile}"
        request += f"&direction={self._direction}"
        request += "&geometryFormat=wkt"
        request += f"&crs={authid}"

        request += self._additional_url_param

        blocking_req = QgsBlockingNetworkRequest()
        qreq = QNetworkRequest(url=QUrl(request))
        error_code = blocking_req.get(qreq, forceRefresh=True, feedback=feedback)

        # Add feedback in case of error
        if error_code != QgsBlockingNetworkRequest.ErrorCode.NoError:
            if feedback:
                err_msg = f"{blocking_req.errorMessage()}."
                # get the API response error to log it
                req_reply = blocking_req.reply()
                if req_reply and b"application/json" in req_reply.rawHeader(
                    b"Content-Type"
                ):
                    api_response_error = json.loads(str(req_reply.content(), "UTF8"))
                    if (
                        "error" in api_response_error
                        and "message" in api_response_error["error"]
                    ):
                        err_msg += f"API error message: {api_response_error['error']['message']}"
                feedback.reportError(
                    self.tr(
                        "Erreur lors de la requête pour calcul d'isochrone : {}".format(
                            err_msg
                        )
                    )
                )
            return []

        data = json.loads(str(blocking_req.reply().content(), "UTF8"))

        f = QgsFeature()
        f.setGeometry(QgsGeometry.fromWkt(data["geometry"]))
        f.setFields(self.outputFields(feature.fields()))
        f.setAttribute("request", request)
        f.setAttribute("x", geom.x())
        f.setAttribute("y", geom.y())
        f.setAttribute("profile", self._id_resource)
        f.setAttribute("direction", self._direction)
        f.setAttribute("max_duration", self._max_duration)

        return [f]

    def outputName(self) -> str:
        """Returns the translated, user visible name for any layers created by this algorithm.

        :return: _description_
        :rtype: str
        """
        return self.tr("Isochrones")

    def outputWkbType(self, _: Qgis.WkbType) -> Qgis.WkbType:
        """Maps the input WKB geometry type (inputWkbType) to the corresponding output WKB type generated by the algorithm.

        :param _: input WkbType (not used)
        :type _: Qgis.WkbType
        :return: output WkbType (alway Qgis.WkbType.Polygon)
        :rtype: Qgis.WkbType
        """
        return Qgis.WkbType.Polygon

    def outputFields(self, _: QgsFields) -> QgsFields:
        """Maps the input source fields (inputFields) to corresponding output fields generated by the algorithm.

        :param _: input fields
        :type _: QgsFields
        :return: output fields
        :rtype: QgsFields
        """
        result = QgsFields()
        result.append(QgsField("x"))
        result.append(QgsField("y"))
        result.append(QgsField("request"))
        result.append(QgsField("profile"))
        result.append(QgsField("direction"))
        result.append(QgsField("max_duration"))
        return result

    def outputCrs(
        self, inputCrs: QgsCoordinateReferenceSystem
    ) -> QgsCoordinateReferenceSystem:
        """Maps the input source coordinate reference system (inputCrs) to a corresponding output CRS generated by the algorithm.

        :param inputCrs: input crs
        :type inputCrs: QgsCoordinateReferenceSystem
        :return: output crs (alway EPSG:4326)
        :rtype: QgsCoordinateReferenceSystem
        """
        self._input_crs = inputCrs
        # TODO : get usable crs for resources from GetCapabities, for now always use EPSG:4326
        return QgsCoordinateReferenceSystem("EPSG:4326")

    def inputLayerTypes(self) -> List[int]:
        """Returns the valid input layer types for the source layer for this algorithm.
        Only point vector are supported

        :return: list of supported input layer type
        :rtype: List[int]
        """
        return [Qgis.ProcessingSourceType.VectorPoint]
