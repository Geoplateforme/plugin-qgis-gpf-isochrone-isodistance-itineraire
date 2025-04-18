# standard
import json
from typing import Any, Dict, List, Optional

# PyQGIS
from qgis.core import Qgis, QgsBlockingNetworkRequest, QgsRectangle
from qgis.PyQt.QtCore import QUrl, QVariant
from qgis.PyQt.QtNetwork import QNetworkRequest

from gpf_isochrone_isodistance_itineraire.constants import ISOCHRONE_OPERATION
from gpf_isochrone_isodistance_itineraire.toolbelt.log_handler import PlgLogger
from gpf_isochrone_isodistance_itineraire.toolbelt.preferences import PlgOptionsManager

# ############################################################################
# ########## GLOBALS #############
# ################################

# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def isochrone_available_for_service(url_service: Optional[str] = None) -> bool:
    """Check if isochrone is available for service

    :param url_service: url for service, defaults to None (plugin settings param is used)
    :type url_service: Optional[str], optional
    :return: True if isochrone is available for service, False otherwise
    :rtype: bool
    """
    return ISOCHRONE_OPERATION in get_available_operation(url_service)


def get_available_operation(url_service: Optional[str] = None) -> List[str]:
    """Get list of available operation for a service

    :param url_service: url for service, defaults to None (plugin settings param is used)
    :type url_service: Optional[str], optional
    :return: list of available operations
    :rtype: List[str]
    """
    data = download_getcapabilities(url_service)
    if data and "operations" in data:
        return [op["id"] for op in data["operations"]]
    return []


def isochrone_available_for_resource(
    id_resource: str, url_service: Optional[str] = None
) -> bool:
    """Check if isochrone is available for a resource

    :param id_resource: id resource
    :type id_resource: str
    :param url_service: url for service, defaults to None (plugin settings param is used)
    :type url_service: Optional[str], optional
    :return: True if isochrone is available for resource, False otherwise
    :rtype: bool
    """
    available_resources = get_available_resources(url_service, ISOCHRONE_OPERATION)
    return id_resource in available_resources


def get_available_resources(
    url_service: Optional[str] = None,
    operation: Optional[str] = None,
) -> List[str]:
    """Get list of available resources for a service.
    Optional operation filter can be used to get only resource with specific operation

    :param url_service: url for service, defaults to None (plugin settings param is used)
    :type url_service: Optional[str], optional
    :param operation: operation filter for resource, defaults to None
    :type operation: Optional[str], optional
    :return: list of available resources
    :rtype: List[str]
    """
    data = download_getcapabilities(url_service)
    if data and "resources" in data:
        # If no operation filter return all resources
        if operation is None:
            return [res["id"] for res in data["resources"]]

        # Parse resources to get available operation and check filter
        result = []
        for res in data["resources"]:
            available_operation = [op["id"] for op in res["availableOperations"]]
            if operation in available_operation:
                result.append(res["id"])

        return result
    return []


def get_resource_operation_parameters(
    id_resource: str, operation: str, url_service: Optional[str] = None
) -> Optional[List[Any]]:
    """Get resource operation parameter list

    :param id_resource: id resource
    :type id_resource: str
    :param operation: operation
    :type operation: str
    :param url_service: url for service, defaults to None (plugin settings param is used)
    :type url_service: Optional[str], optional
    :return: list of operation parameters
    :rtype: Optional[List[Any]]
    """
    data = download_getcapabilities(url_service)

    if data and "resources" in data:
        # Parse resources to get available operation and check filter
        for res in data["resources"]:
            if (
                "id" in res
                and "availableOperations" in res
                and res["id"] == id_resource
            ):
                for op in res["availableOperations"]:
                    if (
                        "id" in op
                        and "availableParameters" in op
                        and op["id"] == operation
                    ):
                        return op["availableParameters"]

    return None


def get_resource_operation_parameters_values(
    parameter: str, id_resource: str, operation: str, url_service: Optional[str] = None
) -> List[Optional[QVariant]]:
    """Get resource operation parameter values list

    :param parameter: parameter name
    :type parameter: str
    :param id_resource: id resource
    :type id_resource: str
    :param operation: operation
    :type operation: str
    :param url_service: url for service, defaults to None (plugin settings param is used)
    :type url_service: Optional[str], optional
    :return: list of operation parameters
    :rtype: List[Optional[QVariant]]
    """
    params = get_resource_operation_parameters(
        id_resource=id_resource, operation=operation, url_service=url_service
    )
    if not params:
        return []

    for param in params:
        if param["id"] == parameter and "values" in param:
            return param["values"]
    return []


def get_resource_operation_parameters_default_value(
    parameter: str, id_resource: str, operation: str, url_service: Optional[str] = None
) -> Optional[Any]:
    """Get resource operation parameter default value

    :param parameter: parameter name
    :type parameter: str
    :param id_resource: id resource
    :type id_resource: str
    :param operation: operation
    :type operation: str
    :param url_service: url for service, defaults to None (plugin settings param is used)
    :type url_service: Optional[str], optional
    :return: default value for parameter if available, None otherwise
    :rtype: Optional[Any]
    """
    params = get_resource_operation_parameters(
        id_resource=id_resource, operation=operation, url_service=url_service
    )
    if not params:
        return []

    for param in params:
        if param["id"] == parameter and "defaultValue" in param:
            return param["defaultValue"]
    return []


