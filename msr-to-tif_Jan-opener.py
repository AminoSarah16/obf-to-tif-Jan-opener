'''

Opens .msr files and saves individual stacks as .tiffs.

The OBF file format originates from the Department of NanoBiophotonics
of the Max Planck Institute for Biophysical Chemistry in Göttingen, Germany. A specification can be found at
https://github.com/AbberiorInstruments/ImspectorDocs/blob/master/docs/fileformat.rst

Opening and converting to numpy array is done via the obf support package by Jan Keller-Findeisen (https://github.com/jkfindeisen)
https://github.com/jkfindeisen/python-mix/tree/main/obf
[Pure Python read only support for OBF files.  This implementation is similar to the File and Stack API of specpy
(https://pypi.org/project/specpy/). Can also read MSR files (the OBF part of it).]

Include Jan's obf_support.py in your project and import it into the code with "import obf_support".

Sarah Schweighofer, Sept 2021, Göttingen, Max Planck Institute for Biophysical Chemistry
'''


import obf_support
from tkinter import filedialog
import os
import numpy
from PIL import Image


def main():
    # let the user choose the folder containing the images to be converted
    root_path = filedialog.askdirectory()  # prompts user to choose directory. From tkinter

    # prints out the number of files in the selected folder with the .obf file format
    file_format = ".msr"
    filenames = [filename for filename in sorted(os.listdir(root_path)) if filename.endswith(file_format)]
    print("There are {} files with this format.".format(len(filenames)))
    if not filenames:  # pythonic for if a list is empty
        print("There are no files with this format.")

    # ask user which what part in the name we are looking for:
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

        #extract the stacks according o the defined name part
        wanted_stacks = [stack for stack in current_obf_file.stacks if namepart in stack.name]
        print('The measurement contains {} {} channels.'.format(len(wanted_stacks), namepart))

        # alternatively take all stacks from the measurement with the following line:
        # for stack in current_obf_file.stacks:

        # now load all the wanted stacks, turn them into numpy arrays and get the exact name.
        for stack in wanted_stacks:
            array = stack.data  # this is where Jan does the magic of converting obf to numpy

            # Dimensionnen von Imspector aus sind [T, Z, Y, X]
            size = array.shape  # The shape attribute for numpy arrays returns the dimensions of the array. If Y has n rows and m columns, then Y.shape is (n,m). So Y.shape[0] is n
            print('The numpy array of the channel has the following dimensions: {}'.format(size))

            # wir wollen aber [X, Y, Z]
            # 1) reduce to [Z, Y, X]
            array = numpy.reshape(array, size[:2])  # TODO: make sure it also works for videos or stacks

            # 3) just to visualize the dimensions again
            size = array.shape
            print('After transposing, the numpy array of the channel has the following dimensions: {}'.format(size))

            array = numpy.transpose(array)  # need to transpose to have in the original orientation
            stackname = stack.name
            enhanced_contrast = enhance_contrast(array, stackname)

            # save the tiff images unprocessed
            a = array * 1  ## dass ich hier das Array duplizieren muss und mal 1 nehmen, ist vollkommener Bullshit, aber auf dem originalen Array lässt er mich nicht rummanipulieren... :/
            a[a > 255] = 255
            save_array_with_pillow(a, result_path, filename, stackname)

            #save the contrast enhanced images
            save_array_with_pillow(enhanced_contrast, result_path, filename, stackname + "contr-enh")
            #
            # #save an image which was just contrast enhanced by multiplying with 2
            # if "Bax" in stackname:
            #     contrast_x = array * 2.5
            #     save_array_with_pillow(contrast_x, result_path, filename, stackname + "contrx2,5")


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
    print("The enhancement factor is: {}".format(str(factor)))
    enhanced_contrast = numpy_array * factor

    # Now the whole array has been multiplied in order to be nicely distributed over an 8-bit range (0-255)
    # however, some pixels will be above the threshold, and these need to be set to 255, otherwise weird artefacts can occur
    enhanced_contrast[enhanced_contrast > 255] = 255  # ich suche mir die Pixel im Array, die über dem Threshold liegen und setze die Intensitäten an diesen Stellen auf 255
    return enhanced_contrast


if __name__ == '__main__':
    main()