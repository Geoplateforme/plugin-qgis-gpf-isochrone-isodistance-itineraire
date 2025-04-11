# standard
import json
from typing import Any, Dict, List, Optional

# PyQGIS
from qgis.core import (
    Qgis,
    QgsBlockingNetworkRequest,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsExpression,
    QgsExpressionContext,
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
    QgsProcessingParameterExpression,
    QgsProcessingParameterString,
)
from qgis.PyQt.QtCore import QCoreApplication, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

# project
from gpf_isochrone_isodistance_itineraire.constants import ISOCHRONE_OPERATION
from gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser import (
    get_available_resources,
    get_resource_cost_type,
    get_resource_direction,
    get_resource_param_bbox,
    get_resource_profiles,
    isochrone_available_for_resource,
    isochrone_available_for_service,
)
from gpf_isochrone_isodistance_itineraire.toolbelt.preferences import PlgOptionsManager


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
        self._max_duration = ""
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
        plg_settings = PlgOptionsManager().get_plg_settings()

        self.addParameter(
            QgsProcessingParameterString(
                name=self.URL_SERVICE,
                description=self.tr("Url service"),
                defaultValue=plg_settings.url_service,
            )
        )
        self.addParameter(
            QgsProcessingParameterExpression(
                name=self.ID_RESOURCE,
                description=self.tr("Identifiant ressource"),
                parentLayerParameterName=self.inputParameterName(),
            )
        )
        self.addParameter(
            QgsProcessingParameterExpression(
                name=self.PROFILE,
                description=self.tr("Profil"),
                parentLayerParameterName=self.inputParameterName(),
            )
        )
        self.addParameter(
            QgsProcessingParameterExpression(
                name=self.DIRECTION,
                description=self.tr("Direction"),
                parentLayerParameterName=self.inputParameterName(),
                defaultValue=self.DIRECTION_ENUM[0],
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterExpression(
                name=self.MAX_DURATION,
                description=self.tr("Durée maximale (secondes)"),
                parentLayerParameterName=self.inputParameterName(),
                defaultValue=3600.0,
            )
        )

        param = QgsProcessingParameterExpression(
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
        self._url_service = self.parameterAsString(
            parameters, self.URL_SERVICE, context
        )
        self._id_resource = self.parameterAsExpression(
            parameters, self.ID_RESOURCE, context
        )
        self._profile = self.parameterAsExpression(parameters, self.PROFILE, context)
        self._direction = self.parameterAsExpression(
            parameters, self.DIRECTION, context
        )

        self._max_duration = self.parameterAsExpression(
            parameters, self.MAX_DURATION, context
        )
        self._additional_url_param = self.parameterAsExpression(
            parameters, self.ADDITIONAL_URL_PARAM, context
        )

        # Check service for isochrone
        if not isochrone_available_for_service(self._url_service):
            if feedback:
                feedback.reportError(
                    self.tr(
                        "Service isochrone indisponible pour l'url : {}".format(
                            self._url_service
                        )
                    )
                )
            return False

        # If id resource is fixed (not refering to a field), check that isochrone is available
        if '"' not in self._id_resource and not self._check_resource(
            self._id_resource, self._url_service, feedback
        ):
            return False

        return True

    def _check_resource(
        self,
        id_resource: str,
        url_service: str,
        feedback: Optional[QgsProcessingFeedback],
    ) -> bool:
        """Check if resource is valid for a isochrone service

        :param id_resource: id resource
        :type id_resource: str
        :param url_service: url service
        :type url_service: str
        :param feedback: processing feedback
        :type feedback: Optional[QgsProcessingFeedback]
        :return: True if resource is valid, False otherwise
        :rtype: bool
        """
        if id_resource not in get_available_resources(url_service):
            if feedback:
                feedback.reportError(
                    self.tr(
                        "Le service ne contient pas la resource : {}".format(
                            id_resource
                        )
                    )
                )
            return False

        if not isochrone_available_for_resource(id_resource, url_service):
            if feedback:
                feedback.reportError(
                    self.tr(
                        "Service isochrone indisponible pour la resource : {}".format(
                            id_resource
                        )
                    )
                )
            return False

        return True

    def _check_profile(
        self,
        profile: str,
        id_resource: str,
        url_service: str,
        feedback: Optional[QgsProcessingFeedback],
    ) -> bool:
        """Check if profile is valid for ressource

        :param profile: profile
        :type profile: str
        :param id_resource: id resource
        :type id_resource: str
        :param url_service: url service
        :type url_service: str
        :param feedback: processing feedback
        :type feedback: Optional[QgsProcessingFeedback]
        :return: True if profile is valid, False otherwise
        :rtype: bool
        """
        if profile not in get_resource_profiles(
            id_resource=id_resource,
            operation=ISOCHRONE_OPERATION,
            url_service=url_service,
        ):
            if feedback:
                feedback.reportError(
                    self.tr(
                        "La resource {} ne contient pas le profil : {}".format(
                            id_resource, profile
                        )
                    )
                )
            return False
        return True

    def _check_direction(
        self,
        direction: str,
        id_resource: str,
        url_service: str,
        feedback: Optional[QgsProcessingFeedback],
    ) -> bool:
        """Check if profile is valid for ressource

        :param profile: profile
        :type profile: str
        :param id_resource: id resource
        :type id_resource: str
        :param url_service: url service
        :type url_service: str
        :param feedback: processing feedback
        :type feedback: Optional[QgsProcessingFeedback]
        :return: True if profile is valid, False otherwise
        :rtype: bool
        """
        if direction not in get_resource_direction(
            id_resource=id_resource,
            url_service=url_service,
        ):
            if feedback:
                feedback.reportError(
                    self.tr(
                        "La resource {} ne contient pas la direction : {}".format(
                            id_resource, direction
                        )
                    )
                )
            return False
        return True

    def _check_cost_type(
        self,
        cost_type: str,
        id_resource: str,
        url_service: str,
        feedback: Optional[QgsProcessingFeedback],
    ) -> bool:
        """Check if profile is valid for ressource

        :param profile: profile
        :type profile: str
        :param id_resource: id resource
        :type id_resource: str
        :param url_service: url service
        :type url_service: str
        :param feedback: processing feedback
        :type feedback: Optional[QgsProcessingFeedback]
        :return: True if profile is valid, False otherwise
        :rtype: bool
        """
        if cost_type not in get_resource_cost_type(
            id_resource=id_resource,
            url_service=url_service,
        ):
            if feedback:
                feedback.reportError(
                    self.tr(
                        "La resource {} ne contient pas le type de cout : {}".format(
                            id_resource, cost_type
                        )
                    )
                )
            return False
        return True

    def _check_point(
        self,
        geom: QgsPointXY,
        id_resource: str,
        url_service: str,
        feedback: Optional[QgsProcessingFeedback],
    ) -> bool:
        """Check if point is inside resource bbox

        :param profile: profile
        :type profile: str
        :param id_resource: id resource
        :type id_resource: str
        :param url_service: url service
        :type url_service: str
        :param feedback: processing feedback
        :type feedback: Optional[QgsProcessingFeedback]
        :return: True if profile is valid, False otherwise
        :rtype: bool
        """
        bbox = get_resource_param_bbox(
            parameter="point",
            id_resource=id_resource,
            operation=ISOCHRONE_OPERATION,
            url_service=url_service,
        )
        if not bbox:
            if feedback:
                feedback.pushWarning(
                    self.tr(
                        "Impossible de définir la bounding box pour la ressource {}".format(
                            id_resource
                        )
                    )
                )
        else:
            if not bbox.contains(geom):
                if feedback:
                    feedback.reportError(
                        self.tr(
                            "Point {} non contenu dans la bounding box de la ressource {} : {}".format(
                                geom.asWkt(), id_resource, bbox
                            )
                        )
                    )
                return False
        return True

    def _evaluateExpression(
        self, expression_ctx: QgsExpressionContext, expression_str: str
    ) -> Any:
        """Evaluate expression from context. If there is an evaluation error return expression string.

        :param expression_ctx: expression context
        :type expression_ctx: QgsExpressionContext
        :param expression_str: expression string
        :type expression_str: str
        :return: evaluated value
        :rtype: Any
        """
        expression = QgsExpression(expression_str)
        result = expression.evaluate(expression_ctx)
        if expression.hasEvalError():
            result = expression_str
        return result

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

        expression_ctx = context.expressionContext()
        expression_ctx.setFeature(feature)

        request = f"{self._url_service}/isochrone?point={geom.x()},{geom.y()}"

        # Check resource
        id_resource = self._evaluateExpression(expression_ctx, self._id_resource)
        if not self._check_resource(id_resource, self._url_service, feedback):
            return []
        request += f"&resource={id_resource}"

        # Check point geom
        if not self._check_point(geom, id_resource, self._url_service, feedback):
            return []

        # Check profile
        profile = self._evaluateExpression(expression_ctx, self._profile)
        if not self._check_profile(profile, id_resource, self._url_service, feedback):
            return []
        request += f"&profile={profile}"

        # Check direction
        direction = self._evaluateExpression(expression_ctx, self._direction)
        if not self._check_direction(
            direction, id_resource, self._url_service, feedback
        ):
            return []
        request += f"&direction={direction}"

        # Check cost type
        cost_type = "time"
        if not self._check_cost_type(
            cost_type, id_resource, self._url_service, feedback
        ):
            return []
        request += f"&costType={cost_type}"

        request += "&timeUnit=second"

        # TODO check url getCapabilities to check values
        max_duration = self._evaluateExpression(expression_ctx, self._max_duration)
        request += f"&costValue={max_duration}"
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
        f.setAttribute("id_resource", id_resource)
        f.setAttribute("profile", profile)
        f.setAttribute("direction", direction)
        f.setAttribute("max_duration", max_duration)

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
        result.append(QgsField("id_resource"))
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