def get_resource_profiles(
    id_resource: str, operation: str, url_service: Optional[str] = None
) -> List[str]:
    """Get list of resource profile for an operation

    :param id_resource: id resource
    :type id_resource: str
    :param operation: operation
    :type operation: str
    :param url_service: url for service, defaults to None (plugin settings param is used)
    :type url_service: Optional[str], optional
    :return: list of profiles for a resource
    :rtype: List[str]
    """
    return get_resource_operation_parameters_values(
        parameter="profile",
        id_resource=id_resource,
        operation=operation,
        url_service=url_service,
    )


def get_resource_crs(
    id_resource: str, operation: str, url_service: Optional[str] = None
) -> List[str]:
    """Get list of resource crs for an operation

    :param id_resource: id resource
    :type id_resource: str
    :param operation: operation
    :type operation: str
    :param url_service: url for service, defaults to None (plugin settings param is used)
    :type url_service: Optional[str], optional
    :return: list of crs for a resource
    :rtype: List[str]
    """
    if operation == ISOCHRONE_OPERATION:
        return get_resource_operation_parameters_values(
            parameter="projection",
            id_resource=id_resource,
            operation=operation,
            url_service=url_service,
        )
    return get_resource_operation_parameters_values(
        parameter="crs",
        id_resource=id_resource,
        operation=operation,
        url_service=url_service,
    )


def get_resource_default_crs(
    id_resource: str, operation: str, url_service: Optional[str] = None
) -> Optional[str]:
    """Get resource default crs for an operation

    :param id_resource: id resource
    :type id_resource: str
    :param operation: operation
    :type operation: str
    :param url_service: url for service, defaults to None (plugin settings param is used)
    :type url_service: Optional[str], optional
    :return: default crs for a resource, None if not available
    :rtype: Optional[str]
    """
    if operation == ISOCHRONE_OPERATION:
        return get_resource_operation_parameters_default_value(
            parameter="projection",
            id_resource=id_resource,
            operation=operation,
            url_service=url_service,
        )
    return get_resource_operation_parameters_default_value(
        parameter="crs",
        id_resource=id_resource,
        operation=operation,
        url_service=url_service,
    )


def get_resource_param_bbox(
    parameter: str, id_resource: str, operation: str, url_service: Optional[str] = None
) -> Optional[QgsRectangle]:
    """Get resource bbox for an operation

    :param id_resource: id resource
    :type id_resource: str
    :param operation: operation
    :type operation: str
    :param url_service: url for service, defaults to None (plugin settings param is used)
    :type url_service: Optional[str], optional
    :return: bbox for resource, None if bbox can't be defined
    :rtype: Optional[QgsRectangle]
    """
    params = get_resource_operation_parameters(
        id_resource=id_resource, operation=operation, url_service=url_service
    )
    if not params:
        return None

    for param in params:
        if param["id"] == parameter:
            bbox_str = param["values"]["bbox"]
            try:
                values = bbox_str.split(",")
                return QgsRectangle(
                    float(values[0]),
                    float(values[1]),
                    float(values[2]),
                    float(values[3]),
                )
            except ValueError:
                return None
    return None


def get_resource_direction(
    id_resource: str, url_service: Optional[str] = None
) -> List[str]:
    """Get list of direction for an isochrone operation

    :param id_resource: id resource
    :type id_resource: str
    :param url_service: url for service, defaults to None (plugin settings param is used)
    :type url_service: Optional[str], optional
    :return: list of profiles for a resource
    :rtype: List[str]
    """
    return get_resource_operation_parameters_values(
        parameter="direction",
        id_resource=id_resource,
        operation=ISOCHRONE_OPERATION,
        url_service=url_service,
    )


def get_resource_cost_type(
    id_resource: str, url_service: Optional[str] = None
) -> List[str]:
    """Get list of costType for an isochrone operation

    :param id_resource: id resource
    :type id_resource: str
    :param url_service: url for service, defaults to None (plugin settings param is used)
    :type url_service: Optional[str], optional
    :return: list of profiles for a resource
    :rtype: List[str]
    """
    return get_resource_operation_parameters_values(
        parameter="costType",
        id_resource=id_resource,
        operation=ISOCHRONE_OPERATION,
        url_service=url_service,
    )


def download_getcapabilities(
    url_service: Optional[str] = None, forceRefresh: bool = False
) -> Optional[Dict[str, Any]]:
    """Download getcapabilities json content for a service

    :param url_service: url for service, defaults to None (plugin settings param is used)
    :type url_service: Optional[str], optional
    :return: json content for getcapabilities, None if error
    :rtype: Optional[Dict[str, Any]]
    """
    if not url_service:
        plg_settings = PlgOptionsManager().get_plg_settings()
        url_service = plg_settings.url_service

    url = f"{url_service}/getcapabilities"

    blocking_req = QgsBlockingNetworkRequest()
    qreq = QNetworkRequest(url=QUrl(url))
    error_code = blocking_req.get(qreq, forceRefresh=forceRefresh)

    # Add feedback in case of error
    if error_code != QgsBlockingNetworkRequest.ErrorCode.NoError:
        PlgLogger().log(
            f"Error for getcapabilities '{url}' : {blocking_req.errorMessage()}",
            log_level=Qgis.MessageLevel.Warning,
        )
        return None

    data = json.loads(str(blocking_req.reply().content(), "UTF8"))
    return data
