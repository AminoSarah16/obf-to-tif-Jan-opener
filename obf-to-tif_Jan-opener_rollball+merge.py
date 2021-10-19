'''

Opens .obf files and saves individual stacks as .tiffs.
Also stretches Histogram to 255 and applies rolling ball to Bax channel.
Then merges the two channels in an RGB file.

The OBF file format originates from the Department of NanoBiophotonics
of the Max Planck Institute for Biophysical Chemistry in Göttingen, Germany. A specification can be found at
https://github.com/AbberiorInstruments/ImspectorDocs/blob/master/docs/fileformat.rst

Opening and converting to numpy array is done via the obf support package by Jan Keller-Findeisen (https://github.com/jkfindeisen)
https://github.com/jkfindeisen/python-mix/tree/main/obf
[Pure Python read only support for OBF files.  This implementation is similar to the File and Stack API of specpy
(https://pypi.org/project/specpy/). Can also read MSR files (the OBF part of it).]

Include Jan's obf_support.py in your project and import it into the code with "import obf_support".

Sarah Schweighofer, May 2021, Göttingen, Max Planck Institute for Biophysical Chemistry
'''


import obf_support
from tkinter import filedialog
import os
import numpy
from PIL import Image
from cv2_rolling_ball import subtract_background_rolling_ball


def main():
    # let the user choose the folder containing the images to be converted
    root_path = filedialog.askdirectory()  # prompts user to choose directory. From tkinter

    # prints out the number of files in the selected folder with the .obf file format
    file_format = ".obf"  ##TODO: make run with .msr  ##TODO: make contrast stretching
    filenames = [filename for filename in sorted(os.listdir(root_path)) if filename.endswith(file_format)]
    print("There are {} files with this format.".format(len(filenames)))
    if not filenames:  # pythonic for if a list is empty
        print("There are no files with this format.")

    # ask user which part in the name we are looking for:
    namepart = input("Please enter the namepart you are looking for - case-sensitive (eg STED, Confocal..). If all stacks are wanted press enter: ")

    # create a subfolder where the converted images would be saved
    result_path = os.path.join(root_path, 'tifs')
    if not os.path.isdir(result_path):
        os.makedirs(result_path)

    # go through the list of files
    for filename in filenames:
        print(filename)
        file_path = os.path.join(root_path, filename)
        current_obf_file = obf_support.File(file_path) #this is where Jan does the magic of opening

        # extract the stacks according to the defined name part
        wanted_stacks = [stack for stack in current_obf_file.stacks if namepart in stack.name]
        print('The measurement contains {} {} channels.'.format(len(wanted_stacks), namepart))

        # alternatively take all stacks from the measurement with the following line:
        # for stack in current_obf_file.stacks:

        # now load all the wanted stacks, turn them into numpy arrays and get the exact name.
        for stack in wanted_stacks:
            array = stack.data  # this is where Jan does the magic of converting obf to numpy
            array = numpy.transpose(array)  # need to transpose to have in the original orientation
            stackname = stack.name

            # save the tiff images unprocessed
            a = array * 1  ## dass ich hier das Array duplizieren muss und mal 1 nehmen, ist vollkommener Bullshit, aber auf dem originalen Array lässt er mich nicht rummanipulieren... :/
            a[a>255] = 255  # um komische Artefakte zu verhindern, falls Nummern über 255 entstehen beim stretchen
            save_array_with_pillow(a, result_path, filename, stackname)

            if "Bax" in stackname:
                # background subtraction by rolling ball algorithm with 3x3 mean filter (=presmooth) and ball as structuring element
                # ATTENTION: This takes forever (like 2 hours for one 60x60µm image), so if you just want to try the code, use the file without the rolling ball thing!!
                img, background = subtract_background_rolling_ball(array.astype(numpy.uint8), 10, light_background=False, use_paraboloid=False, do_presmooth=True)
                save_array_with_pillow(img, result_path, filename, stackname + "img_without_background")
                save_array_with_pillow(background, result_path, filename, stackname + "background")
                # enhance contrast
                Bax_enhanced = enhance_contrast(img, stackname)
                # save the contrast enhanced images
                save_array_with_pillow(Bax_enhanced, result_path, filename, stackname + "contr-enh")
            if "Tom" in stackname:
                # enhance contrast
                Tom_enhanced = enhance_contrast(array, stackname)
                # save the contrast enhanced images
                save_array_with_pillow(Tom_enhanced, result_path, filename, stackname + "contr-enh")

        #turn them to RGB; Bax in green (0, 255, 0) and Tom in magenta (255, 0, 255).
        #However, opencv uses the format BGR!> B and R need to be set by Tom, and G by Bax
        x = stack.shape[1]
        y = stack.shape[0]
        merged = numpy.zeros((x, y, 3)) #creates a blank canvas with 3 dimensions for every pixel
        merged[:, :, 0] = Tom_enhanced
        merged[:, :, 1] = Bax_enhanced
        merged[:, :, 2] = Tom_enhanced

        # merged = numpy.transpose(merged)  # need to transpose to have in the original orientation
        save_array_with_pillow(merged, result_path, filename, stackname[0:0] + "merged")



def save_array_with_pillow(array, result_path, filename, stackname):  ##TODO: add pixel size in metadata, so that when you open it in imageJ, it knows it automatically
    # The type of the numpy array needs to be unsigned integer, otherwise can't be saved as tiff.
    # unit8 = Unsigned integer (0 to 255); unit32 = Unsigned integer (0 to 4294967295)
    eight_bit_array = array.astype(numpy.uint8)
    output_file = os.path.join(result_path, filename[:-4] + "_" + stackname + '.tiff')
    # print("wanted stack : {}".format(stackname)
    img = Image.fromarray(eight_bit_array)
    # print("I will save now")
    img.save(output_file, format='tiff')


def enhance_contrast(numpy_array, stackname): ##TODO: is 255 really the right scale here?
    # Enhance contrast by stretching the histogram over the full range of 8-bit grayvalues
    # takes the upper 0.2 % of pixels as the highest value, cause sometimes there are super bright single pixels
    # minimum_gray = numpy.amin(numpy_array)
    # maximum_gray = numpy.amax(numpy_array)
    # mean_gray = numpy.mean(numpy_array)
    # print("The {} channel has the following greyvalue range: {} - {}, with a mean of: {}.".format(stackname, str(minimum_gray), str(maximum_gray), str(mean_gray)))
    # lower2 = numpy.percentile(numpy_array, 0.2)
    upper2 = numpy.percentile(numpy_array, 99.8)
    print("0.2% of all the pixels have a value higher than {}".format(str(upper2)))
    # number_highest_value = numpy.count_nonzero(numpy_array == maximum_gray)
    # print("The pixel with the highest value({}) occurs {} times.".format(str(maximum_gray), str(number_highest_value)))
    thresh = 255
    factor = thresh/upper2
    print(factor)
    enhanced_contrast = numpy_array * factor

    # Now the whole array has been multiplied in order to be nicely distributed over an 8-bit range (0-255)
    # however, some pixels will be above the threshold, and these need to be set to 255, otherwise weird artefacts can occur
    enhanced_contrast[enhanced_contrast > 255] = 255  # ich suche mir die Pixel im Array, die über dem Threshold liegen und setze die Intensitäten an diesen Stellen auf 255
    return enhanced_contrast


if __name__ == '__main__':
    main()