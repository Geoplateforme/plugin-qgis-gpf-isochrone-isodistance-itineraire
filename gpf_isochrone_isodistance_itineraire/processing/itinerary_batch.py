# standard
from typing import Any, Dict, List, Optional

# PyQGIS
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsProcessing,
    QgsProcessingContext,
    QgsProcessingFeatureBasedAlgorithm,
    QgsProcessingFeedback,
    QgsProcessingParameterCrs,
    QgsProcessingParameterField,
    QgsProcessingParameterString,
    QgsProcessingParameterVectorLayer,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QCoreApplication

from gpf_isochrone_isodistance_itineraire.processing.itinerary import (
    ItineraryProcessing,
)

# plugin
from gpf_isochrone_isodistance_itineraire.processing.utils import (
    get_short_string,
    get_user_manual_url,
)
from gpf_isochrone_isodistance_itineraire.toolbelt import PlgOptionsManager


class BatchItineraryAlgorithm(QgsProcessingFeatureBasedAlgorithm):
    URL_SERVICE = "URL_SERVICE"

    ID_START_FIELD = "ID_START_FIELD"
    ID_END_FIELD = "ID_END_FIELD"
    ID_INTERMEDIATES_FIELD = "ID_INTERMEDIATES_FIELD"
    RESSOURCE_FIELD = "RESSOURCE_FIELD"
    PROFIL_FIELD = "PROFIL_FIELD"
    OPTIMIZATION_FIELD = "OPTIMIZATION_FIELD"
    ADDITIONAL_URL_PARAM_FIELD = "ADDITIONAL_URL_PARAM_FIELD"

    STARTS_LAYER = "STARTS_LAYER"
    STARTS_LAYER_ID_FIELD = "STARTS_LAYER_ID_FIELD"

    ENDS_LAYER = "ENDS_LAYER"
    ENDS_LAYER_ID_FIELD = "ENDS_LAYER_ID_FIELD"

    INTERMEDIATES_LAYER = "INTERMEDIATES_LAYER"
    INTERMEDIATES_LAYER_ID_FIELD = "INTERMEDIATES_LAYER_ID_FIELD"

    CRS = "CRS"

    def __init__(self) -> None:
        """Processing for batch itinerary compute"""
        super().__init__()
        self.url_service = ""

        self.param_id_start_field = ""
        self.param_id_end_field = ""
        self.param_id_intermediates_field = ""
        self.param_ressource_field = ""
        self.param_profil_field = ""
        self.param_optimization_field = ""
        self.param_additionnal_url_param_field = ""

        self.starts_layer = None
        self.ends_layer = None
        self.intermediates_layer = None

        self.id_start_field = ""
        self.id_end_field = ""
        self.id_intermediate_field = ""

        self.output_crs = None

        self.start_transform = None
        self.end_transform = None
        self.result_transform = None
        self.alg = None

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def createInstance(self):
        return BatchItineraryAlgorithm()

    def name(self):
        return "itinerary_batch"

    def displayName(self):
        return self.tr("Batch itinerary")

    def group(self):
        return self.tr("")

    def groupId(self):
        return ""

    def helpUrl(self):
        return get_user_manual_url(self.name())

    def shortHelpString(self):
        return get_short_string(self.name(), self.displayName())

    def initParameters(self, configuration: Dict[str, Any] = {}) -> None:
        plg_settings = PlgOptionsManager().get_plg_settings()

        self.addParameter(
            QgsProcessingParameterString(
                name=self.URL_SERVICE,
                description=self.tr("Url service"),
                defaultValue=plg_settings.url_service,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.ID_START_FIELD,
                description=self.tr("Champ départ"),
                parentLayerParameterName="INPUT",
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.ID_END_FIELD,
                description=self.tr("Champ arrivée"),
                parentLayerParameterName="INPUT",
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.ID_INTERMEDIATES_FIELD,
                description=self.tr("Champ étapes"),
                parentLayerParameterName="INPUT",
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.RESSOURCE_FIELD,
                description=self.tr("Champ ressource"),
                parentLayerParameterName="INPUT",
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.PROFIL_FIELD,
                description=self.tr("Champ profil"),
                parentLayerParameterName="INPUT",
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.OPTIMIZATION_FIELD,
                description=self.tr("Champ optimisation"),
                parentLayerParameterName="INPUT",
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.ADDITIONAL_URL_PARAM_FIELD,
                description=self.tr("Champ paramètres additionnels"),
                parentLayerParameterName="INPUT",
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                name=self.STARTS_LAYER,
                description=self.tr("Départs"),
                types=[QgsProcessing.SourceType.TypeVectorPoint],
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.STARTS_LAYER_ID_FIELD,
                description=self.tr("Champ pour identifiant des départs"),
                parentLayerParameterName=self.STARTS_LAYER,
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                name=self.ENDS_LAYER,
                description=self.tr("Arrivées"),
                types=[QgsProcessing.SourceType.TypeVectorPoint],
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.ENDS_LAYER_ID_FIELD,
                description=self.tr("Champ pour identifiant des arrivées"),
                parentLayerParameterName=self.ENDS_LAYER,
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                name=self.INTERMEDIATES_LAYER,
                description=self.tr("Etapes"),
                types=[QgsProcessing.SourceType.TypeVectorPoint],
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.INTERMEDIATES_LAYER_ID_FIELD,
                description=self.tr("Champ pour identifiant des étapes"),
                parentLayerParameterName=self.INTERMEDIATES_LAYER,
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                name=self.CRS,
                description=self.tr("Système de coordonnées de sortie"),
                optional=True,
            )
        )

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
        self.url_service = self.parameterAsString(parameters, self.URL_SERVICE, context)

        self.param_id_start_field = self.parameterAsString(
            parameters, self.ID_START_FIELD, context
        )

        self.param_id_end_field = self.parameterAsString(
            parameters, self.ID_END_FIELD, context
        )
        self.param_id_intermediates_field = self.parameterAsString(
            parameters, self.ID_INTERMEDIATES_FIELD, context
        )
        self.param_ressource_field = self.parameterAsString(
            parameters, self.RESSOURCE_FIELD, context
        )
        self.param_profil_field = self.parameterAsString(
            parameters, self.PROFIL_FIELD, context
        )
        self.param_optimization_field = self.parameterAsString(
            parameters, self.OPTIMIZATION_FIELD, context
        )
        self.param_additionnal_url_param_field = self.parameterAsString(
            parameters, self.ADDITIONAL_URL_PARAM_FIELD, context
        )

        self.starts_layer = self.parameterAsVectorLayer(
            parameters, self.STARTS_LAYER, context
        )
        self.ends_layer = self.parameterAsVectorLayer(
            parameters, self.ENDS_LAYER, context
        )

        self.intermediates_layer = self.parameterAsVectorLayer(
            parameters, self.INTERMEDIATES_LAYER, context
        )

        self.id_start_field = self.parameterAsString(
            parameters, self.STARTS_LAYER_ID_FIELD, context
        )
        self.id_end_field = self.parameterAsString(
            parameters, self.ENDS_LAYER_ID_FIELD, context
        )
        if self.intermediates_layer is not None:
            self.id_intermediate_field = self.parameterAsString(
                parameters, self.INTERMEDIATES_LAYER_ID_FIELD, context
            )
            if not self.id_intermediate_field:
                feedback.reportError(
                    self.tr(
                        "Champ pour identifiant des étapes dans la couche non définie."
                    )
                )
                return False

        self.output_crs = self.parameterAsCrs(parameters, self.CRS, context)

        if self.output_crs is None:
            self.output_crs = self.starts_layer.crs()

        # All points for itinerary compute must be defined in project CRS
        # QgsProcessingParameterPoint always use project CRS
        self.start_transform = QgsCoordinateTransform(
            self.starts_layer.crs(),
            context.project().crs(),
            context.transformContext(),
        )
        self.end_transform = QgsCoordinateTransform(
            self.ends_layer.crs(),
            context.project().crs(),
            context.transformContext(),
        )

        self.result_transform = QgsCoordinateTransform(
            context.project().crs(),
            self.output_crs,
            context.transformContext(),
        )

        algo_str = (
            f"gpf_isochrone_isodistance_itineraire:{ItineraryProcessing().name()}"
        )
        self.alg = QgsApplication.processingRegistry().algorithmById(algo_str)

        return True

    def _define_id_intermediates(self, id_intermediates: Any) -> List[Any]:
        """Define id_intermediates list from feature field

        :param id_intermediates: value from feature
        :type id_intermediates: Any
        :return: list of id intermediates
        :rtype: List[Any]
        """
        # Convert str to list of values
        if isinstance(id_intermediates, str):
            if id_intermediates:
                result = id_intermediates.split(",")
            else:
                result = []
        # If not a list, create one with single value
        elif not isinstance(id_intermediates, list):
            result = [id_intermediates]
        # This is already a list, keep value
        else:
            result = id_intermediates

        return result

    def _create_intermediates_layer(
        self, id_intermediates: List[Any], feedback: QgsProcessingFeedback
    ) -> QgsVectorLayer:
        """Create intermediates layer from a list of id

        :param id_intermediates: list of id
        :type id_intermediates: List[Any]
        :param feedback: processing feedback
        :type feedback: QgsProcessingFeedback
        :return: layer with point from steps layer
        :rtype: QgsVectorLayer
        """

        intermediates_layer = QgsVectorLayer(
            f"Point?crs={self.intermediates_layer.crs()}", "intermediates", "memory"
        )
        intermediates_layer.startEditing()

        feedback.pushDebugInfo(
            self.tr("Liste des identifiants d'étapes {}").format(id_intermediates)
        )

        for id_ in id_intermediates:
            request_filter = f"{self.id_intermediate_field} = {id_}"

            intermediate_features = [
                f for f in self.intermediates_layer.getFeatures(request_filter)
            ]
            if len(intermediate_features) == 0:
                feedback.pushWarning(
                    self.tr(
                        "Identifiant {} non trouvé dans la couche des étapes"
                    ).format(id_)
                )
            for f in intermediate_features:
                point = QgsFeature()
                point.setGeometry(f.geometry())
                intermediates_layer.addFeature(point)
        intermediates_layer.commitChanges()

        return intermediates_layer

    def processFeature(
        self,
        feat: QgsFeature,
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
        id_start = feat[self.param_id_start_field]
        id_end = feat[self.param_id_end_field]
        id_resource = feat[self.param_ressource_field]
        profile = feat[self.param_profil_field]
        optimization = feat[self.param_optimization_field]

        feedback.pushInfo(
            self.tr(
                "Préparation calcul itinéraire pour id_start {} id_end {} id_resource {} profile {} optimization {}"
            ).format(id_start, id_end, id_resource, profile, optimization)
        )

        start_feature = [
            f
            for f in self.starts_layer.getFeatures(f"{self.id_start_field}={id_start}")
        ]
        if len(start_feature) != 0:
            start = start_feature[0].geometry().asPoint()
            start = self.start_transform.transform(start)
        else:
            feedback.pushWarning(
                self.tr("Identifiant {} non trouvé dans la couche de départs").format(
                    id_start
                )
            )
            return []

        end_feature = [
            f for f in self.ends_layer.getFeatures(f"{self.id_end_field}={id_end}")
        ]
        if len(end_feature) != 0:
            end = end_feature[0].geometry().asPoint()
            end = self.end_transform.transform(end)
        else:
            feedback.pushWarning(
                self.tr("Identifiant {} non trouvé dans la couche d'arrivées").format(
                    id_start
                )
            )
            return []

        params = {
            ItineraryProcessing.URL_SERVICE: self.url_service,
            ItineraryProcessing.ID_RESOURCE: id_resource,
            ItineraryProcessing.START: start,
            ItineraryProcessing.END: end,
            ItineraryProcessing.PROFILE: profile,
            ItineraryProcessing.OPTIMIZATION: optimization,
            ItineraryProcessing.OUTPUT: "TEMPORARY_OUTPUT",
        }

        if self.param_additionnal_url_param_field in feat.attributeMap():
            additional_url_param = feat[self.param_additionnal_url_param_field]
            params[ItineraryProcessing.ADDITIONAL_URL_PARAM] = additional_url_param

        if (
            self.intermediates_layer is not None
            and self.param_id_intermediates_field in feat.attributeMap()
        ):
            id_intermediates = self._define_id_intermediates(
                feat[self.param_id_intermediates_field]
            )
            params[ItineraryProcessing.INTERMEDIATES] = (
                self._create_intermediates_layer(id_intermediates, feedback)
            )

        results, successful = self.alg.run(params, context, feedback)
        if successful:
            res = results[ItineraryProcessing.OUTPUT]
            res_layer = context.getMapLayer(res)

            output_features = []
            for f in res_layer.getFeatures():
                new_feature = QgsFeature()
                new_feature.setFields(self.outputFields(feat.fields()))
                geom = f.geometry()
                geom.transform(self.result_transform)
                new_feature.setGeometry(geom)

                for field in res_layer.fields():
                    new_feature[field.name()] = f[field.name()]

                for field in feat.fields():
                    feat_field_name = field.name()
                    if feat_field_name == "fid":
                        feat_field_name = "fid_input"
                    new_feature[feat_field_name] = feat[field.name()]
                output_features.append(new_feature)
            return output_features
        else:
            return []

    def outputWkbType(self, _: Qgis.WkbType) -> Qgis.WkbType:
        """Maps the input WKB geometry type (inputWkbType) to the corresponding output WKB type generated by the algorithm.

        :param _: input WkbType (not used)
        :type _: Qgis.WkbType
        :return: output WkbType (alway Qgis.WkbType.LineString)
        :rtype: Qgis.WkbType
        """
        return Qgis.WkbType.LineString

    def outputFields(self, inputFields: QgsFields) -> QgsFields:
        """Maps the input source fields (inputFields) to corresponding output fields generated by the algorithm.

        :param inputFields: input fields
        :type inputFields: QgsFields
        :return: output fields
        :rtype: QgsFields
        """

        output_fields = ItineraryProcessing.get_output_fields()
        for f in inputFields:
            field = QgsField(f)
            field_name = field.name()
            if field_name == "fid":
                field.setName("fid_input")
            output_fields.append(field)
        return output_fields

    def outputCrs(
        self, _: QgsCoordinateReferenceSystem
    ) -> QgsCoordinateReferenceSystem:
        """Maps the input source coordinate reference system (inputCrs) to a corresponding output CRS generated by the algorithm.

        :param inputCrs: input crs
        :type inputCrs: QgsCoordinateReferenceSystem
        :return: output crs (defined in parameter or from start layer)
        :rtype: QgsCoordinateReferenceSystem
        """
        return self.output_crs

    def outputName(self) -> str:
        """Returns the translated, user visible name for any layers created by this algorithm.

        :return: _description_
        :rtype: str
        """
        return self.tr("Itinéraires")

    def inputLayerTypes(self) -> List[int]:
        """Returns the valid input layer types for the source layer for this algorithm.
        Only point vector are supported

        :return: list of supported input layer type
        :rtype: List[int]
        """
        return [Qgis.ProcessingSourceType.Vector]
