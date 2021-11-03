import numpy

def enhance_contrast(numpy_array):
    '''
    :param numpy_array: original image as numpy array
    :param percentile: put in the percentage of pixels in an upper percentile which are used to calculate the max value
    :return: numpy array of the image with enhanced contrast
    '''
    percentile = 99.9
    # Enhance contrast by stretching the histogram over the full range of 8-bit grayvalues
    # minimum_gray = numpy.amin(numpy_array)
    # maximum_gray = numpy.amax(numpy_array)
    # mean_gray = numpy.mean(numpy_array)
    # print("The {} channel has the following greyvalue range: {} - {}, with a mean of: {}.".format(stackname, str(minimum_gray), str(maximum_gray), str(mean_gray)))
    # lower2 = numpy.percentile(numpy_array, 0.2)

    # in order to enhance the lower values a bit more, replace every pixel value by its sqrt:
    numpy_array = numpy.sqrt(numpy_array)

    # As the single brightest pixel is most likely and outlier, I take the upper percentile above x% of the pixels as the brigthest values (where eg 0.02% are still 3200 pixels in an image of 4000x4000 pixels)
    upper2 = numpy.percentile(numpy_array, percentile)
    print("{}% of all the pixels have a value lower than {}".format(str(percentile), str(upper2)))
    # number_highest_value = numpy.count_nonzero(numpy_array == maximum_gray)
    # print("The pixel with the highest value({}) occurs {} times.".format(str(maximum_gray), str(number_highest_value)))

    # as we are in 8-bit space, 255 is the maximum possible value that we want to adjust the histogram to
    thresh = 255
    # by dividing every pixel value by the maximum brightness of the image (defined by the upper percentile) and then multiplying by 255, we stretch the histogram towards 255
    factor = thresh/upper2
    print("The enhancement factor is: {}".format(str(factor)))
    enhanced_contrast = numpy_array * factor

    # Now the whole array has been multiplied in order to be nicely distributed over an 8-bit range (0-255)
    # however, some pixels (the ones which lie above the percentile threshold) will be above the threshold, and these need to be set to 255, otherwise weird artefacts can occur
    enhanced_contrast[enhanced_contrast > 255] = 255  # ich suche mir die Pixel im Array, die über dem Threshold liegen (evaluiert zu True oder False) und setze die Intensitäten an diesen Stellen auf 255
    enhanced_contrast[enhanced_contrast <= factor] = 0  # ich suche mir die Pixel im Array, die unter oder gleich dem Faktor liegen und setze die Intensitäten an diesen Stellen auf 0, weil die waren vorher 1
    return enhanced_contrast, percentile

