# standard
from pathlib import Path
from typing import Optional

# PyQgis
from qgis import processing
from qgis.core import Qgis, QgsApplication
from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtWidgets import QAction

# project
from gpf_isochrone_isodistance_itineraire.__about__ import __uri_homepage__
from gpf_isochrone_isodistance_itineraire.toolbelt.log_handler import PlgLogger


def get_locale_prefix() -> str:
    """Return prefix to used for localized help

    :return: locale prefix
    :rtype: str
    """
    return ""


def get_user_manual_url(processing_name: str) -> str:
    """Return url to user manual for a processing

    :param processing_name: processing name
    :type processing_name: str
    :return: user manual url
    :rtype: str
    """
    # Need to avoid use of _ in labels for Myst. Replacing with -
    fixed_processing_name = processing_name.replace("_", "-")
    return f"{__uri_homepage__}usage/{get_locale_prefix()}processings.html#{fixed_processing_name}"


def get_short_string(processing_name: str, default_help_str: str) -> str:
    """Get short string help for a processing.
    Use value defined in ../resources/help/locale_prefixe_processing_name.md if available.
    Otherwise, default_help_str is used

    :param processing_name: processing name
    :type processing_name: str
    :param default_help_str: default help string if no value available
    :type default_help_str: str
    :return: processing short string help
    :rtype: str
    """
    current_dir = Path(__file__).parent.resolve()
    help_md = current_dir.joinpath(
        "..", "resources", "help", f"{get_locale_prefix()}{processing_name}.md"
    )
    help_str = default_help_str
    if help_md.exists():
        with help_md.open(mode="r", encoding="UTF-8") as help_file:
            help_str = "".join(help_file.readlines())
    else:
        PlgLogger().log(
            f"Help not found for '{processing_name}', fallback to default value.",
            log_level=Qgis.MessageLevel.Warning,
            push=False,
        )
    return help_str


def create_processing_action(algorithm_id: str, parent: QObject) -> Optional[QAction]:
    """Create action to display a processing dialog for an algorithm

    :param algorithm_id: algorithm id
    :type algorithm_id: str
    :param parent: parent for QAction
    :type parent: QObject
    :return: QAction connected to processing dialog display, None if processing is not available.
    :rtype: Optional[QAction]
    """
    registry = QgsApplication.processingRegistry()
    alg = registry.algorithmById(algorithm_id)

    if alg is None:
        PlgLogger().log(
            f"Algorithme '{algorithm_id}' non trouvé.",
            log_level=Qgis.MessageLevel.Warning,
        )
        return None

    action = QAction(alg.icon(), alg.displayName(), parent)
    action.setToolTip(alg.shortHelpString())

    action.triggered.connect(lambda: processing.execAlgorithmDialog(algorithm_id))

    return action
