'''

Opens tiffs, enhances them by stretching the histogram to 255 and then runs a Gaussian blur.

Sarah V. Schweighofer, May 2021, Göttingen, Max Planck Institute for Biophysical Chemistry
'''

from utils import *  # need the utils.py file which has auxiliary funcs
import tkinter as tk
from tkinter import simpledialog
from tkinter import filedialog
import os
import numpy
from PIL import Image
import scipy.ndimage as ndimage


def main():
    # let the user choose the folder containing the images to be converted
    root_path = filedialog.askdirectory()  # prompts user to choose directory. From tkinter

    # prints out the number of files in the selected folder with the .tiff file format
    file_format = ".tiff"
    file_list = []
    # spaziert durch alle Subdirectories und sucht sich alle Files und packt sie in ne neue Liste, die ich oben neu kreiert habe
    for root, dirs, files in os.walk(root_path):
        for name in files:
            file_list.append(os.path.join(root, name))
    filenames = [filename for filename in file_list if filename.endswith(file_format)]
    print("There are {} files with this format.".format(len(filenames)))
    if not filenames:  # pythonic for if a list is empty
        print("There are no files with this format.")

    # ask user which what part in the name we are looking for with Tkinter:
    ROOT = tk.Tk() # no idea what this does but is needed for the prompt to work
    ROOT.withdraw() # no idea what this does but is needed for the prompt to work
    channel1 = simpledialog.askstring(title="channel1", prompt="Please enter the namepart you are looking for - best: copy-paste (eg STED, Confocal..):")

    # ask user which what part in the name we are looking for:
    # merge1, merge2 = input("Please enter the 2 nameparts you are looking for - case-sensitive (eg STED, Confocal..). ").split()

    # create a subfolder where the converted images would be saved
    result_path = root_path

    # go through the list of files
    for filename in filenames:
        if channel1 in filename:
            im_array1 = open_tiff_image_to_np_array(root_path, filename)
            im1_enhanced, percentile = enhance_contrast(im_array1)

            # save the contrast enhanced images
            save_array_with_pillow(im1_enhanced, result_path, filename[:-4] + "_enh" + str(percentile) + ".tiff")

            # Gaussian blur
            im1_enhanced = im1_enhanced.astype(numpy.uint8)
            denoised_image = ndimage.gaussian_filter(im1_enhanced, sigma=2)
            # save the contrast enhanced and Guassian blurred images
            save_array_with_pillow(denoised_image, result_path, filename[:-4] + "_enh" + str(percentile) + "_Gauss2.tiff")


def open_tiff_image_to_np_array(root_path, filename):
    # opens image via Pillow
    print(filename)
    file_path = os.path.join(root_path, filename)
    im = Image.open(file_path)
    # im.show()
    im_array = numpy.array(im)
    return im_array


def save_array_with_pillow(array, result_path, filename):
    # The type of the numpy array needs to be unsigned integer, otherwise can't be saved as tiff.
    # unit8 = Unsigned integer (0 to 255); unit32 = Unsigned integer (0 to 4294967295)
    eight_bit_array = array.astype(numpy.uint8)
    output_file = os.path.join(result_path, filename)
    img = Image.fromarray(eight_bit_array)
    img.save(output_file, format='tiff')



if __name__ == '__main__':
    main()