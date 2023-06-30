""" 
Functions for working with Landsat8 surface reflectance data from google earth engine
"""
import ee

def prep_landsat8_collection(collection, roi):
    collection = collection.map(prep_landsat8)
    collection = collection.map(lambda image: clip_to_roi(image, roi))
    return collection

def prep_landsat8(image):
    image = mask_clouds(image)
    image = scale_factor(image)
    return image


def bitwise_extract(input, start=3, end=4):
        mask_size = ee.Number(1).add(end).subtract(start)
        mask = ee.Number(1).leftShift(mask_size).subtract(1)
        return input.rightShift(start).bitwiseAnd(mask)

def mask_clouds(image):
    # https://spatialthoughts.com/2021/08/19/qa-bands-bitmasks-gee/
    # https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2#bands

    qa = image.select('QA_PIXEL')
    # clouds are Bit 3, cloud shadow is Bit 4
    cloud_mask = bitwise_extract(qa).eq(0)
    image = image.updateMask(cloud_mask)
    return image

def scale_factor(image):
    optical = image.select('SR_B.').multiply(0.0000275).add(-0.2)
    thermal = image.select('ST_B.*').multiply(0.00341802).add(149.0)
    image = image.addBands(optical, None, True)
    image = image.addBands(thermal, None, True)
    return image

def clip_to_roi(image, roi):
    return image.clip(roi)