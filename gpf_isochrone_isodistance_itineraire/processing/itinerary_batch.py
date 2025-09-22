# standard
from typing import Any, Dict, Optional

# PyQGIS
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCoordinateTransform,
    QgsFeature,
    QgsField,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingParameterCrs,
    QgsProcessingParameterFeatureSink,
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


class BatchItineraryAlgorithm(QgsProcessingAlgorithm):
    URL_SERVICE = "URL_SERVICE"

    STARTS_LAYER = "STARTS_LAYER"
    STARTS_LAYER_ID_FIELD = "STARTS_LAYER_ID_FIELD"
    ENDS_LAYER = "ENDS_LAYER"
    ENDS_LAYER_ID_FIELD = "ENDS_LAYER_ID_FIELD"
    INTERMEDIATES_LAYER = "INTERMEDIATES_LAYER"
    INTERMEDIATES_LAYER_ID_FIELD = "INTERMEDIATES_LAYER_ID_FIELD"

    BATCH_PARAMETERS_LAYER = "BATCH_PARAMETERS_LAYER"

    ID_START_FIELD = "ID_START_FIELD"
    ID_END_FIELD = "ID_END_FIELD"
    ID_INTERMEDIATES_FIELD = "ID_INTERMEDIATES_FIELD"

    RESSOURCE_FIELD = "RESSOURCE_FIELD"
    PROFIL_FIELD = "PROFIL_FIELD"
    OPTIMIZATION_FIELD = "OPTIMIZATION_FIELD"

    ADDITIONAL_URL_PARAM_FIELD = "ADDITIONAL_URL_PARAM_FIELD"
    CRS = "CRS"
    OUTPUT = "OUTPUT"

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
        return self.tr("Livraison")

    def groupId(self):
        return ""

    def helpUrl(self):
        return get_user_manual_url(self.name())

    def shortHelpString(self):
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
            QgsProcessingParameterVectorLayer(
                name=self.BATCH_PARAMETERS_LAYER,
                description=self.tr("Paramètres calcul en lot"),
                types=[QgsProcessing.SourceType.TypeVector],
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.ID_START_FIELD,
                description=self.tr("Champ paramètre pour les départs"),
                parentLayerParameterName=self.BATCH_PARAMETERS_LAYER,
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.ID_END_FIELD,
                description=self.tr("Champ paramètre pour les arrivées"),
                parentLayerParameterName=self.BATCH_PARAMETERS_LAYER,
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.ID_INTERMEDIATES_FIELD,
                description=self.tr("Champ paramètre pour les étapes"),
                parentLayerParameterName=self.BATCH_PARAMETERS_LAYER,
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.RESSOURCE_FIELD,
                description=self.tr("champ paramètre pour les ressources"),
                parentLayerParameterName=self.BATCH_PARAMETERS_LAYER,
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.PROFIL_FIELD,
                description=self.tr("champ paramètre pour les profils"),
                parentLayerParameterName=self.BATCH_PARAMETERS_LAYER,
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.OPTIMIZATION_FIELD,
                description=self.tr("champ paramètre pour l'optimisation"),
                parentLayerParameterName=self.BATCH_PARAMETERS_LAYER,
                optional=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.ADDITIONAL_URL_PARAM_FIELD,
                description=self.tr("champ paramètre pour les paramètres additionnels"),
                parentLayerParameterName=self.BATCH_PARAMETERS_LAYER,
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

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.OUTPUT,
                description=self.tr("Itinéraire"),
                type=QgsProcessing.SourceType.VectorLine,
            )
        )

    def processAlgorithm(
        self,
        parameters: Dict[str, Any],
        context: QgsProcessingContext,
        feedback: Optional[QgsProcessingFeedback],
    ) -> Dict[str, Any]:
        """Runs the algorithm using the specified parameters.

        :param parameters: algorithm parameters
        :type parameters: Dict[str, Any]
        :param context: processing context
        :type context: QgsProcessingContext
        :param feedback: processing feedback
        :type feedback: Optional[QgsProcessingFeedback]
        :raises QgsProcessingException: Multiple crs for input layers
        :raises QgsProcessingException: Error in upload creation
        :return: algorithm results
        :rtype: Dict[str, Any]
        """

        url_service = self.parameterAsString(parameters, self.URL_SERVICE, context)
        starts_layer = self.parameterAsVectorLayer(
            parameters, self.STARTS_LAYER, context
        )
        ends_layer = self.parameterAsVectorLayer(parameters, self.ENDS_LAYER, context)

        intermediates_layer = self.parameterAsVectorLayer(
            parameters, self.INTERMEDIATES_LAYER, context
        )

        batch_param_layer = self.parameterAsVectorLayer(
            parameters, self.BATCH_PARAMETERS_LAYER, context
        )

        id_start_field = self.parameterAsString(
            parameters, self.STARTS_LAYER_ID_FIELD, context
        )
        id_end_field = self.parameterAsString(
            parameters, self.ENDS_LAYER_ID_FIELD, context
        )
        if intermediates_layer is not None:
            id_intermediate_field = self.parameterAsString(
                parameters, self.INTERMEDIATES_LAYER_ID_FIELD, context
            )
            if not id_intermediate_field:
                raise QgsProcessingException(
                    self.tr(
                        "Champ pour identifiant des étapes dans la couche non définie."
                    )
                )

        param_id_start_field = self.parameterAsString(
            parameters, self.ID_START_FIELD, context
        )

        param_id_end_field = self.parameterAsString(
            parameters, self.ID_END_FIELD, context
        )
        param_id_intermediates_field = self.parameterAsString(
            parameters, self.ID_INTERMEDIATES_FIELD, context
        )
        param_ressource_field = self.parameterAsString(
            parameters, self.RESSOURCE_FIELD, context
        )
        param_profil_field = self.parameterAsString(
            parameters, self.PROFIL_FIELD, context
        )
        param_optimization_field = self.parameterAsString(
            parameters, self.OPTIMIZATION_FIELD, context
        )
        param_additionnal_url_param_field = self.parameterAsString(
            parameters, self.ADDITIONAL_URL_PARAM_FIELD, context
        )

        if self.CRS in parameters:
            output_crs = self.parameterAsCrs(parameters, self.CRS, context)
        else:
            output_crs = starts_layer.crs()

        output_fields = ItineraryProcessing.get_output_fields()
        for f in batch_param_layer.fields():
            field = QgsField(f)
            field_name = field.name()
            if field_name == "fid":
                field.setName("fid_input")
            output_fields.append(field)

        # Get sink for output feature
        (sink_itinerary, sink_itinerary_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            output_fields,
            Qgis.WkbType.LineStringZ,
            output_crs,
        )

        algo_str = (
            f"gpf_isochrone_isodistance_itineraire:{ItineraryProcessing().name()}"
        )
        alg = QgsApplication.processingRegistry().algorithmById(algo_str)

        # All points for itinerary compute must be defined in project CRS
        # QgsProcessingParameterPoint always use project CRS
        start_transform = QgsCoordinateTransform(
            starts_layer.crs(),
            context.project().crs(),
            context.transformContext(),
        )
        end_transform = QgsCoordinateTransform(
            ends_layer.crs(),
            context.project().crs(),
            context.transformContext(),
        )

        result_transform = QgsCoordinateTransform(
            context.project().crs(),
            output_crs,
            context.transformContext(),
        )

        for feat in batch_param_layer.getFeatures():
            if feedback.isCanceled():
                break
            id_start = feat[param_id_start_field]
            id_end = feat[param_id_end_field]
            id_resource = feat[param_ressource_field]
            profile = feat[param_profil_field]
            optimization = feat[param_optimization_field]

            feedback.pushInfo(
                self.tr(
                    "Préparation calcul itinéraire pour id_start {} id_end {} id_resource {} profile {} optimization {}"
                ).format(id_start, id_end, id_resource, profile, optimization)
            )

            start_feature = [
                f for f in starts_layer.getFeatures(f"{id_start_field}={id_start}")
            ]
            if len(start_feature) != 0:
                start = start_feature[0].geometry().asPoint()
                start = start_transform.transform(start)
            else:
                feedback.pushWarning(
                    self.tr(
                        "Identifiant {} non trouvé dans la couche de départs"
                    ).format(id_start)
                )
                continue

            end_feature = [
                f for f in ends_layer.getFeatures(f"{id_end_field}={id_end}")
            ]
            if len(end_feature) != 0:
                end = end_feature[0].geometry().asPoint()
                end = end_transform.transform(end)
            else:
                feedback.pushWarning(
                    self.tr(
                        "Identifiant {} non trouvé dans la couche d'arrivées"
                    ).format(id_start)
                )
                continue

            params = {
                ItineraryProcessing.URL_SERVICE: url_service,
                ItineraryProcessing.ID_RESOURCE: id_resource,
                ItineraryProcessing.START: start,
                ItineraryProcessing.END: end,
                ItineraryProcessing.PROFILE: profile,
                ItineraryProcessing.OPTIMIZATION: optimization,
                ItineraryProcessing.OUTPUT: "TEMPORARY_OUTPUT",
            }

            if param_additionnal_url_param_field in feat.attributeMap():
                additional_url_param = feat[param_additionnal_url_param_field]
                params[ItineraryProcessing.ADDITIONAL_URL_PARAM] = additional_url_param

            if (
                intermediates_layer is not None
                and param_id_intermediates_field in feat.attributeMap()
            ):
                id_intermediates = feat[param_id_intermediates_field]

                if isinstance(id_intermediates, str):
                    if id_intermediates:
                        id_intermediates = id_intermediates.split(",")
                    else:
                        id_intermediates = []

                if not isinstance(id_intermediates, list):
                    id_intermediates = [id_intermediates]

                current_intermediates_layer = QgsVectorLayer(
                    f"Point?crs={intermediates_layer.crs()}", "intermediates", "memory"
                )
                current_intermediates_layer.startEditing()

                feedback.pushDebugInfo(
                    self.tr("Liste des identifiants d'étapes {}").format(
                        id_intermediates
                    )
                )

                for id_ in id_intermediates:
                    request_filter = f"{id_intermediate_field} = {id_}"

                    intermediate_features = [
                        f for f in intermediates_layer.getFeatures(request_filter)
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
                        current_intermediates_layer.addFeature(point)
                current_intermediates_layer.commitChanges()
                params[ItineraryProcessing.INTERMEDIATES] = current_intermediates_layer

            results, successful = alg.run(params, context, feedback)
            if successful:
                res = results[ItineraryProcessing.OUTPUT]
                res_layer = context.getMapLayer(res)
                for f in res_layer.getFeatures():
                    new_feature = QgsFeature()
                    new_feature.setFields(output_fields)
                    geom = f.geometry()
                    geom.transform(result_transform)
                    new_feature.setGeometry(geom)

                    for field in res_layer.fields():
                        new_feature[field.name()] = f[field.name()]

                    for field in batch_param_layer.fields():
                        feat_field_name = field.name()
                        if feat_field_name == "fid":
                            feat_field_name = "fid_input"
                        new_feature[feat_field_name] = feat[field.name()]
                    sink_itinerary.addFeature(new_feature)

        return {self.OUTPUT: sink_itinerary_id}
