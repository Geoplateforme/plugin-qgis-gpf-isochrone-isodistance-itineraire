#! python3  # noqa: E265

"""
Main plugin module.
"""

# standard
from functools import partial
from pathlib import Path

# PyQGIS
from qgis.core import (
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsPointXY,
    QgsSettings,
)
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QCoreApplication, QLocale, Qt, QTranslator, QUrl
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.PyQt.QtWidgets import QAction, QDockWidget, QMenu, QWidget

# project
from gpf_isochrone_isodistance_itineraire.__about__ import (
    DIR_PLUGIN_ROOT,
    __icon_path__,
    __title__,
    __uri_homepage__,
)
from gpf_isochrone_isodistance_itineraire.gui.dlg_settings import PlgOptionsFactory
from gpf_isochrone_isodistance_itineraire.gui.wdg_iso_service import IsoServiceWidget
from gpf_isochrone_isodistance_itineraire.gui.wdg_itinerary import ItineraryWidget
from gpf_isochrone_isodistance_itineraire.processing.provider import (
    PluginGpfIsochroneIsodistanceItineraireProvider,
)
from gpf_isochrone_isodistance_itineraire.processing.utils import (
    create_processing_action,
)
from gpf_isochrone_isodistance_itineraire.toolbelt import PlgLogger

# ############################################################################
# ########## Classes ###############
# ##################################


