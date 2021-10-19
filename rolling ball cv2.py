import cv2
from cv2_rolling_ball import subtract_background_rolling_ball

img = cv2.imread(f'path/to/img.tif', 0)
img, background = subtract_background_rolling_ball(img, 30, light_background=True, use_paraboloid=False, do_presmooth=True)
