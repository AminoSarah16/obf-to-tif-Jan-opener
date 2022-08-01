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
Also include utils.py file!!

Sarah Schweighofer, May 2021, Göttingen, Max Planck Institute for Biophysical Chemistry
'''


from utils import *  # need the utils.py file which has auxiliary funcs
import obf_support
from tkinter import filedialog
import os
import numpy
from PIL import Image
import glob2


def main():
    file_format = ".obf"

    # ask user which what part in the name we are looking for:
    namepart = input("Please enter the namepart you are looking for - case-sensitive (eg STED, Confocal..). If all stacks are wanted press enter: ")
    # namepart = ""

    # let the user choose the folder containing the images to be converted
    root_path = glob2.glob(filedialog.askdirectory())  # prompts user to choose directory. From tkinter
    #glob is needed for the wildcards to work later when walking childpaths
    print(root_path)

    path_list = []
    for p in root_path:
        child_paths = glob2.glob(os.path.join(p, 'IF*/renamed'))
        for child_path in child_paths:
            path_list.append(child_path)
        print(path_list)
    for path in path_list:
        filenames = [filename for filename in sorted(os.listdir(path)) if filename.endswith(file_format)]
        # also create a subfolder where the converted images would be saved
        result_path = os.path.join(path, 'tifs')
        if not os.path.isdir(result_path):
            os.makedirs(result_path)
        print(filenames)

        #now that we have all files, go through the list of files
        for filename in filenames:
            print(filename)
            file_path = os.path.join(path, filename)
            print(file_path)


            current_obf_file = obf_support.File(file_path) #this is where Jan does the magic of opening

            #extract the stacks according to the defined name part
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

                # #save the contrast enhanced images with percentile and sqr root enhancement (see utils) - ACTIVATE IF WANTED!!
                enhanced_contrast, percentile = enhance_contrast(array)
                save_array_with_pillow(enhanced_contrast, result_path, filename, stackname + "-enh" + str(percentile))

                #save contrast enhanced images with fixed value enhancement (eg. for cytC normalized to untreated cells etc) - ACTIVATE IF WANTED!!
                factor = 2 #change the wanted factor here!
                enhanced_contrast = enhance_contrast_fixed(array, factor)
                save_array_with_pillow(enhanced_contrast, result_path, filename, stackname + "-enh" + str(factor) + "x")

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