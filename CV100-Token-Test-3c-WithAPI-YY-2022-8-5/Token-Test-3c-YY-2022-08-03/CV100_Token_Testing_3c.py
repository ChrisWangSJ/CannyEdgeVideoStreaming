'''-------------------------------------------------------------------------------------------------------
* Company Name : CTI One Corporation                                                                     *
* Program name : CV100_Token_Testing_3c.py (Testing)                                                     *
* Coded By     : YY                                                                                      *
* Date         : 2022-07-27                                                                              *
* Updated By   :                                                                                         *
* Date         :                                                                                         *
* Version      : v1.0.0                                                                                  *
* Copyright    : Copyright (c) 2022 CTI One Corporation                                                  *
* Purpose      : Perform Handwriting                                                                     *
*              :                                                                                         *
*              : v1.0.0 2022-07-27 YY Create from main-smudge2-video-niblack-color-split-std-2022-07-22.py *
-------------------------------------------------------------------------------------------------------'''
# --------------------------------------------------------#
# Coded by: HL, BJ;   Date: July 22, 2022;                     #
# Version: x01.0; Status: Debug                          #
# Note: this code is Phase II implementation for Token    #
#       Test 2 to be integrated with Token Test 1 by     #
#       replacing Canny.                                 #
# Copyright: CTI One Corporation                         #
# Note: Last clean up on July 20th, 2022 to remove print  #
# Last update: July 21, 2022 for video processing result  #
#       recording.                                       #
# File name: CTI_CV100_Text_Extraction.py                 #
# -------------------------------------------------------#

import numpy as np
import cv2
import time
import os
import sys
import socket
import traceback

# Github: https://github.com/KadenMc/PreprocessingHTR/blob/main/mainProcessing.py
# import connectedComponentsProcessing

