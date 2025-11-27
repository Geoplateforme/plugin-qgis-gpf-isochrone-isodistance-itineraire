# CHANGELOG

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

<!--

Unreleased

## version_tag - YYYY-DD-mm

### Added

### Changed

### Removed

-->

## 0.5.1 - 2025-11-27

* fix(isoservice): avoid error when using gpkg for output in processing by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/65>
* build(deps): bump actions/labeler from 5 to 6 by @dependabot[bot] in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/58>
* Packaging: declare plugin compatible qgis4 by @Guts in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/56>

## 0.5.0 - 2025-09-23

* fix(qt6): QMenu need a parent in Qt6 for correct use by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/52>
* feat(crs): always use EPSG:4326 for geoplateforme request by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/53>
* Feature: add processing to batch itinerary resolution by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/54>

## 0.4.0 - 2025-09-05

This release contains fixes for Qt6 use and documentation initialization.

* fix(ui): disable connect for marker update when updating min/max for spinbox by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/40>
* fix(qt6): no url param for QNetworkRequest by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/42>
* feat(processing): check if feature geometry is null by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/46>
* feat(ui): update icon to distinguish services by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/41>
* feat(ui): add action for widget and processing in menu by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/44>
* doc(processing): init documentation for processings by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/43>
* feat(isoservice): keep fields from input layer in result by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/45>
* feat(ui): add tooltip for resource selection by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/47>
* fix(ci): always run test and lint to be able to merge PR by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/39>
* build(deps): bump dawidd6/action-download-artifact from 9 to 11 by @dependabot[bot] in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/29>
* build(deps): bump actions/download-artifact from 4 to 5 by @dependabot[bot] in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/48>
* build(deps): bump actions/checkout from 4 to 5 by @dependabot[bot] in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/49>
* build(deps): bump actions/upload-pages-artifact from 3 to 4 by @dependabot[bot] in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/50>
* Update metadata.txt by @IGNF-Xavier in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/35>
* [pre-commit.ci] pre-commit autoupdate by @pre-commit-ci[bot] in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/30>

## 0.3.0 - 2025-05-28

First version with itinerary compute from Geoplateforme.

* fix(iti): raise error if API return error by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/24>
* feat(gpf): add function create_gpf_plugins_actions to be called by geoplateforme plugin by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/21>
* feat(itinerary): init processing by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/22>
* feat(itinerary): init widget for processing use (no steps possible) by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/23>

## 0.2.0-beta1 - 2025-04-29

* feat(getcap): check direction and cost type by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/6>
* feat(getcap): test if point is inside resource bbox by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/7>
* feat(isochrone): evaluate additional parameters and add to output field by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/8>
* feat(isochrone): check input crs and apply transformation if needed by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/9>
* test(getcap): unit test for parser by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/10>
* feat(isochrone): define parameters from expression by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/3>
* feat(isochrone): init processing by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/2>
* feat(getcap): test if isochrone available for service and resources by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/4>
* feat(getcap): test if profile is available for a resource by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/5>
* feat(getcap): use local cache to store getcap for a service url by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/11>
* feature(isodistance): add processing by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/12>
* feat(isoservice): add widget to use isoservice by @jmkerloch in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/16>
* fix(ci): make QGIS tests work again on new Docker images by @Guts in <https://github.com/Geoplateforme/plugin-qgis-gpf-isochrone-isodistance-itineraire/pull/1>

## 0.1.0 - 2025-04-07

* First release
* Generated with the [QGIS Plugins templater](https://oslandia.gitlab.io/qgis/template-qgis-plugin/)
