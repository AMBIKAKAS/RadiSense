import ee

def compute_bsi(aoi_geojson, start, end):
    geom = ee.Geometry(aoi_geojson)

    col = (
        ee.ImageCollection("COPERNICUS/S2_SR")
        .filterBounds(geom)
        .filterDate(start, end)
    )

    def add_bsi(img):
        b = img.select("B2")
        r = img.select("B4")
        nir = img.select("B8")
        swir = img.select("B11")

        bsi = (r.add(swir).subtract(nir.add(b))) \
            .divide(r.add(swir).add(nir).add(b)) \
            .rename("BSI")

        return img.addBands(bsi)

    col2 = col.map(add_bsi)

    latest = col2.sort("system:time_start", False).first()

    return latest.select("BSI")