class textExtraction:

    def __init__(self, color_plane_selection, debug_mode_selection):
        # User inputs
        self.color_plane_selection = color_plane_selection
        self.debug_mode_selection = debug_mode_selection

        # Parameters
        self.scale_percent = 50  # percent of original size

        # Dilation kernel size
        self.dilation_kernel_size = np.ones((3, 3), np.uint8)
        self.dilation_iteration_number = 1

        # Reduce Noise
        self.ddepth = cv2.CV_16S
        self.kernel_size = 3

        # Niblack Binerization
        self.window_size = 7
        self.ni_k = 0.1

        # Contour Parameters 45 ~ 600
        self.area_lowerBound = 210 * (self.scale_percent / 100)
        self.area_upperBound = 5000 * (self.scale_percent / 100)

        self.aspect_threshold_lower = 0.05  # w / h
        self.aspect_threshold_upper = 3.0

        self.extent_ratio_lower = 0.0  # object area / bounding rectangle area
        self.extent_ratio_upper = 1.0

        self.solid_ratio_lower = 0.0  # contour area / convex hull area
        self.solid_ratio_upper = 1.0  #

        # Picked Color Range in HSV
        self.light_blue = (30, 15, 100)  # (H, S, V)
        self.dark_blue = (60, 150, 255)

        self.color_mean_std_alpha_hi = 1.5
        self.color_mean_std_alpha_low = 0.95

    def print_hi(self, name):
        print(f'Text Extraction, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

    def reduceNoise(self, img, ddepth, kernelSize):
        Gau_Blur_img = cv2.GaussianBlur(img, (3, 3), 0)
        Gau_Blur_img_gray = cv2.cvtColor(Gau_Blur_img, cv2.COLOR_BGR2GRAY)
        result = cv2.Laplacian(Gau_Blur_img_gray, ddepth, ksize=kernelSize)
        abs_result = cv2.convertScaleAbs(result)
        return abs_result

    def dilation_erosion(self, img):
        # Dilation and erosion
        # erosion = cv2.erode(img, self.dilation_kernel_size, iterations=self.dilation_iteration_number)
        # cv2.imshow('CTI erosion', erosion)

        dilation = cv2.dilate(img, self.dilation_kernel_size, iterations=self.dilation_iteration_number)
        if self.debug_mode_selection == "debug":
            cv2.imshow('Dilation Result', dilation)
        return dilation

    def niblack_binarization(self, image_gray, window_size, ni_k):
        # Niblack operation thresh hold
        binary_image_nib = cv2.ximgproc.niBlackThreshold(image_gray, 255, cv2.THRESH_BINARY, \
                                                         window_size, ni_k)
        if self.debug_mode_selection == "debug":
            cv2.imshow("niblack_binarization", binary_image_nib)
        return binary_image_nib

    def contour_analysis(self, img_binary, original_img):
        '''
        :param wN: Window name for imshow
        :param img_binary: Image tensor after binerization
        :param original_img: Image tensor from the original output
        :return:
        '''
        height = img_binary.shape[0]
        width = img_binary.shape[1]
        # Create mask
        bb_no_filter = np.zeros((height, width, 3), dtype="uint8")
        bb_filter = np.zeros((height, width, 3), dtype="uint8")
        contour_filtered_mask = np.zeros(img_binary.shape, dtype="uint8")
        # Find Contours
        contour_mode = [cv2.RETR_EXTERNAL,  # retrieves only the extreme outer contours
                        cv2.RETR_CCOMP,  # retrieves all of the contours and organizes them into a two-level hierarchy.
                        cv2.RETR_TREE
                        # retrieves all of the contours and reconstructs a full hierarchy of nested contours.
                        ]
        contours1, hierarchy = cv2.findContours(img_binary, contour_mode[0],
                                                cv2.CHAIN_APPROX_SIMPLE)  # cv2.CCOMP for 2 levels
        # print(contours1[0].shape)
        for contour in contours1:  # filtering based the contour features
            # Straight Box
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(bb_no_filter, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Draw the rectangle

            # Rotated Box
            # rect = cv2.minAreaRect(contour)
            # box = cv2.boxPoints(rect)
            # box = np.int0(box)
            # cv2.drawContours(bb_no_filter,[box],0,(0,255,0),2)
            # x = rect[0][0]
            # y = rect[0][1]
            # w = rect[1][0]
            # h = rect[1][1]

            # Aspect Ratio
            aspect_ratio_contour = float(w) / h if int(h) != 0 else 0
            # Area size
            area = cv2.contourArea(contour)
            # Extent
            rect_area = w * h
            extent = float(area) / rect_area if int(rect_area) != 0 else 0
            # Solidity
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            solidity = float(area) / hull_area if int(hull_area) != 0 else 0

            # Perimeter
            perimeter = cv2.arcLength(contour, True)

            # Color Mean in Contour, find each contour's mean color
            current_contour_mask = np.zeros(img_binary.shape, dtype="uint8")
            cv2.drawContours(current_contour_mask, [contour], -1, 255, -1)
            # B, G, R
            (contour_color_mean, contour_color_stddv) = cv2.meanStdDev(original_img,
                                                                       mask=current_contour_mask)
            # Grab mean for each channels
            (contour_B_mean, contour_G_mean, contour_R_mean) = [contour_color_mean[0], contour_color_mean[1],
                                                                contour_color_mean[2]]
            contour_gray_mean = 0.299 * contour_R_mean + 0.587 * contour_G_mean + 0.114 * contour_B_mean
            # contour_avr_mean = (contour_B_m + contour_G_m + contour_R_m ) / 3

            # Grab std for each channels
            (contour_B_std, contour_G_std, contour_R_std) = [contour_color_stddv[0], contour_color_stddv[1],
                                                             contour_color_stddv[2]]
            contour_gray_std = 0.299 * contour_R_std + 0.587 * contour_G_std + 0.114 * contour_B_std
            # contour_avr_std = (contour_B_std + contour_G_s + contour_R_s) / 3
            if self.color_plane_selection == "red":
                current_contour_color_mean = contour_R_mean
                current_contour_color_std = contour_R_std
                current_contour_color_std_mean = current_contour_color_mean + current_contour_color_std
            elif self.color_plane_selection == "green":
                current_contour_color_mean = contour_G_mean
                current_contour_color_std = contour_G_std
                current_contour_color_std_mean = current_contour_color_mean + current_contour_color_std
            elif self.color_plane_selection == "blue":
                current_contour_color_mean = contour_B_mean
                current_contour_color_std = contour_B_std
                current_contour_color_std_mean = current_contour_color_mean + current_contour_color_std
            elif self.color_plane_selection == "gray":
                current_contour_color_mean = contour_gray_mean
                current_contour_color_std = contour_gray_std
                current_contour_color_std_mean = current_contour_color_mean + current_contour_color_std
            else:
                print("Error: Incorrect Plane Selection!")
            if area > self.area_lowerBound and area < self.area_upperBound \
                    and self.aspect_threshold_lower < aspect_ratio_contour \
                    and aspect_ratio_contour < self.aspect_threshold_upper \
                    and extent > self.extent_ratio_lower \
                    and extent < self.extent_ratio_upper \
                    and solidity > self.solid_ratio_lower \
                    and solidity < self.solid_ratio_upper \
                    and current_contour_color_std_mean > current_contour_color_mean - current_contour_color_std * self.color_mean_std_alpha_low \
                    and current_contour_color_std_mean < current_contour_color_mean + current_contour_color_std * self.color_mean_std_alpha_hi:  # Thresholding to find noise
                # print(contour)
                cv2.drawContours(contour_filtered_mask, [contour], -1, 255, -1)

                # Draw the rotated rectangle
                # cv2.drawContours(bb_filter, [box], 0, (0, 255, 0), 2)

                # Draw the straight rectangle
                cv2.rectangle(bb_filter, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # print(cv2.contourArea(contour))
        if self.debug_mode_selection == "debug":
            cv2.imshow('All bounding boxes', bb_no_filter)
            cv2.imshow('Bounding boxes to be filtered', bb_filter)
        # image_black = cv2.drawContours(image_black, contours1, -1, (0, 255, 255), thickness=-1)
        # cv2.imshow('contours w/o filter', image_black)
        # bitwise_AND operation
        # cv2.imshow("Filter", contour_filtered_mask)
        img_white_mask = np.full_like(original_img, fill_value=(255, 255, 255))
        contour_removed = cv2.bitwise_and(original_img, img_white_mask, mask=contour_filtered_mask)
        # cv2.imshow("Final Testing Result", contour_removed)

        return contour_removed

    def color_segmentation_hsv(self, original_img, hsv_img, low_range_color, high_range_color):
        mask = cv2.inRange(hsv_img, low_range_color, high_range_color)
        img_white_mask = np.full_like(original_img, fill_value=(255, 255, 255))
        result = cv2.bitwise_and(original_img, img_white_mask, mask=mask)
        return result

    def remove_high_intensity_white_light(self, original_img):
        dim_white = (0, 0, 100)
        bright_white = (100, 60, 255)
        hsv_img = cv2.cvtColor(original_img, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv_img, dim_white, bright_white)
        for idx, value in np.ndenumerate(mask):
            if value == 0:
                mask[idx] = 255
            elif value == 1 or value == 255:
                mask[idx] = 0
        cv2.imshow("white light remove mask", mask)
        img_white_mask = np.full_like(original_img, fill_value=(255, 255, 255))
        result = cv2.bitwise_and(original_img, img_white_mask, mask=mask)
        return result

    def image_plane_split(self, mode_debug, mode_displayColor, original_img):
        (img_B, img_G, img_R) = cv2.split(original_img)
        img_gray = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
        threshold = 220
        threshold_binary = 110
        threshold_R = threshold_binary
        threshold_G = threshold_binary
        threshold_B = threshold_binary
        binarization_high = 240
        ret, img_R_binarized = cv2.threshold(img_R, threshold_R, binarization_high, cv2.THRESH_BINARY)
        ret, img_G_binarized = cv2.threshold(img_G, threshold_G, binarization_high, cv2.THRESH_BINARY)
        ret, img_B_binarized = cv2.threshold(img_B, threshold_B, binarization_high, cv2.THRESH_BINARY)
        # cv2.imshow('Binarization R', img_R_binarized)
        # cv2.imshow('Binarization G', img_G_binarized)
        # cv2.imshow('Binarization B', img_B_binarized)
        if mode_debug == "debug":
            if mode_displayColor == "red":
                cv2.imshow('Red Plane', img_R)
                return img_R_binarized
            elif mode_displayColor == "green":
                cv2.imshow('Green Plane', img_G)
                return img_G_binarized
            elif mode_displayColor == "blue":
                cv2.imshow('Blue Plane', img_B)
                return img_B_binarized
            elif mode_displayColor == "gray":
                cv2.imshow("Gray Plane", img_gray)
                return img_gray
            else:
                print("Error: Incorrect Plane Selection!")
        else:
            if mode_displayColor == "red":
                return img_R_binarized
            elif mode_displayColor == "green":
                return img_G_binarized
            elif mode_displayColor == "blue":
                return img_B_binarized
            elif mode_displayColor == "gray":
                return img_gray
            else:
                print("Error: Incorrect Plane Selection!")

    # def gihub_connected_components(self, img_bgr):
    #     # Github Connected Components
    #     # connected_components = connectedComponentsProcessing.show_connected_components(image_binary)
    #     # if self.debug_mode_selection == "debug":
    #     #     cv2.imshow("Connect Componenets", connected_components)
    #     # config = None
    #
    #     # Convert to gray
    #     img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    #     # Blur
    #     img_gray_blur = cv2.medianBlur(img_gray, 5)
    #     img_gray_blur_canny = cv2.Canny(img_gray_blur, 40, 50, apertureSize=3)
    #     config = None
    #     connected_bounding_boxes = connectedComponentsProcessing.connected_components(img_gray_blur_canny, config)
    #
    #     # filtered_mask = np.zeros(img_gray_blur_canny.shape, dtype="uint8")
    #     # cv2.drawContours(filtered_mask, [connected_bounding_boxes], -1, 255, -1)
    #     # cv2.imshow("Connected Filter Mask", filtered_mask)

    def piplineProcess(self, img):
        # define desired dimension
        width = int(img.shape[1] * self.scale_percent / 100)
        height = int(img.shape[0] * self.scale_percent / 100)
        dim = (width, height)

        # resize image
        image_resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

        # Human removal process
        # image_resized_rgb = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)
        # hfr = humanRemoval(self.debug_mode_selection)
        # human_removed_bitwiseAND_img = hfr.remove(image_resized_rgb,dim,hfr_model)

        # reduced noise
        # image_noise_reduction = reduceNoise(image_resized,ddepth,kernel_size)
        # cv2.imshow('Noise Cancellation', image_noise_reduction)

        # White light removal
        # img_white_removed = self.remove_high_intensity_white_light(image_resized)
        # if self.debug_mode_selection == "debug":
        #     cv2.imshow('Image with high intensity white removed', img_white_removed)

        # Split color image plane
        img_plane = self.image_plane_split(self.debug_mode_selection,
                                           self.color_plane_selection, image_resized)

        # cv2.imshow('original original', image_resized)
        # Perform flare removal
        # img_flare_removed = flare_removal.flare_removal(flare_removal_model, image_resized)

        # Color segmentation
        # image_hsv = cv2.cvtColor(img_plane_B, cv2.COLOR_RGB2HSV)
        # color_seg_img = color_segmentation_hsv(img_plane_B,image_hsv, light_blue, dark_blue)
        # cv2.imshow('color segmentation', color_seg_img)

        # Gray scale process
        # img_gray = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)
        # color_seg_img_gray = cv2.cvtColor(color_seg_img, cv2.COLOR_RGB2GRAY)
        # if mode_str_sel == "gray":
        #     cv2.imshow('Gray Image', img_gray)

        # niblack_operation
        ni_result = self.niblack_binarization(img_plane, self.window_size, self.ni_k)

        ni_result = self.dilation_erosion(ni_result)

        # Countour_analysis
        contour_analysis_result = self.contour_analysis(ni_result, image_resized)

        # self.gihub_connected_components(contour_analysis_result)

        return contour_analysis_result

def main():
    SCREEN_SIZE = (1920, 1080)  # get it from your OS display settings
    IP_ADDRESS = "0.0.0.0"  # All IP address
    TCP_PORT = 8801
    BUFFER_LENGTH = 6553600

    # Load machine learning model
    # flare_removal_model = flare_removal.load_model('./Checkpoint-over-1000/model', None, 1)

    # Load human figure removal model
    # human_figure_removal_model_path = "./Mask-RCNN-TF2/samples/data_1.h5"
    # human_figure_removal_model = mrcnn.model.MaskRCNN(mode="inference",
    #                                   config=SimpleConfig(),
    #                                   model_dir=os.getcwd())
    # # hfr model load weight
    # human_figure_removal_model.load_weights(filepath=human_figure_removal_model_path,
    #                         by_name=True)
    # human_figure_removal_model = None

    # Image and video types
    # img_types = [".png", ".jpg", ".jpeg"]
    # video_types = [".mp4", ".mp3", ".avi"]

    # User Inputs
    # file_path = input("Please enter an image or video: ")
    while True:
        color_plane_selection = input("Please select one image plane from (red, green, blue, gray): ").lower()

        if color_plane_selection == "red" or color_plane_selection == "green" or color_plane_selection == "blue" or \
                color_plane_selection == "gray":
            break

    # debug_mode_selection = input("Please select a mode from (Normal, Debug): ").lower()
    debug_mode_selection = "Normal"

    # file_name, ext = os.path.splitext(file_path)

    # Start program class
    program = textExtraction(color_plane_selection, debug_mode_selection)
    # program.print_hi('CTI One Testing 2022-7-22')
    # Process image
    '''
    if ext.lower() in img_types:
        image = cv2.imread(file_path)
        # piplineProcess
        program.piplineProcess(image)
        # wait key destroy all windows
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    # Process Video
    elif ext.lower() in video_types:
        cap = cv2.VideoCapture(file_path)
        while (cap.isOpened()):
            # read frame
            ret, image = cap.read()
            # piplineProcess
            program.piplineProcess(image)
            # Time sleep
            time.sleep(.3)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()

        cv2.waitKey(0)
        cv2.destroyAllWindows()
    '''

    # 2022-06-08 YY receive a image from a Swift client
    # TCP/IP Socket programming part
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((IP_ADDRESS, TCP_PORT))
    # server_sock.settimeout(2)
    server_sock.listen(5)

    server_conn, addr = server_sock.accept()
    # server_sock.setblocking(0)
    times = []

    while True:
        try:
            t1 = time.time()
            frameBuffer = bytearray()

            while True:
                bufferData = server_conn.recv(BUFFER_LENGTH)
                frameBuffer += bufferData

                # print("bufferData size: ", len(bufferData))

                if b"IEND" in frameBuffer:  # b"IEND" is the EOF of PNG
                    break

            # print("Received Data Size :", len(frameBuffer))

            x = np.frombuffer(frameBuffer, dtype='uint8')
            # 2022-07-27 YY Catch "libpng error: PNG input buffer is incomplete"
            image_org = None
            try:
                image_org = cv2.imdecode(x, cv2.IMREAD_COLOR)

                image_org = cv2.resize(image_org, SCREEN_SIZE, cv2.INTER_AREA)

            except Exception as e:
                continue

            # CannyEdge of the original image
            contour_analysis_result = program.piplineProcess(image_org)
            t2 = time.time()

            processed_img = cv2.putText(contour_analysis_result, 'TT3c: Handwriting', (300, 600),
                                           cv2.FONT_HERSHEY_SIMPLEX,
                                           3, (0, 255, 0), 8, cv2.LINE_AA)
            times.append(t2 - t1)
            times = times[-20:]
            ms = sum(times) / len(times) * 1000
            fps = 1000 / ms

            processed_img = cv2.putText(processed_img, "FPS: {:.1f}".format(fps), (0, 100),
                                           cv2.FONT_HERSHEY_COMPLEX_SMALL, 3, (0, 255, 0), 2)

            rtn, img_detected_png = cv2.imencode('.png', processed_img)
            server_conn.sendall(img_detected_png)

        except KeyboardInterrupt:
            # print("KeyboarInterrupt")
            break

        except Exception as e:
            print("Program END")
            # print("Error #####: ", traceback.format_exc())
            break


if __name__ == '__main__':
    main()
