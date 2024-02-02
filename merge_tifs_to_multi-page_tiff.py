'''
Opens .tif files and saves merges as multi-page-tiff.

Sarah Schweighofer, Feb 2024, Göttingen, Max Planck Institute for Multidisciplinary Sciences
'''

from utils import *

def main():
    # let the user choose the folder containing the images to be converted
    root_path = filedialog.askdirectory()  # prompts user to choose directory. From tkinter
    print(root_path)

    # prints out the number of files in the selected folder with the .obf file format
    file_format = ".tiff"
    filenames = [filename for filename in sorted(os.listdir(root_path)) if filename.endswith(file_format)]
    print("There are {} files with this format.".format(len(filenames)))
    if not filenames:  # pythonic for if a list is empty
        print("There are no files with this format.")

    # ask user which what part in the name we are looking for:
    namepart1 = "Alexa 594_STED {0}"
    namepart2 = "STAR RED_STED {0}"
    # namepart1 = input("Please enter the namepart of the first channel you are looking for - case-sensitive (eg STED, Confocal..): ")
    # namepart2 = input("Please enter the namepart of the second channel you are looking for - case-sensitive (eg STED, Confocal..): ")

    # create a subfolder where the converted images would be saved
    result_path = os.path.join(root_path, 'merged')
    if not os.path.isdir(result_path):
        os.makedirs(result_path)

    # find only the tiffs according to the defined name part
    wanted_files = [filename for filename in filenames if namepart1 in filename]
    print('The folder contains {} {} channels.'.format(len(wanted_files), namepart1))


    #open_tifs()
    # get the filepaths
    for filename in wanted_files:
        print(filename)
        file_path1 = os.path.join(root_path, filename)

        # read the image
        img1 = io.imread(file_path1) #this is already a numpy array then
        # # show the image
        # plt.imshow(img1, cmap='gray')
        # plt.show()

        # read the second image
        file_path2 = file_path1.replace(namepart1, namepart2)
        img2 = io.imread((file_path2))
        # #show the image
        #plt.imshow(img2, cmap='gray')
        #plt.show()


        # Get the dimensions (x, y) of the image
        x_dim1, y_dim1 = img1.shape
        x_dim2, y_dim2 = img2.shape
        if x_dim1 != x_dim2 or y_dim1 != y_dim2:
            raise ValueError("The dimensions of the two images are not equal.")
        else:
            print("The x and y dimensions of both opened images are the same.")

        # Metadata - Example: pixel size in micrometers
        #pixelsize = input("Please enter the pixelsize in microns: ")
        pixelsize = 0.020
        metadata = {'microns_per_pixel': pixelsize}

        # Concatenate along the channel axis to create a 3D array
        merged = numpy.stack([img1, img2], axis=0)

        # # # Expand dimensions to add a virtual Z-axis (z=1)
        # # merged = numpy.expand_dims(merged, axis=1)
        #
        # # Expand dimensions to add a virtual Z-axis (z=1)
        # merged = numpy.expand_dims(merged, axis=0)
        #
        # # # Expand dimensions to add a virtual T-axis (z=1)
        # # merged = numpy.expand_dims(merged, axis=0)
        #
        # # # Rearrange the dimensions to (c, z, y, x) order ZCYX
        # # merged = numpy.transpose(merged, (1, 0, 2, 3))


        #save_merged()
        savename = filename.replace(namepart1, "multi-merged_")
        # merged = numpy.transpose(merged)  # need to transpose to have in the original orientation

        output_file = os.path.join(result_path, savename)

        tifffile.imwrite(output_file, merged, imagej=True, metadata={'axes': 'CYX', 'mode':'composite', 'resolution': pixelsize, 'unit': 'micrometers'}, resolution=(1/pixelsize, 1/pixelsize))

        #io.imsave(output_file, merged, plugin='tifffile', metadata=metadata)

     ##TODO: generate log-files


if __name__ == '__main__':
    main()