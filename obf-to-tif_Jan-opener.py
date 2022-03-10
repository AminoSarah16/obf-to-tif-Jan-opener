'''

Opens .obf files and saves individual stacks as .tiffs.

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


from utils import *  # need the utils.py file which has auxiliary funcs
import obf_support
from tkinter import filedialog
import os
import numpy
from PIL import Image


def main():
    # let the user choose the folder containing the images to be converted
    root_path = filedialog.askdirectory()  # prompts user to choose directory. From tkinter

    file_format = ".obf"
    file_list = []
    # spaziert durch alle Subdirectories und sucht sich alle Files und packt sie in ne neue Liste, die ich oben neu kreiert habe
    for root, dirs, files in os.walk(root_path):
        for name in files:
            file_list.append(os.path.join(root, name))
    filenames = [filename for filename in file_list if filename.endswith(file_format)]
    print("There are {} files with this format.".format(len(filenames)))
    if not filenames:  # pythonic for if a list is empty
        print("There are no files with this format.")  ##TODO:does not save into "tif" directory > why? the prolem lies in the save function, because outpute file tries to join two different filepaths, so Python overrules the "result-path" one

    # ask user which what part in the name we are looking for:
    # namepart = input("Please enter the namepart you are looking for - case-sensitive (eg STED, Confocal..). If all stacks are wanted press enter: ")
    namepart =""
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
            array = numpy.transpose(array)  # need to transpose to have in the original orientation
            stackname = stack.name


            # save the tiff images unprocessed
            a = array * 1  ## dass ich hier das Array duplizieren muss und mal 1 nehmen, ist vollkommener Bullshit, aber auf dem originalen Array lässt er mich nicht rummanipulieren... :/
            a[a > 255] = 255
            save_array_with_pillow(a, result_path, filename, stackname)

            #save the contrast enhanced images - ACTIVATE IF WANTED!!
            enhanced_contrast, percentile = enhance_contrast(array)
            save_array_with_pillow(enhanced_contrast, result_path, filename, stackname + "-enh" + str(percentile))
            #
            #save an image which was just contrast enhanced by multiplying with 2
            if "Bax" in stackname:
                contrast_x = array * 2.5
                save_array_with_pillow(contrast_x, result_path, filename, stackname + "contrx2,5")


def save_array_with_pillow(array, result_path, filename, stackname):  ##TODO: add pixel size in metadata, so that when you open it in imageJ, it knows it automatically
    # The type of the numpy array needs to be unsigned integer, otherwise can't be saved as tiff.
    # unit8 = Unsigned integer (0 to 255); unit32 = Unsigned integer (0 to 4294967295)
    eight_bit_array = array.astype(numpy.uint8)
    output_file = os.path.join(result_path, filename[:-4] + "_" + stackname + '.tiff')
    # print("wanted stack : {}".format(stackname)
    img = Image.fromarray(eight_bit_array)
    # print("I will save now")
    img.save(output_file, format='tiff')


if __name__ == '__main__':
    main()