# GPF - Isochrone Isodistance Itinéraire - QGIS Plugin

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)


[![flake8](https://img.shields.io/badge/linter-flake8-green)](https://flake8.pycqa.org/)

## Generated options

### Plugin

| Cookiecutter option | Picked value |
| :-- | :--: |
| Plugin name | GPF - Isochrone Isodistance Itinéraire |
| Plugin name slugified | gpf_isochrone_isodistance_itineraire |
| Plugin name class (used in code) | PluginGpfIsochroneIsodistanceItineraire |
| Plugin category | Web |
| Plugin description short | Utiliser le service de calcul d'isochrone, isodistance et d'itinéraire de la Géoplateforme |
| Plugin description long | Intégration de l'API de la Géoplateforme de calcul d'isochrone, d'isodisance et d'itinéraires dans QGIS. |
| Plugin tags | IGN,Géoplateforme,itinéraire,isochone,isodistance,routing,API,Valhalla,pgRouting,OSRM |
| Plugin icon | default_icon.png |
| Plugin with processing provider | True |
| Author name | Julien Moura |
| Author organization | Oslandia |
| Author email | julien.moura@oslandia.com |
| Minimum QGIS version | 3.40.0 |
| Maximum QGIS version | 3.99.0 |
| Support Qt6 | True |
| Git repository URL | https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/ |
| Git default branch | main |
| License | GPLv2+ |
| Python linter | Flake8 |
| CI/CD platform | GitHub |
| IDE | VSCode |

### Tooling

This project is configured with the following tools:

- [Black](https://black.readthedocs.io/en/stable/) to format the code without any existential question
- [iSort](https://pycqa.github.io/isort/) to sort the Python imports

Code rules are enforced with [pre-commit](https://pre-commit.com/) hooks.  
Static code analisis is based on: Flake8

See also: [contribution guidelines](CONTRIBUTING.md).

## CI/CD

Plugin is linted, tested, packaged and published with GitHub.

If you mean to deploy it to the [official QGIS plugins repository](https://plugins.qgis.org/), remember to set your OSGeo credentials (`OSGEO_USER_NAME` and `OSGEO_USER_PASSWORD`) as environment variables in your CI/CD tool.


### Documentation

The documentation is generated using Sphinx and is automatically generated through the CI and published on Pages.

- homepage: <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/>
- repository: <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/>
- tracker: <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire//issues/>

----

## Next steps

### Set up development environment

> Typical commands on Linux (Ubuntu).

1. If you don't pick the `git init` option, initialize your local repository:

    ```sh
    git init
    ```

1. Follow the [embedded documentation to set up your development environment](./docs/development/environment.md)
1. Add all files to git index to prepare initial commit:

    ```sh
    git add -A
    ```

1. Run the git hooks to ensure that everything runs OK and to start developing on quality standards:

    ```sh
    pre-commit run -a
    ```

### Try to build documentation locally

1. Have a look to the [plugin's metadata.txt file](gpf_isochrone_isodistance_itineraire/metadata.txt): review it, complete it or fix it if needed (URLs, etc.).
1. Follow the [embedded documentation to build plugin documentation locally](./docs/development/environment.md)

----

## License

Distributed under the terms of the [`GPLv2+` license](LICENSE).
