'''

Opens tiffs, enhances them by stretching the histogram to 255 and then merges channels to multi-color images.

Sarah Schweighofer, May 2021, Göttingen, Max Planck Institute for Biophysical Chemistry
'''


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

    # prints out the number of files in the selected folder with the .obf file format
    file_format = ".tiff"
    filenames = [filename for filename in sorted(os.listdir(root_path)) if filename.endswith(file_format)]
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
            im1_enhanced = enhance_contrast(im_array1)

            # save the contrast enhanced images
            save_array_with_pillow(im1_enhanced, result_path, filename[:-4] + "_contr-enh.tiff")


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


def enhance_contrast(numpy_array):
    # Enhance contrast by stretching the histogram over the full range of 8-bit grayvalues
    # takes the upper 0.2 % of pixels as the highest value, cause sometimes there are super bright single pixels
    upper2 = numpy.percentile(numpy_array, 99.8)
    print("0.2% of all the pixels have a value higher than {}".format(str(upper2)))
    thresh = 255
    factor = thresh/upper2
    print("The enhancement factor is: {}".format(str(factor)))
    enhanced_contrast = numpy_array * factor

    # Now the whole array has been multiplied in order to be nicely distributed over an 8-bit range (0-255)
    # however, some pixels will be above the threshold, and these need to be set to 255, otherwise weird artefacts can occur
    enhanced_contrast[enhanced_contrast > 255] = 255  # ich suche mir die Pixel im Array, die über dem Threshold liegen und setze die Intensitäten an diesen Stellen auf 255
    enhanced_contrast[enhanced_contrast <= factor] = 0 # ich suche mir die Pixel im Array, die unter oder gleich dem Faktor liegen und setze die Intensitäten an diesen Stellen auf 0, weil die waren vorher 1
    return enhanced_contrast


if __name__ == '__main__':
    main()