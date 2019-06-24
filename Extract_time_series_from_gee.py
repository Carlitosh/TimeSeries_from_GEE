# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from datetime import datetime as dt
import ee


def extract_time_series(lat, lon, start, end, product_name, band_name, sf):

    # Set up point geometry
    point = ee.Geometry.Point(lon, lat)

    # Obtain image collection for all images within query dates
    coll = ee.ImageCollection(product_name)\
        .filterDate(start, end)

    # Get list of images which correspond with the above
    images = [item.get('id') for item in coll.getInfo().get('features')]

    store = []
    date_store = []
    
    # Loop over all images and extract pixel value
    for image in images:

        im = ee.Image(image)
        projection = im.projection().getInfo()['crs']
        # Obtain date from timestamp in metadata
        date = dt.fromtimestamp(im.get("system:time_start").getInfo() / 1000.)
        date_store.append(np.datetime64(date))

        # Extract pixel value
        data = im.select(band_name)\
        .reduceRegion(ee.Reducer.first(),
                      point,
                      1,
                      crs=projection)\
        .get(band_name)

        store.append(data.getInfo())

    # Scale the returned data based on scale factor
    store = [x * sf if isinstance(x, int) else np.nan for x in store]

    # Convert output into pandas data frame
    df = pd.DataFrame(index=date_store, data=store, columns=[band_name])

    return df


if __name__ == "__main__":

    ee.Initialize()

    latitude = -33.5
    longitude = -64.5
    start_date = '2018-01-01'
    end_date = '2018-01-31'
    product = 'MODIS/006/MOD11A1' 
    band = 'LST_Day_1km'
    scale_factor = 0.02

    # Extract data and obtain pd.DataFrame
    output = extract_time_series(latitude,
                                 longitude,
                                 start_date,
                                 end_date,
                                 product,
                                 band,
                                 scale_factor)
    print(output.head(5))


