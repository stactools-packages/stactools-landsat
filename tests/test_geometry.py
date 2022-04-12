import unittest

import vcr
from stactools.core.utils.antimeridian import Strategy

from stactools.landsat.stac import create_stac_item
from tests.data import TEST_GEOMETRY_PATHS


class GeometryTest(unittest.TestCase):

    def test_stored_stac(self):
        """Test USGS STAC geometry is returned when use_usgs_stac=True and STAC
        exists in storage. Expected geometry copied from the SR STAC file in
        the tests/data-files/assets2 directory.
        """
        mtl_xml_href = TEST_GEOMETRY_PATHS["stac_in_storage"]
        expected_geometry = {
            "type":
            "Polygon",
            "coordinates": [[[70.70487567768816, -80.24577066106241],
                             [75.274690570951, -81.80839588279174],
                             [63.466214893229875, -82.43020599776871],
                             [60.660355360178656, -80.76338417289233],
                             [70.70487567768816, -80.24577066106241]]]
        }
        expected_coords = expected_geometry["coordinates"][0]
        item = create_stac_item(mtl_xml_href, use_usgs_geometry=True)
        item_coords = item.geometry["coordinates"][0]
        for e, i in zip(expected_coords, item_coords):
            self.assertAlmostEqual(e[0], i[0], 7)
            self.assertAlmostEqual(e[1], i[1], 7)

    @vcr.use_cassette(TEST_GEOMETRY_PATHS["vcr_cassette"])
    def test_api_stac(self):
        """Test USGS STAC geometry is returned when use_usgs_stac=True and STAC
        does not exist in storage but does exist on the USGS server. Expected
        geometry copied from STAC generated by the USGS STAC API.
        """
        mtl_xml_href = TEST_GEOMETRY_PATHS["stac_not_in_storage"]
        expected_geometry = {
            "type":
            "Polygon",
            "coordinates": [[[-124.27364628436257, 48.508467268961375],
                             [-124.89607929858929, 46.80220745164398],
                             [-122.53800038880695, 46.37691124870954],
                             [-121.83985903460558, 48.078084372791],
                             [-124.27364628436257, 48.508467268961375]]]
        }
        expected_coords = expected_geometry["coordinates"][0]
        item = create_stac_item(mtl_xml_href, use_usgs_geometry=True)
        item_coords = item.geometry["coordinates"][0]
        for e, i in zip(expected_coords, item_coords):
            self.assertAlmostEqual(e[0], i[0], 7)
            self.assertAlmostEqual(e[1], i[1], 7)

    def test_ang(self):
        """Test geometry is generated from the "ANG.txt" file data when
        use_usgs_stac=False. Expected geometry copied from Planetary Computer
        STAC API, which uses Items with geometries generated with the
        "ANG.txt" file.
        """
        mtl_xml_href = TEST_GEOMETRY_PATHS["stac_in_storage"]
        expected_geometry = {
            "type":
            "Polygon",
            "coordinates": [[[77.41721421, -81.41837295],
                             [65.95800182, -82.94593976],
                             [56.05168383, -81.25621974],
                             [67.44881125, -79.72178205],
                             [77.41721421, -81.41837295]]]
        }
        expected_coords = expected_geometry["coordinates"][0]
        item = create_stac_item(mtl_xml_href, use_usgs_geometry=False)
        item_coords = item.geometry["coordinates"][0]
        for e, i in zip(expected_coords, item_coords):
            self.assertAlmostEqual(e[0], i[0], 7)
            self.assertAlmostEqual(e[1], i[1], 7)

    def test_antimeridian(self):
        """Test that a scene spanning the antimeridian is normalized."""
        mtl_xml_href = TEST_GEOMETRY_PATHS["antimeridian"]
        crosssing_geometry = {
            "type":
            "Polygon",
            "coordinates": [[[-179.70358951407547, 52.750507455036264],
                             [179.96672360880183, 52.00163609753924],
                             [-177.89334479610974, 50.62805205289558],
                             [-179.9847165338706, 51.002602948712465],
                             [-179.70358951407547, 52.750507455036264]]]
        }
        crossing_coords = crosssing_geometry["coordinates"][0]
        crossing_lons = [lon for lon, lat in crossing_coords]
        item = create_stac_item(mtl_xml_href,
                                legacy_l8=False,
                                use_usgs_geometry=True,
                                antimeridian_strategy=Strategy.NORMALIZE)
        item_coords = item.geometry["coordinates"][0]
        item_lons = [lon for lon, lat in item_coords]
        self.assertFalse(
            all(lon >= 0 for lon in crossing_lons)
            or all(lon <= 0 for lon in crossing_lons))
        self.assertTrue(
            all(lon >= 0 for lon in item_lons)
            or all(lon <= 0 for lon in item_lons))

    def test_presplit_antimeridian_normalize(self):
        """Test that an item with geometry already split along the antimeridian
        does not trigger the stactools antimeridian MultiPolygon value error.
        Use the NORMALIZE strategy.
        """
        mtl_xml_href = TEST_GEOMETRY_PATHS["presplit_antimeridian"]
        item = create_stac_item(mtl_xml_href,
                                use_usgs_geometry=True,
                                legacy_l8=False,
                                antimeridian_strategy=Strategy.NORMALIZE)
        self.assertEqual(item.geometry["type"], "Polygon")

    def test_presplit_antimeridian_split(self):
        """Test that an item with geometry already split along the antimeridian
        does not trigger the stactools antimeridian MultiPolygon value error.
        Use the SPLIT strategy.
        """
        mtl_xml_href = TEST_GEOMETRY_PATHS["presplit_antimeridian"]
        item = create_stac_item(mtl_xml_href,
                                use_usgs_geometry=True,
                                legacy_l8=False,
                                antimeridian_strategy=Strategy.SPLIT)
        self.assertEqual(item.geometry["type"], "MultiPolygon")
