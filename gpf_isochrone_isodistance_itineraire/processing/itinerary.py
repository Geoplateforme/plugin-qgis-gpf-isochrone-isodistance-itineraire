import json
from typing import Optional

from qgis.core import (
    Qgis,
    QgsBlockingNetworkRequest,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsPointXY,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterPoint,
    QgsProcessingParameterString,
    QgsProcessingParameterVectorLayer,
)
from qgis.PyQt.QtCore import QCoreApplication, QMetaType, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

from gpf_isochrone_isodistance_itineraire.constants import ROUTE_OPERATION
from gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser import (
    get_available_resources,
    get_resource_crs,
    get_resource_default_crs,
    get_resource_optimization,
    get_resource_param_bbox,
    get_resource_profiles,
    route_available_for_resource,
    route_available_for_service,
)
from gpf_isochrone_isodistance_itineraire.processing.utils import (
    get_short_string,
    get_user_manual_url,
)
from gpf_isochrone_isodistance_itineraire.toolbelt import PlgOptionsManager


class ItineraryProcessing(QgsProcessingAlgorithm):
    URL_SERVICE = "URL_SERVICE"
    ID_RESOURCE = "ID_RESOURCE"
    START = "START"
    END = "END"
    INTERMEDIATES = "INTERMEDIATES"
    PROFILE = "PROFILE"
    OPTIMIZATION = "OPTIMIZATION"
    ADDITIONAL_URL_PARAM = "ADDITIONAL_URL_PARAM"

    OUTPUT = "OUTPUT"

    def tr(self, string):
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, string)

    def createInstance(self):
        return ItineraryProcessing()

    def name(self):
        return "itinerary"

    def displayName(self):
        return self.tr("Calcul itinéraire")

    def group(self):
        return self.tr("")

    def groupId(self):
        return ""

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

    def initAlgorithm(self, config=None):
        plg_settings = PlgOptionsManager().get_plg_settings()

        self.addParameter(
            QgsProcessingParameterString(
                name=self.URL_SERVICE,
                description=self.tr("Url service"),
                defaultValue=plg_settings.url_service,
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                name=self.ID_RESOURCE,
                description=self.tr("Identifiant ressource"),
            )
        )

        self.addParameter(
            QgsProcessingParameterPoint(
                name=self.START, description=self.tr("Point de départ")
            )
        )

        self.addParameter(
            QgsProcessingParameterPoint(
                name=self.END, description=self.tr("Point d'arrivée")
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                name=self.INTERMEDIATES,
                description=self.tr("Etapes"),
                types=[QgsProcessing.SourceType.TypeVectorPoint],
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                name=self.PROFILE,
                description=self.tr("Profil"),
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                name=self.OPTIMIZATION,
                description=self.tr("Optimisation"),
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

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.OUTPUT,
                description=self.tr("Itinéraire"),
                type=QgsProcessing.SourceType.VectorLine,
            )
        )

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

        if not route_available_for_resource(id_resource, url_service):
            if feedback:
                feedback.reportError(
                    self.tr(
                        "Service itinéraire indisponible pour la resource : {}".format(
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
            operation=ROUTE_OPERATION,
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

    def _check_point(
        self,
        geom: QgsPointXY,
        geom_crs: QgsCoordinateReferenceSystem,
        id_resource: str,
        url_service: str,
        context: QgsProcessingContext,
        feedback: Optional[QgsProcessingFeedback],
    ) -> bool:
        """Check if point is inside resource bbox

        :param geom: point geom
        :type geom: QgsPointXY
        :param geom_crs: point crs
        :type geom_crs: QgsCoordinateReferenceSystem
        :param id_resource: id resource
        :type id_resource: str
        :param url_service: url service
        :type url_service: str
        :param context: processing context
        :type context: QgsProcessingContext
        :param feedback: processing feedback
        :type feedback: Optional[QgsProcessingFeedback]
        :return: True if point is inside resource bbox, False otherwise
        :rtype: bool
        """
        bbox = get_resource_param_bbox(
            parameter="start",
            id_resource=id_resource,
            operation=ROUTE_OPERATION,
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
            # convert bbox to input crs
            source_crs = QgsCoordinateReferenceSystem("EPSG:4326")
            transform = QgsCoordinateTransform(
                source_crs,
                geom_crs,
                context.transformContext(),
            )
            bbox = transform.transformBoundingBox(bbox)

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

    def _check_optimization(
        self,
        optimization: str,
        id_resource: str,
        url_service: str,
        feedback: Optional[QgsProcessingFeedback],
    ) -> bool:
        """Check if optimization is valid for ressource

        :param optimization: optimization
        :type optimization: str
        :param id_resource: id resource
        :type id_resource: str
        :param url_service: url service
        :type url_service: str
        :param feedback: processing feedback
        :type feedback: Optional[QgsProcessingFeedback]
        :return: True if optimization is valid, False otherwise
        :rtype: bool
        """
        if optimization not in get_resource_optimization(
            id_resource=id_resource,
            url_service=url_service,
        ):
            if feedback:
                feedback.reportError(
                    self.tr(
                        "La resource {} ne contient pas l'optimisation : {}".format(
                            id_resource, optimization
                        )
                    )
                )
            return False
        return True

    def _define_request_crs(
        self,
        input_crs: QgsCoordinateReferenceSystem,
        id_resource: str,
        url_service: str,
        feedback: Optional[QgsProcessingFeedback],
    ) -> Optional[QgsCoordinateReferenceSystem]:
        """Define request CRS by checking supported CRS for resource.
        If CRS incompatible return default CRS or first available CRS for resource
        If no CRS defined in resource None value returned

        :param input_crs: input CRS
        :type input_crs: QgsCoordinateReferenceSystem
        :param id_resource: id resource
        :type id_resource: str
        :param url_service: url service
        :type url_service: str
        :param feedback: processing feedback
        :type feedback: Optional[QgsProcessingFeedback]
        :return: request CRS, None if no CRS available for resource
        :rtype: Optional[QgsCoordinateReferenceSystem]
        """
        # There is an issue in Road2 for some sources if the CRS is not EPSG:4326
        # See : https://github.com/IGNF/road2/issues/119 and https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/issues/37
        # We need to force use of 4326 for request CRS
        return QgsCoordinateReferenceSystem("EPSG:4326")

        # Check if input crs is compatible
        supported_crs = get_resource_crs(
            id_resource=id_resource,
            operation=ROUTE_OPERATION,
            url_service=url_service,
        )
        if len(supported_crs) == 0:
            if feedback:
                feedback.reportError(
                    self.tr(
                        "La resource ne supporte aucun CRS : {}".format(id_resource)
                    )
                )
            return None

        request_crs = input_crs
        if input_crs.authid() not in supported_crs:
            # If CRS incompatible, use default or first available CRS
            if default_auth_id := get_resource_default_crs(
                id_resource=id_resource,
                operation=ROUTE_OPERATION,
                url_service=url_service,
            ):
                request_crs = QgsCoordinateReferenceSystem(default_auth_id)
            else:
                request_crs = QgsCoordinateReferenceSystem(supported_crs[0])

            if feedback:
                feedback.pushWarning(
                    self.tr(
                        "Le CRS en entrée n'est pas compatible avec la ressource : {}. Utilisation du CRS {} pour le calcul".format(
                            id_resource, request_crs.authid()
                        )
                    )
                )
        return request_crs

    @staticmethod
    def get_output_fields() -> QgsFields:
        """Return fields for output layer

        :return: field for output layer
        :rtype: QgsFields
        """
        output_fields = QgsFields()
        output_fields.append(QgsField(name="start_x", type=QMetaType.Type.Double))
        output_fields.append(QgsField(name="start_y", type=QMetaType.Type.Double))
        output_fields.append(QgsField(name="end_x", type=QMetaType.Type.Double))
        output_fields.append(QgsField(name="end_y", type=QMetaType.Type.Double))
        output_fields.append(
            QgsField(name="intermediates", type=QMetaType.Type.QString)
        )
        output_fields.append(QgsField(name="request", type=QMetaType.Type.QString))
        output_fields.append(QgsField(name="id_resource", type=QMetaType.Type.QString))
        output_fields.append(QgsField(name="profile", type=QMetaType.Type.QString))
        output_fields.append(QgsField(name="optimization", type=QMetaType.Type.QString))
        output_fields.append(
            QgsField(name="additional_url_param", type=QMetaType.Type.QString)
        )
        output_fields.append(QgsField(name="distance", type=QMetaType.Type.Double))
        output_fields.append(QgsField(name="duration", type=QMetaType.Type.Double))
        return output_fields

    def processAlgorithm(self, parameters, context, feedback):
        url_service = self.parameterAsString(parameters, self.URL_SERVICE, context)
        id_resource = self.parameterAsString(parameters, self.ID_RESOURCE, context)
        profile = self.parameterAsString(parameters, self.PROFILE, context)
        optimization = self.parameterAsString(parameters, self.OPTIMIZATION, context)
        start = self.parameterAsPoint(parameters, self.START, context)
        end = self.parameterAsPoint(parameters, self.END, context)
        input_crs = self.parameterAsPointCrs(parameters, self.START, context)

        intermediates_layer = self.parameterAsVectorLayer(
            parameters, self.INTERMEDIATES, context
        )

        additional_url_param = self.parameterAsString(
            parameters, self.ADDITIONAL_URL_PARAM, context
        )

        # Check service for isochrone
        if not route_available_for_service(url_service):
            raise QgsProcessingException(
                self.tr(
                    "Service itineraire indisponible pour l'url : {}".format(
                        url_service
                    )
                )
            )
        output_fields = ItineraryProcessing.get_output_fields()
        # Get sink for output feature
        (sink_itinerary, sink_itinerary_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            output_fields,
            Qgis.WkbType.LineStringZ,
            input_crs,
        )

        # Check resource
        if not self._check_resource(id_resource, url_service, feedback):
            raise QgsProcessingException(
                self.tr(
                    "Service itineraire indisponible pour l'url : {} et la ressource {}".format(
                        url_service, id_resource
                    )
                )
            )

        # Define request crs
        request_crs = self._define_request_crs(
            input_crs=input_crs,
            id_resource=id_resource,
            url_service=url_service,
            feedback=feedback,
        )
        if request_crs is None:
            raise QgsProcessingException(
                self.tr(
                    "Impossible de définir le système de coordonnées pour la requête"
                )
            )

        # Check if geometry must be converted
        transform = None
        if input_crs != request_crs:
            transform = QgsCoordinateTransform(
                input_crs,
                request_crs,
                context.transformContext(),
            )
            start = transform.transform(start)
            end = transform.transform(end)

        # Create request
        request = f"{url_service}/itineraire?start={start.x()},{start.y()}&end={end.x()},{end.y()}"

        # Add intermediates
        intermediates_str = ""
        if intermediates_layer:
            intermediates_crs = intermediates_layer.crs()

            intermediates_str_list = []
            for feature in intermediates_layer.getFeatures():
                if feature.geometry().isNull():
                    feedback.pushWarning(
                        self.tr(
                            "Point intermédiaire avec géométrie nulle. Le point n'est pas utilisé."
                        )
                    )
                    continue

                step = feature.geometry().asPoint()
                if intermediates_crs != request_crs:
                    intermediate_transform = QgsCoordinateTransform(
                        intermediates_crs,
                        request_crs,
                        context.transformContext(),
                    )
                    step = intermediate_transform.transform(step)
                if not self._check_point(
                    step, request_crs, id_resource, url_service, context, feedback
                ):
                    feedback.pushWarning(
                        self.tr(
                            "Point intermédiaire non contenu dans la bbox du service. Le point n'est pas utilisé."
                        )
                    )
                else:
                    intermediates_str_list.append(f"{step.x()},{step.y()}")

            intermediates_str = "|".join(intermediates_str_list)
            request += f"&intermediates={intermediates_str}"

        # Add resource
        request += f"&resource={id_resource}"

        # Check point geom
        if not self._check_point(
            start, request_crs, id_resource, url_service, context, feedback
        ):
            raise QgsProcessingException(
                self.tr(
                    "Point de départ non inclus dans la bounding box de la ressource."
                )
            )

        if not self._check_point(
            end, request_crs, id_resource, url_service, context, feedback
        ):
            raise QgsProcessingException(
                self.tr(
                    "Point d'arrivée non inclus dans la bounding box de la ressource."
                )
            )

        # Check profile
        if not self._check_profile(profile, id_resource, url_service, feedback):
            raise QgsProcessingException(
                self.tr(
                    "Profil {} non compatible avec la ressource {}".format(
                        profile, id_resource
                    )
                )
            )
        request += f"&profile={profile}"

        # Check optimization
        if not self._check_optimization(
            optimization, id_resource, url_service, feedback
        ):
            raise QgsProcessingException(
                self.tr(
                    "Optimisation {} non compatible avec la ressource {}".format(
                        optimization, id_resource
                    )
                )
            )
        request += f"&optimization={optimization}"

        request += "&geometryFormat=wkt"

        request += f"&crs={request_crs.authid()}"

        # Check if additional param are available
        if additional_url_param:
            request += additional_url_param

        if feedback:
            feedback.pushCommandInfo(f"request : {request}")

        blocking_req = QgsBlockingNetworkRequest()
        qreq = QNetworkRequest(QUrl(request))
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

                raise QgsProcessingException(
                    self.tr(
                        "Erreur lors de la requête pour calcul d'itinéraire : {}".format(
                            err_msg
                        )
                    )
                )

        res_str = str(blocking_req.reply().content(), "UTF8")
        if res_str:
            data = json.loads(res_str)

            output_geom = QgsGeometry.fromWkt(data["geometry"])
            # Apply inverse transformation if input data was converted
            if transform:
                output_geom.transform(
                    transform, direction=Qgis.TransformDirection.Reverse
                )

            duration = data["duration"]
            distance = data["distance"]

            f = QgsFeature()
            f.setGeometry(output_geom)
            f.setFields(output_fields)

            f.setAttribute("start_x", start.x())
            f.setAttribute("start_y", start.y())
            f.setAttribute("end_x", end.x())
            f.setAttribute("end_y", end.y())
            f.setAttribute("intermediates", intermediates_str)
            f.setAttribute("request", request)
            f.setAttribute("id_resource", id_resource)
            f.setAttribute("profile", profile)
            f.setAttribute("optimization", optimization)
            f.setAttribute("distance", distance)
            f.setAttribute("duration", duration)
            f.setAttribute("additional_url_param", additional_url_param)

            sink_itinerary.addFeature(feature=f, flags=QgsFeatureSink.Flag.FastInsert)
        else:
            raise QgsProcessingException(
                self.tr("Réponse vide pour la requête de calcul d'itinéraire.")
            )

        return {self.OUTPUT: sink_itinerary_id}
