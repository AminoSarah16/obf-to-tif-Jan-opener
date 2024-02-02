'''
Opens .tif files and saves merges as RGB.

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
    namepart1 = input("Please enter the namepart of the first channel you are looking for - case-sensitive (eg STED, Confocal..): ")
    namepart2 = input("Please enter the namepart of the second channel you are looking for - case-sensitive (eg STED, Confocal..): ")

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


        #merge_channels()
        # turn them to RGB; img1 in green (0, 255, 0) and img2 in magenta (255, 0, 255).
        # However, opencv uses the format BGR!> B and R need to be set by img2, and G by img1
        x = img1.shape[1]
        y = img1.shape[0]

        # create a blank canvas with x number of pixels times y number of pixels with 3 values (BGR) for every pixel
        merged = numpy.zeros((y, x, 3)) #for whatever reason, y needs to come before x
        #TODO: make a two-channel tiff instead of the merge into RGB

        merged[:, :, 0] = img2  # sets all the pixels for B with the values from the img2 channel
        merged[:, :, 1] = img1  # sets all the pixels for G with the values from the img1 channel
        merged[:, :, 2] = img2  # sets all the pixels for R with the values from the img2 channel

        #save_merged()
        savename = filename.replace(namepart1, "merged_")
        # merged = numpy.transpose(merged)  # need to transpose to have in the original orientation

        eight_bit_array = merged.astype(numpy.uint8)
        output_file = os.path.join(result_path, savename)
        # print("wanted stack : {}".format(stackname)
        img = Image.fromarray(eight_bit_array)
        # print("I will save now")
        img.save(output_file, format='tiff')

     ##TODO: generate log-files




if __name__ == '__main__':
    main()