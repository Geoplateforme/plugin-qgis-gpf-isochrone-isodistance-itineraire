# standard
import unittest
from unittest.mock import MagicMock, patch

# pyQGIS
from qgis.core import QgsRectangle

# project
import gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser as getcap


class TestGetCapabilitiesParser(unittest.TestCase):
    ISOCHRONE_RESOURCE = "iso_resource"
    ROUTE_RESOURCE = "route_resource"

    def setUp(self):
        self.mock_data = {
            "operations": [
                {"id": "isochrone"},
                {"id": "route"},
            ],
            "resources": [
                {
                    "id": self.ISOCHRONE_RESOURCE,
                    "availableOperations": [
                        {
                            "id": "isochrone",
                            "availableParameters": [
                                {"id": "profile", "values": ["bike", "car"]},
                                {
                                    "id": "projection",
                                    "values": ["EPSG:4326"],
                                    "defaultValue": "EPSG:4326",
                                },
                                {"id": "direction", "values": ["forward", "backward"]},
                                {"id": "costType", "values": ["time", "distance"]},
                                {"id": "bbox", "values": {"bbox": "0.0,0.0,10.0,10.0"}},
                            ],
                        }
                    ],
                },
                {
                    "id": self.ROUTE_RESOURCE,
                    "availableOperations": [
                        {
                            "id": "route",
                            "availableParameters": [
                                {"id": "profile", "values": ["bike", "car"]},
                                {
                                    "id": "projection",
                                    "values": ["EPSG:4326"],
                                    "defaultValue": "EPSG:4326",
                                },
                                {"id": "bbox", "values": {"bbox": "0.0,0.0,10.0,10.0"}},
                            ],
                        }
                    ],
                },
            ],
        }

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_isochrone_available_for_service(self, mock_download):
        """Test isochrone service available in operations

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        mock_download.return_value = self.mock_data
        self.assertTrue(getcap.isochrone_available_for_service())

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_isochrone_not_available_for_service(self, mock_download):
        """Test when service is not available

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        # The exact name is isochrone, isodistance is not a valid operation
        mock_download.return_value = {"operations": [{"id": "isodistance"}]}
        self.assertFalse(getcap.isochrone_available_for_service())

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_get_available_operation(self, mock_download: MagicMock):
        """Check read of available operation

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        mock_download.return_value = self.mock_data
        operations = getcap.get_available_operation()
        self.assertIn("isochrone", operations)
        self.assertIn("route", operations)

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_isochrone_available_for_resource(self, mock_download: MagicMock):
        """Check of isochrone operation for a resource

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        mock_download.return_value = self.mock_data
        self.assertTrue(
            getcap.isochrone_available_for_resource(self.ISOCHRONE_RESOURCE)
        )

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_isochrone_not_available_for_resource(self, mock_download: MagicMock):
        """Check of isochrone operation for a resource

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        mock_download.return_value = self.mock_data
        self.assertFalse(getcap.isochrone_available_for_resource(self.ROUTE_RESOURCE))

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_isochrone_for_invalid_resource(self, mock_download: MagicMock):
        """Check of isochrone operation for a invalid resource

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        mock_download.return_value = self.mock_data
        self.assertFalse(getcap.isochrone_available_for_resource("unavailable"))

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_get_available_resources(self, mock_download: MagicMock):
        """Get list of available resources for an operation

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        mock_download.return_value = self.mock_data
        resources = getcap.get_available_resources(operation="isochrone")
        self.assertIn(self.ISOCHRONE_RESOURCE, resources)
        self.assertNotIn(self.ROUTE_RESOURCE, resources)

        resources = getcap.get_available_resources(operation="route")
        self.assertNotIn(self.ISOCHRONE_RESOURCE, resources)
        self.assertIn(self.ROUTE_RESOURCE, resources)

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_get_resource_operation_parameters(self, mock_download: MagicMock):
        """Get list of available parameter for a resource operation

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        mock_download.return_value = self.mock_data
        params = getcap.get_resource_operation_parameters(
            self.ISOCHRONE_RESOURCE, "isochrone"
        )
        self.assertIsInstance(params, list)
        self.assertEqual(len(params), 5)

        # Check None is returned for invalid resource
        params = getcap.get_resource_operation_parameters("invalid", "isochrone")
        self.assertIsNone(params)

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_get_resource_operation_parameters_values(self, mock_download: MagicMock):
        """Get list of available parameter values for a resource operation

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        mock_download.return_value = self.mock_data
        params = getcap.get_resource_operation_parameters_values(
            "profile", self.ISOCHRONE_RESOURCE, "isochrone"
        )
        self.assertIsInstance(params, list)
        self.assertEqual(len(params), 2)
        self.assertIn("bike", params)

        # Check empty list is returned for invalid resource
        params = getcap.get_resource_operation_parameters_values(
            "profile", "invalid", "isochrone"
        )
        self.assertIsInstance(params, list)
        self.assertEqual(len(params), 0)

        # Check empty list is returned for invalid resource
        params = getcap.get_resource_operation_parameters_values(
            "costType", self.ROUTE_RESOURCE, "route"
        )
        self.assertIsInstance(params, list)
        self.assertEqual(len(params), 0)

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_get_resource_profiles(self, mock_download: MagicMock):
        """Get list of available profile for a resource operation

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        mock_download.return_value = self.mock_data
        profiles = getcap.get_resource_profiles(self.ISOCHRONE_RESOURCE, "isochrone")
        self.assertIn("bike", profiles)

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_get_resource_crs(self, mock_download: MagicMock):
        """Get list of available crs for a resource operation

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        mock_download.return_value = self.mock_data
        crs = getcap.get_resource_crs(self.ISOCHRONE_RESOURCE, "isochrone")
        self.assertIn("EPSG:4326", crs)

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_get_resource_default_crs(self, mock_download: MagicMock):
        """Get default crs for a resource operation

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        mock_download.return_value = self.mock_data
        default_crs = getcap.get_resource_default_crs(
            self.ISOCHRONE_RESOURCE, "isochrone"
        )
        self.assertEqual(default_crs, "EPSG:4326")

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_get_resource_direction(self, mock_download: MagicMock):
        """Get direction for a resource operation

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        mock_download.return_value = self.mock_data
        directions = getcap.get_resource_direction(self.ISOCHRONE_RESOURCE)
        self.assertIn("forward", directions)

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_get_resource_cost_type(self, mock_download: MagicMock):
        """Get cost type for a resource operation

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        mock_download.return_value = self.mock_data
        cost_types = getcap.get_resource_cost_type(self.ISOCHRONE_RESOURCE)
        self.assertIn("time", cost_types)

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_get_resource_param_bbox(self, mock_download: MagicMock):
        """Get bbox for a resource operation

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        mock_download.return_value = self.mock_data
        bbox = getcap.get_resource_param_bbox(
            "bbox", self.ISOCHRONE_RESOURCE, "isochrone"
        )
        self.assertIsInstance(bbox, QgsRectangle)
        self.assertEqual(
            (bbox.xMinimum(), bbox.yMinimum(), bbox.xMaximum(), bbox.yMaximum()),
            (0.0, 0.0, 10.0, 10.0),
        )

        # Invalid resource
        bbox = getcap.get_resource_param_bbox("bbox", "invalid", "isochrone")
        self.assertIsNone(bbox)

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_get_available_operation_with_empty_data(self, mock_download: MagicMock):
        """Check empty operation return for empty getcap

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        mock_download.return_value = {}
        operations = getcap.get_available_operation()
        self.assertEqual(operations, [])

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_get_available_resources_with_missing_operations(
        self, mock_download: MagicMock
    ):
        """Check empty resource return for operation

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        mock_download.return_value = {
            "resources": [{"id": "res1", "availableOperations": []}]
        }
        resources = getcap.get_available_resources(operation="isochrone")
        self.assertEqual(resources, [])

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_get_resource_operation_parameters_invalid_resource(
        self, mock_download: MagicMock
    ):
        """Check None return for invalid resource

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        mock_download.return_value = self.mock_data
        params = getcap.get_resource_operation_parameters(
            "unknown_resource", "isochrone"
        )
        self.assertIsNone(params)

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_get_resource_operation_parameters_invalid_operation(
        self, mock_download: MagicMock
    ):
        """Check None return for invalid operation parameter

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        mock_download.return_value = self.mock_data
        params = getcap.get_resource_operation_parameters(
            self.ISOCHRONE_RESOURCE, "unknown_operation"
        )
        self.assertIsNone(params)

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_get_resource_param_bbox_missing_bbox(self, mock_download: MagicMock):
        """Check None return for missing bbox

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        broken_data = {
            "resources": [
                {
                    "id": "my_resource",
                    "availableOperations": [
                        {"id": "isochrone", "availableParameters": []}
                    ],
                }
            ]
        }
        mock_download.return_value = broken_data
        bbox = getcap.get_resource_param_bbox("bbox", "my_resource", "isochrone")
        self.assertIsNone(bbox)

    @patch(
        "gpf_isochrone_isodistance_itineraire.processing.get_capabities_parser.getcapabilities_json"
    )
    def test_get_resource_profiles_with_invalid_data(self, mock_download: MagicMock):
        """Check empty profiles return if no data available

        :param mock_download: mock for getcap download
        :type mock_download: MagicMock
        """
        mock_download.return_value = {
            "resources": [
                {
                    "id": "my_resource",
                    "availableOperations": [
                        {
                            "id": "isochrone",
                        }
                    ],
                }
            ]
        }
        profiles = getcap.get_resource_profiles("my_resource", "isochrone")
        self.assertEqual(profiles, [])


if __name__ == "__main__":
    unittest.main()
