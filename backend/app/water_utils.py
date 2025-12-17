import ee

def compute_water_turbidity(aoi_geojson, start, end):
    geom = ee.Geometry(aoi_geojson)

    col = (
        ee.ImageCollection("COPERNICUS/S2_SR")
        .filterBounds(geom)
        .filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40))
    )

    def add_indices(img):
        ndwi = img.normalizedDifference(["B3", "B8"]).rename("NDWI")
        ndti = img.normalizedDifference(["B11", "B12"]).rename("NDTI")
        return img.addBands(ndwi).addBands(ndti)

    col2 = col.map(add_indices)

    latest = col2.sort("system:time_start", False).first()

    return {
        "NDWI": latest.select("NDWI"),
        "NDTI": latest.select("NDTI")
    }
