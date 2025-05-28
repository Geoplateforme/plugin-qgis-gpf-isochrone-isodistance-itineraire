# CHANGELOG

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

<!--

Unreleased

## version_tag - YYYY-DD-mm

### Added

### Changed

### Removed

-->

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
