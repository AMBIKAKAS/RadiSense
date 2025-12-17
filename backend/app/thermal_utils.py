import ee

def compute_landsat_thermal_anomaly(aoi_geojson, start, end):
    geom = ee.Geometry(aoi_geojson)

    collection = (
        ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
        .filterBounds(geom)
        .filterDate(start, end)
        .map(lambda img: img.updateMask(img.select("QA_PIXEL").bitwiseAnd(1<<3).eq(0)))
    )

    def add_temp(img):
        radiance = img.select("ST_B10")
        temp = radiance.multiply(0.00341802).add(149.0)  # L8 temp conversion
        return img.addBands(temp.rename("temp"))

    col_temp = collection.map(add_temp).select("temp")

    mean = col_temp.mean()
    std = col_temp.reduce(ee.Reducer.stdDev())
    latest = col_temp.sort("system:time_start", False).first()

    z = latest.subtract(mean).divide(std.add(1e-6)).rename("thermal_z")
    anomaly = z.gt(2).selfMask().rename("thermal_anomaly")

    return {
        "thermal_z": z,
        "thermal_mask": anomaly
    }