class GpfIsochroneIsodistanceItinerairePlugin:
    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class which \
        provides the hook by which you can manipulate the QGIS application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.provider = None
        self.log = PlgLogger().log

        self.docks = []
        self.actions = []
        self.isoservice_widget_action = None
        self.itinerary_widget_action = None

        # translation
        # initialize the locale
        self.locale: str = QgsSettings().value("locale/userLocale", QLocale().name())[
            0:2
        ]
        locale_path: Path = (
            DIR_PLUGIN_ROOT
            / "resources"
            / "i18n"
            / f"{__title__.lower()}_{self.locale}.qm"
        )
        self.log(message=f"Translation: {self.locale}, {locale_path}", log_level=4)
        if locale_path.exists():
            self.translator = QTranslator()
            self.translator.load(str(locale_path.resolve()))
            QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        """Set up plugin UI elements."""

        # settings page within the QGIS preferences menu
        self.options_factory = PlgOptionsFactory()
        self.iface.registerOptionsWidgetFactory(self.options_factory)

        # -- Actions
        self.action_help = QAction(
            QgsApplication.getThemeIcon("mActionHelpContents.svg"),
            self.tr("Help"),
            self.iface.mainWindow(),
        )
        self.action_help.triggered.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_homepage__))
        )

        self.action_settings = QAction(
            QgsApplication.getThemeIcon("console/iconSettingsConsole.svg"),
            self.tr("Settings"),
            self.iface.mainWindow(),
        )
        self.action_settings.triggered.connect(
            lambda: self.iface.showOptionsDialog(
                currentPage="mOptionsPage{}".format(__title__)
            )
        )

        # -- Menu
        self.iface.addPluginToMenu(__title__, self.action_settings)
        self.iface.addPluginToMenu(__title__, self.action_help)

        # -- Help menu

        # documentation
        self.iface.pluginHelpMenu().addSeparator()
        self.action_help_plugin_menu_documentation = QAction(
            QIcon(str(__icon_path__)),
            f"{__title__} - Documentation",
            self.iface.mainWindow(),
        )
        self.action_help_plugin_menu_documentation.triggered.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_homepage__))
        )

        self.iface.pluginHelpMenu().addAction(
            self.action_help_plugin_menu_documentation
        )

        # -- Processing
        self.provider = PluginGpfIsochroneIsodistanceItineraireProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

        # Need to init widget after initializationCompleted because we are defining default crs in IsoServiceWidget
        # self.iface.initializationCompleted.connect(self._init_widget)
        # Better to init widget in initGui because the signal may not be emitted when we install the plugin after QGIS start
        # User will have to restart QGIS to get the widgets
        self._init_widget()

    def _init_widget(self) -> None:
        """Init widget for plugin after QGIS initialization"""

        # Create widget for isoservice
        isoservice_widget = IsoServiceWidget(self.iface.mainWindow())

        # Define default position
        isoservice_widget.wdg_point_selection.set_crs(
            QgsCoordinateReferenceSystem("EPSG:4326")
        )
        isoservice_widget.wdg_point_selection.set_display_point(
            QgsPointXY(2.42412, 48.84572)
        )

        # Add dockwidget with action
        self.isoservice_widget_action = self.add_dock_widget_and_action(
            title=self.tr("Calcul isochrone / isodistance"),
            name="isochrone_isodistance_compute",
            widget=isoservice_widget,
        )

        # Create widget for itinerary
        itinerary_widget = ItineraryWidget(self.iface.mainWindow())
        # Define default position
        itinerary_widget.wdg_start_selection.set_crs(
            QgsCoordinateReferenceSystem("EPSG:4326")
        )
        itinerary_widget.wdg_start_selection.set_display_point(
            QgsPointXY(2.42412, 48.84572)
        )

        itinerary_widget.wdg_end_selection.set_crs(
            QgsCoordinateReferenceSystem("EPSG:4326")
        )
        itinerary_widget.wdg_end_selection.set_display_point(
            QgsPointXY(2.42412, 48.84572)
        )

        self.itinerary_widget_action = self.add_dock_widget_and_action(
            title=self.tr("Calcul itinéraire"),
            name="itinerary_compute",
            widget=itinerary_widget,
        )

    def add_dock_widget_and_action(
        self, title: str, name: str, widget: QWidget
    ) -> QAction:
        """Add widget display as QDockWidget with an QAction in plugin toolbar


        :param name: dockwidget name for position save
        :type name: str
        :param widget: widget to insert
        :type widget: QWidget
        """

        # Create dockwidget
        dock = QDockWidget(title, self.iface.mainWindow())
        dock.setObjectName(name)
        dock.setWindowIcon(widget.windowIcon())

        # Add widget
        dock.setWidget(widget)

        # Add to QGIS
        self.iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

        # Default close
        dock.close()

        # Append to dock list for unload
        self.docks.append(dock)
        dock.toggleViewAction().setIcon(widget.windowIcon())

        # Append to action list for unload
        action = dock.toggleViewAction()
        self.actions.append(action)

        # Add action to toolbar
        self.iface.addToolBarIcon(action)

        return action

    def create_gpf_plugins_actions(self, parent: QWidget) -> list[QAction]:
        """Create action to be inserted a Geoplateforme plugin

        :param parent: parent widget
        :type parent: QWidget
        :return: list of action to add in Geoplateforme plugin
        :rtype: list[QAction]
        """
        available_actions = []

        # Isoservices actions
        iso_service_action = QAction(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/logo_isochrone.png")),
            self.tr("Isoservices"),
            parent,
        )
        iso_service_menu = QMenu()
        if self.isoservice_widget_action:
            iso_service_menu.addAction(self.isoservice_widget_action)

        # Isoservices Processings
        iso_service_action_processing = QAction(self.tr("Traitements"), parent)
        iso_service_menu_processing = QMenu(parent)
        iso_service_menu_processing.addAction(
            create_processing_action(
                "gpf_isochrone_isodistance_itineraire:isochrone_processing",
                iso_service_menu_processing,
            )
        )
        iso_service_menu_processing.addAction(
            create_processing_action(
                "gpf_isochrone_isodistance_itineraire:isodistance_processing",
                iso_service_menu_processing,
            )
        )

        iso_service_action_processing.setMenu(iso_service_menu_processing)

        iso_service_menu.addAction(iso_service_action_processing)

        iso_service_action.setMenu(iso_service_menu)

        available_actions.append(iso_service_action)

        # Itinerary actions
        itinerary_action = QAction(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/logo_itineraire.png")),
            self.tr("Itineraire"),
            parent,
        )
        itinerary_menu = QMenu()
        if self.itinerary_widget_action:
            itinerary_menu.addAction(self.itinerary_widget_action)

        # Itinerary Processings
        itinerary_action_processing = QAction(self.tr("Traitements"), parent)
        itinerary_menu_processing = QMenu(parent)
        itinerary_menu_processing.addAction(
            create_processing_action(
                "gpf_isochrone_isodistance_itineraire:itinerary",
                itinerary_menu_processing,
            )
        )

        itinerary_action_processing.setMenu(itinerary_menu_processing)

        itinerary_menu.addAction(itinerary_action_processing)

        itinerary_action.setMenu(itinerary_menu)

        available_actions.append(itinerary_action)

        return available_actions

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def unload(self):
        """Cleans up when plugin is disabled/uninstalled."""
        for _actions in self.actions:
            self.iface.removeToolBarIcon(_actions)
            del _actions
        for _dock in self.docks:
            self.iface.removeDockWidget(_dock)
            _dock.deleteLater()
        self.docks.clear()

        # -- Clean up menu
        self.iface.removePluginMenu(__title__, self.action_help)
        self.iface.removePluginMenu(__title__, self.action_settings)

        # -- Clean up preferences panel in QGIS settings
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)

        # remove from QGIS help/extensions menu
        if self.action_help_plugin_menu_documentation:
            self.iface.pluginHelpMenu().removeAction(
                self.action_help_plugin_menu_documentation
            )

        # remove actions
        del self.action_settings
        del self.action_help

        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)

    def run(self):
        """Main process.

        :raises Exception: if there is no item in the feed
        """
        try:
            self.log(
                message=self.tr("Everything ran OK."),
                log_level=3,
                push=False,
            )
        except Exception as err:
            self.log(
                message=self.tr("Houston, we've got a problem: {}".format(err)),
                log_level=2,
                push=True,
            )
