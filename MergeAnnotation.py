import os

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import cv2
import h5py

from ImageDraw import ReadLabelingImg, ReadCoreImg
from GenerationH5 import OneHot



def GetAllCoreImgPath(core_img_folder):

    return [os.path.join(core_img_folder, img_index) for img_index in os.listdir(core_img_folder) if
            os.path.splitext(img_index)[-1] == '.jpg']


def GetAllAnnotationImgPath(annotation_img_folder, pathologists_num=6):
    all_annotation_path_list = []
    for pathologists_index in range(pathologists_num):
        sub_annotation_path = os.path.join(annotation_img_folder, 'Maps'+str(pathologists_index+1)+'_T')
        sub_annotation_path_list = [os.path.join(sub_annotation_path, img_index) for img_index in
                                    os.listdir(sub_annotation_path) if os.path.splitext(img_index)[-1] == '.png']
        all_annotation_path_list.append(sub_annotation_path_list)
    return all_annotation_path_list


def CheckSingleCase(core_img_path, all_annotation_folder_path_list):
    core_index = os.path.split(core_img_path)[-1].replace('.jpg', '')

    annotation_path_list = []
    for pathologists_index in range(len(all_annotation_folder_path_list)):
        for sub_annotation_img_path in all_annotation_folder_path_list[pathologists_index]:
            if sub_annotation_img_path.rfind(core_index) != -1:
                annotation_path_list.append(sub_annotation_img_path)

    # for index in annotation_path_list:
    #     print(index)
    return annotation_path_list



def MergeAnnotation(core_img_path, annotation_img_path_list, store_path='', show=False):
    core_img_array, case_name = ReadCoreImg(core_img_path)
    core_img_array = cv2.resize(core_img_array, (512, 512), interpolation=cv2.INTER_NEAREST)
    annotation_dict = {}

    merged_annotation_array = np.zeros((core_img_array.shape[0],core_img_array.shape[1], len(annotation_img_path_list)))
    for annotation_index in range(len(annotation_img_path_list)):
        annotation_img_array, pathologist_num = ReadLabelingImg(annotation_img_path_list[annotation_index])
        annotation_img_array = cv2.resize(cv2.resize(annotation_img_array, (512, 512), interpolation=cv2.INTER_NEAREST),
                                          (512, 512), interpolation=cv2.INTER_NEAREST)
        annotation_dict[pathologist_num] = annotation_img_array

        merged_annotation_array[..., annotation_index] = annotation_img_array


    modal_merged_annotation_array = np.zeros((merged_annotation_array.shape[:2]))
    for row in range(merged_annotation_array.shape[0]):
        for col in range(merged_annotation_array.shape[1]):
            # print(row, col)
            annotation_array = np.array(merged_annotation_array[row, col, :], dtype=np.int64)

            count = np.bincount(annotation_array)
            modal_merged_annotation_array[row, col] = np.argmax(count)

    if show:
        Show(core_img_array, modal_merged_annotation_array)

    if store_path:
        h5_store_path = os.path.join(store_path, case_name+'.h5')
        with h5py.File(h5_store_path, 'w') as h5_file:
            h5_file['input_0'] = core_img_array / 255
            h5_file['output_0'] = OneHot(modal_merged_annotation_array)

    return modal_merged_annotation_array


def Show(core_img_array, modal_merged_annotation_array, store_path='', show=True):
    plt.subplot(241)
    plt.imshow(core_img_array)
    plt.xticks([])
    plt.yticks([])
    plt.title('Core Img' + '\n' + str(core_img_array.shape))
    
    
    one_hot_array = OneHot(modal_merged_annotation_array)

    plt.imshow(core_img_array)
    # plt.contour(downsampled_annotation_img_array)
    plt.title('input_0 ' + '\n' + str(one_hot_array.shape))
    plt.xticks([])
    plt.yticks([])

    plt.subplot(242)
    plt.hist(core_img_array.flatten(), density=True)
    plt.title('pixel distribution of core img')

    plt.subplot(243)
    plt.imshow(one_hot_array[:, :, 0])
    plt.title('output_0 ' + '\n' + str(one_hot_array.shape) + '\n' + '000000')
    plt.xticks([])
    plt.yticks([])

    plt.subplot(244)
    plt.imshow(one_hot_array[:, :, 1])
    plt.title('output_0 ' + '\n' + str(one_hot_array.shape) + '\n' + '010000')
    plt.xticks([])
    plt.yticks([])

    plt.subplot(245)
    plt.imshow(one_hot_array[:, :, 2])
    plt.title('output_0 ' + '\n' + str(one_hot_array.shape) + '\n' + '001000')
    plt.xticks([])
    plt.yticks([])

    plt.subplot(246)
    plt.imshow(one_hot_array[:, :, 3])
    plt.title('output_0' + '\n' + str(one_hot_array.shape) + '\n' + '000100')
    plt.xticks([])
    plt.yticks([])

    plt.subplot(247)
    plt.imshow(one_hot_array[:, :, 4])
    plt.title('output_0 ' + '\n' + str(one_hot_array.shape) + '\n' + '000010')
    plt.xticks([])
    plt.yticks([])

    plt.subplot(248)
    plt.imshow(one_hot_array[:, :, 5])
    plt.title('output_0 ' + '\n' + str(one_hot_array.shape) + '\n' + '000001')
    plt.xticks([])
    plt.yticks([])

    if store_path:
        plt.savefig(store_path)

    if show:
        plt.show()

    plt.close()



def GenerationH5(core_img_folder, store_folder):
    for sub_file in os.listdir(core_img_folder):
        if sub_file.rfind('.jpg') != -1:
            sub_file_path = os.path.join(core_img_folder, sub_file)
            print(sub_file_path)

            MergeAnnotation(sub_file_path,
                            CheckSingleCase(sub_file_path, GetAllAnnotationImgPath(r'Y:\MRIData\OpenData\Gleason2019')),
                            store_path=store_folder)
# CheckSingleCase('slide001_core003', GetAllAnnotationImgPath(r'W:\MRIData\OpenData\Gleason2019'))
# core_img_path = r'Y:\MRIData\OpenData\Gleason2019\Train Imgs\slide002_core041.jpg'
# MergeAnnotation(core_img_path,
#                 CheckSingleCase(core_img_path, GetAllAnnotationImgPath(r'Y:\MRIData\OpenData\Gleason2019')))

GenerationH5(r'Y:\MRIData\OpenData\Gleason2019\Train Imgs',
             r'X:\PrcoessedData\Challenge_Gleason2019\ProcessedH5_merged_512\all_data')