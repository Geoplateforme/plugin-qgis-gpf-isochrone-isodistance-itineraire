# standard
import shutil
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

# PyQGIS
from qgis.core import Qgis
from qgis.PyQt.QtCore import QByteArray, QCoreApplication, QFile, QIODevice

# project
import gpf_isochrone_isodistance_itineraire.toolbelt.log_handler as log_hdlr
from gpf_isochrone_isodistance_itineraire.toolbelt.application_folder import get_app_dir


class CacheManager:
    """Class for local cache management."""

    def __init__(self, app_prefix: str, dir_name: str):
        """Init CacheManager class
        For example on  linux with app_prefix = .qgis and dir_name = oslandia
        cache_path = /home/toto/.qgis/plugin_oslandia/

        :param app_prefix: Name of folder to prefix cache path
        :type app_prefix: str
        :param dir_name: Name of filder un prefix cache path
        :type dir_name: str
        """

        self.cache_dir = get_app_dir(dir_name=dir_name, app_prefix=app_prefix)
        self.log = log_hdlr.PlgLogger().log

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    @property
    def get_cache_path(self) -> Path:
        """Return cache path

        :return: Cache path
        :rtype: Path
        """
        return self.cache_dir

    @staticmethod
    def url_to_dirname(url: str) -> str:
        parsed = urlparse(url)
        # Get base url
        netloc = parsed.netloc
        # Replace / by _
        path = parsed.path.strip("/").replace("/", "_")
        return f"{netloc}_{path}" if path else netloc

    def getcapabilities_cache_path(self, url_service: str) -> Path:
        """Return cache path for a project upload

        :param project_id: project id
        :type project_id: str
        :param upload_secret_and_name: "/uploads/{upload_secret}/{filename}" string
        :type upload_secret_and_name: str
        :return: upload cache path
        :rtype: Path
        """
        dir_name = self.url_to_dirname(url_service)
        return self.cache_dir / "getcapabilities" / dir_name

    def load_cache_file_content(self, cache_file: Path) -> Optional[QByteArray]:
        """Load cache file content if available

        :param cache_file: cache file path
        :type cache_file: Path
        :return: file content if available and can be opened, None otherwise
        :rtype: Optional[QByteArray]
        """
        # Load cache file if it exists
        if cache_file.exists():
            file = QFile(str(cache_file))
            if file.open(QIODevice.OpenModeFlag.ReadOnly):
                bytea = QByteArray(file.readAll())
                file.close()
                return bytea
            else:
                file.close()
                err_msg = self.tr("Can't open cache file: {}".format(cache_file))
                self.log(
                    message=err_msg, log_level=Qgis.MessageLevel.Critical, push=True
                )
        return None

    def save_cache_file_content(self, cache_file: Path, content: QByteArray) -> None:
        """Save cache file content

        :param cache_file: cache file path
        :type cache_file: Path
        :param content: cache content
        :type content: QByteArray
        """
        # Save to cache
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        file = QFile(str(cache_file))
        if file.open(QIODevice.OpenModeFlag.WriteOnly):
            file.write(content)
            file.close()
        else:
            err_msg = self.tr("Can't open cache file for write: {}".format(cache_file))
            self.log(message=err_msg, log_level=Qgis.MessageLevel.Critical, push=True)

    def ensure_cache_dir_exists(self) -> bool:
        """Check if cache_dir exists

        :return: True the cache dir already exists, otherwise false.
        :rtype: bool
        """
        if not self.cache_dir.exists():
            self.log(
                message=f"The cache folder {self.cache_dir} doesn't exist.",
                log_level=Qgis.MessageLevel.Info,
            )
            return False
        else:
            self.log(
                message=f"Cache dir {self.cache_dir} already exists.",
                log_level=Qgis.MessageLevel.Info,
            )
            return True

    def create_cache_dir(self) -> None:
        """Create cache_dir"""
        if not self.ensure_cache_dir_exists():
            self.cache_dir.mkdir(parents=True)
            self.log(
                message=f"Cache dir {self.cache_dir} has been created.",
                log_level=Qgis.MessageLevel.NoLevel,
            )

    def clear_cache(self) -> None:
        """Delete the cache_dir project"""
        if self.ensure_cache_dir_exists():
            shutil.rmtree(self.cache_dir)
            self.log(
                message=self.tr(
                    "Cache dir {} has been removed.".format(self.cache_dir)
                ),
                log_level=Qgis.MessageLevel.Info,
                push=True,
            )
