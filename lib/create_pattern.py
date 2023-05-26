import os.path

import numpy as np
from PIL import Image


def create_HW_patterns(output_folder,width, height):
    # black
    img_black = np.zeros((height, width, 3), dtype=np.uint8)
    # img *= 255 # white background
    # cv2.imshow('result', img)
    # cv2.imwrite("./pattern/black.bmp", img_black)
    im = Image.fromarray(img_black)
    im.convert('RGB').save(os.path.join(output_folder,"black.bmp"))

    # white
    img_white = np.ones((height, width, 3), dtype=np.uint8) * 255
    im = Image.fromarray(img_white)
    im.convert('RGB').save(os.path.join(output_folder,"white.bmp"))

    # blue
    img_blue = np.zeros((height, width, 3), dtype=np.uint8)
    img_blue[:, :] = (0, 0, 255)
    im = Image.fromarray(img_blue)
    im.convert('RGB').save(os.path.join(output_folder,"blue.bmp"))

    # green
    img_green = np.zeros((height, width, 3), dtype=np.uint8)
    img_green[:, :] = (0, 255, 0)
    # cv2.imwrite("./pattern/green.bmp", img_green)
    im = Image.fromarray(img_green)
    im.convert('RGB').save(os.path.join(output_folder,"green.bmp"))

    # red
    img_red = np.zeros((height, width, 3), dtype=np.uint8)
    img_red[:, :] = (255, 0, 0)
    # cv2.imwrite("./pattern/red.bmp", img_red)
    im = Image.fromarray(img_red)
    im.convert('RGB').save(os.path.join(output_folder,"red.bmp"))

    # row reversion
    img_row1 = np.ones((height, width, 3), dtype=np.uint8) * 255  # white
    for i in range(0, height, 2):
        img_row1[i, :] = (0, 0, 0)  # black
    # cv2.imwrite("./pattern/row.bmp", img_row1)
    im = Image.fromarray(img_row1)
    im.convert('RGB').save(os.path.join(output_folder,"row_reversion_01.bmp"))

    img_row2 = np.zeros((height, width, 3), dtype=np.uint8)  # black
    for i in range(0, height, 2):
        img_row2[i, :] = (255, 255, 255)  # white
    # cv2.imwrite("./pattern/reverse_row.bmp", img_row2)
    im = Image.fromarray(img_row2)
    im.convert('RGB').save(os.path.join(output_folder,"row_reversion_02.bmp"))

    # col reversion
    img_col1 = np.ones((height, width, 3), dtype=np.uint8) * 255  # white
    for i in range(0, width, 2):
        img_col1[:, i] = (0, 0, 0)  # black
    # cv2.imwrite("./pattern/col.bmp", img_col1)
    im = Image.fromarray(img_col1)
    im.convert('RGB').save(os.path.join(output_folder,"col_reversion_01.bmp"))

    img_col2 = np.zeros((height, width, 3), dtype=np.uint8)  # black
    for i in range(0, width, 2):
        img_col2[:, i] = (255, 255, 255)  # white
    # cv2.imwrite("./pattern/reverse_col.bmp", img_col2)
    im = Image.fromarray(img_col2)
    im.convert('RGB').save(os.path.join(output_folder,"col_reversion_02.bmp"))

    # col green purple reversion
    img_col1 = np.zeros((height, width, 3), dtype=np.uint8)  # black
    for i in range(0, width, 2):
        img_col1[:, i] = (128, 0, 128)  # purple
        img_col1[:, i + 1] = (0, 128, 0)  # purple

    # cv2.imwrite("./pattern/col_green_purple.bmp", img_col1)
    im = Image.fromarray(img_col1)
    im.convert('RGB').save(os.path.join(output_folder,"col_green_purple_reversion_01.bmp"))

    img_col2 = np.zeros((height, width, 3), dtype=np.uint8)  # black
    for i in range(0, width, 2):
        img_col2[:, i] = (0, 128, 0)
        img_col2[:, i + 1] = (128, 0, 128)
    # cv2.imwrite("./pattern/reverse_col_green_purple.bmp", img_col2)
    im = Image.fromarray(img_col2)
    im.convert('RGB').save(os.path.join(output_folder,"col_green_purple_reversion_02.bmp"))

    # dot reversion
    img_dot1 = np.zeros((height, width, 3), dtype=np.uint8)  # black
    for i in range(0, height):
        for j in range(0, width, 2):
            if i % 2 == 0:
                img_dot1[i, j] = (0, 0, 0)  # black
                img_dot1[i, j + 1] = (255, 255, 255)  # white
            else:
                img_dot1[i, j] = (255, 255, 255)  # white
                img_dot1[i, j + 1] = (0, 0, 0)  # black

    # cv2.imwrite("./pattern/dot.bmp", img_dot1)
    im = Image.fromarray(img_dot1)
    im.convert('RGB').save(os.path.join(output_folder,"dot_reversion_01.bmp"))

    img_dot2 = np.zeros((height, width, 3), dtype=np.uint8)  # black
    for i in range(0, height):
        for j in range(0, width, 2):
            if i % 2 == 0:
                img_dot2[i, j] = (255, 255, 255)  # white
                img_dot2[i, j + 1] = (0, 0, 0)  # black
            else:
                img_dot2[i, j] = (0, 0, 0)  # black
                img_dot2[i, j + 1] = (255, 255, 255)  # white
    # cv2.imwrite("./pattern/reverse_dot.bmp", img_dot2)
    im = Image.fromarray(img_dot2)
    im.convert('RGB').save(os.path.join(output_folder,"dot_reversion_02.bmp"))

    # double_dot reversion
    img_dot1 = np.zeros((height, width, 3), dtype=np.uint8)  # black
    for i in range(0, height, 2):
        for j in range(0, width, 2):
            if i % 4 == 0:
                img_dot1[i:i + 2, j] = (0, 0, 0)  # black
                img_dot1[i:i + 2, j + 1] = (255, 255, 255)  # white
            else:
                img_dot1[i:i + 2, j] = (255, 255, 255)  # white
                img_dot1[i:i + 2, j + 1] = (0, 0, 0)  # black
    # cv2.imwrite("./pattern/double_dot.bmp", img_dot1)
    im = Image.fromarray(img_dot1)
    im.convert('RGB').save(os.path.join(output_folder,"double_dot_reversion_01.bmp"))

    img_dot2 = np.zeros((height, width, 3), dtype=np.uint8)  # black
    for i in range(0, height, 2):
        for j in range(0, width, 2):
            if i % 4 == 0:
                img_dot2[i:i + 2, j] = (255, 255, 255)  # white
                img_dot2[i:i + 2, j + 1] = (0, 0, 0)  # black
            else:
                img_dot2[i:i + 2, j] = (0, 0, 0)  # black
                img_dot2[i:i + 2, j + 1] = (255, 255, 255)  # white
    # cv2.imwrite("./pattern/reverse_double_dot.bmp", img_dot2)
    im = Image.fromarray(img_dot2)
    im.convert('RGB').save(os.path.join(output_folder,"double_dot_reversion_02.bmp"))

    # vertical

    region_limit = height // 5

    img_vertical = np.ones((height, width, 3), dtype=np.uint8) * 255  # white

    for i in range(region_limit, region_limit * 2, 2):  # 1 line
        img_vertical[i, :] = (0, 0, 0)  # black

    for i in range(region_limit * 2, region_limit * 3, 3):  # 2line
        img_vertical[i:i + 2, :] = (0, 0, 0)  # black

    for i in range(region_limit * 3, region_limit * 4, 4):  # 3line
        img_vertical[i:i + 3, :] = (0, 0, 0)  # black
    for i in range(region_limit * 4, region_limit * 5, 5):  # 4line
        img_vertical[i:i + 4, :] = (0, 0, 0)  # black

    # cv2.imwrite("./pattern/vertical.bmp", img_vertical)
    im = Image.fromarray(img_vertical)
    im.convert('RGB').save(os.path.join(output_folder,"vertical.bmp"))

    #
    # horizontal

    region_limit = width // 5

    img_horizon = np.ones((height, width, 3), dtype=np.uint8) * 255  # white

    for i in range(region_limit, region_limit * 2, 2):  # 1 line
        img_horizon[:, i] = (0, 0, 0)  # black

    for i in range(region_limit * 2, region_limit * 3, 3):  # 2line
        img_horizon[:, i:i + 2] = (0, 0, 0)  # black

    for i in range(region_limit * 3, region_limit * 4, 4):  # 3line
        img_horizon[:, i:i + 3] = (0, 0, 0)  # black
    for i in range(region_limit * 4, region_limit * 5, 5):  # 4line
        img_horizon[:, i:i + 4] = (0, 0, 0)  # black

    # cv2.imwrite("./pattern/horizontal.bmp", img_horizon)
    im = Image.fromarray(img_horizon)
    im.convert('RGB').save(os.path.join(output_folder,"horizontal.bmp"))

def create_BOE_patterns(output_folder,width, height):
    # black
    img_black = np.zeros((height, width, 3), dtype=np.uint8)
    # img *= 255 # white background
    # cv2.imshow('result', img)
    # cv2.imwrite("./pattern/black.bmp", img_black)
    im = Image.fromarray(img_black)
    im.convert('RGB').save(os.path.join(output_folder,"black.bmp"))

    # white
    img_white = np.ones((height, width, 3), dtype=np.uint8) * 255
    im = Image.fromarray(img_white)
    im.convert('RGB').save(os.path.join(output_folder,"white.bmp"))

    # Zebra1
    img_row = np.ones((height, width, 3), dtype=np.uint8) * 255  # white
    for i in range(0, height, 2):
        img_row[i, :] = (0, 0, 0)  # black
    # cv2.imwrite("./pattern/row.bmp", img_row1)
    im = Image.fromarray(img_row)
    im.convert('RGB').save(os.path.join(output_folder,"Zebra_1.bmp"))

    # Zebra2
    img_row = np.ones((height, width, 3), dtype=np.uint8) * 255  # white
    for i in range(0, height, 4):
        img_row[i:i+2, :] = (0, 0, 0)  # black
    # cv2.imwrite("./pattern/row.bmp", img_row1)
    im = Image.fromarray(img_row)
    im.convert('RGB').save(os.path.join(output_folder, "Zebra_2.bmp"))

    # Zebra3
    img_row = np.ones((height, width, 3), dtype=np.uint8) * 255  # white
    for i in range(0, height, 6):
        img_row[i:i + 3, :] = (0, 0, 0)  # black
    # cv2.imwrite("./pattern/row.bmp", img_row1)
    im = Image.fromarray(img_row)
    im.convert('RGB').save(os.path.join(output_folder, "Zebra_3.bmp"))

    # Zebra5
    img_row = np.ones((height, width, 3), dtype=np.uint8) * 255  # white
    for i in range(0, height, 10):
        img_row[i:i + 5, :] = (0, 0, 0)  # black
    # cv2.imwrite("./pattern/row.bmp", img_row1)
    im = Image.fromarray(img_row)
    im.convert('RGB').save(os.path.join(output_folder, "Zebra_5.bmp"))

    # Zebra 10
    img_row = np.ones((height, width, 3), dtype=np.uint8) * 255  # white
    for i in range(0, height, 20):
        img_row[i:i + 10, :] = (0, 0, 0)  # black
    # cv2.imwrite("./pattern/row.bmp", img_row1)
    im = Image.fromarray(img_row)
    im.convert('RGB').save(os.path.join(output_folder, "Zebra_10.bmp"))

def create_VNX_patterns(output_folder,width, height):
    # black
    img_black = np.zeros((height, width, 3), dtype=np.uint8)
    # img *= 255 # white background
    # cv2.imshow('result', img)
    # cv2.imwrite("./pattern/black.bmp", img_black)
    im = Image.fromarray(img_black)
    im.convert('RGB').save(os.path.join(output_folder, "black.bmp"))

    # white
    img_white = np.ones((height, width, 3), dtype=np.uint8) * 255
    im = Image.fromarray(img_white)
    im.convert('RGB').save(os.path.join(output_folder, "white.bmp"))

    # row reversion
    img_row1 = np.ones((height, width, 3), dtype=np.uint8) * 255  # white
    for i in range(0, height, 2):
        img_row1[i, :] = (0, 0, 0)  # black
    # cv2.imwrite("./pattern/row.bmp", img_row1)
    im = Image.fromarray(img_row1)
    im.convert('RGB').save(os.path.join(output_folder, "row.bmp"))

    # col reversion
    img_col1 = np.ones((height, width, 3), dtype=np.uint8) * 255  # white
    for i in range(0, width, 2):
        img_col1[:, i] = (0, 0, 0)  # black
    # cv2.imwrite("./pattern/col.bmp", img_col1)
    im = Image.fromarray(img_col1)
    im.convert('RGB').save(os.path.join(output_folder, "col.bmp"))

    # dot
    img_dot1 = np.zeros((height, width, 3), dtype=np.uint8)  # black
    for i in range(0, height):
        for j in range(0, width, 2):
            if i % 2 == 0:
                img_dot1[i, j] = (0, 0, 0)  # black
                img_dot1[i, j + 1] = (255, 255, 255)  # white
            else:
                img_dot1[i, j] = (255, 255, 255)  # white
                img_dot1[i, j + 1] = (0, 0, 0)  # black

    # cv2.imwrite("./pattern/dot.bmp", img_dot1)
    im = Image.fromarray(img_dot1)
    im.convert('RGB').save(os.path.join(output_folder, "dot.bmp"))

    # double_dot reversion
    img_dot1 = np.zeros((height, width, 3), dtype=np.uint8)  # black
    for i in range(0, height, 2):
        for j in range(0, width, 2):
            if i % 4 == 0:
                img_dot1[i:i + 2, j] = (0, 0, 0)  # black
                img_dot1[i:i + 2, j + 1] = (255, 255, 255)  # white
            else:
                img_dot1[i:i + 2, j] = (255, 255, 255)  # white
                img_dot1[i:i + 2, j + 1] = (0, 0, 0)  # black
    # cv2.imwrite("./pattern/double_dot.bmp", img_dot1)
    im = Image.fromarray(img_dot1)
    im.convert('RGB').save(os.path.join(output_folder, "double_dot.bmp"))


def create_CSOT_pattern(output_folder,width, height):
    # black
    img_black = np.zeros((height, width, 3), dtype=np.uint8)
    # img *= 255 # white background
    # cv2.imshow('result', img)
    # cv2.imwrite("./pattern/black.bmp", img_black)
    im = Image.fromarray(img_black)
    im.convert('RGB').save(os.path.join(output_folder, "black.bmp"))

    # white
    img_white = np.ones((height, width, 3), dtype=np.uint8) * 255
    im = Image.fromarray(img_white)
    im.convert('RGB').save(os.path.join(output_folder, "white.bmp"))

    # unknown
    img_unknown = np.ones((height, width, 3), dtype=np.uint8) * 255
    img_unknown[:, :] = (128, 128, 128)
    img_unknown = Image.fromarray(img_unknown)

    img_unknown.convert('RGB').save(os.path.join(output_folder, "unknown.bmp"))

    # dot
    img_dot1 = np.zeros((height, width, 3), dtype=np.uint8)  # black
    for i in range(0, height):
        for j in range(0, width, 2):
            if i % 2 == 0:
                img_dot1[i, j] = (0, 0, 0)  # black
                img_dot1[i, j + 1] = (255, 255, 255)  # white
            else:
                img_dot1[i, j] = (255, 255, 255)  # white
                img_dot1[i, j + 1] = (0, 0, 0)  # black

    # cv2.imwrite("./pattern/dot.bmp", img_dot1)
    im = Image.fromarray(img_dot1)
    im.convert('RGB').save(os.path.join(output_folder, "dot.bmp"))



    # Zebra1
    img_row = np.ones((height, width, 3), dtype=np.uint8) * 255  # white
    for i in range(0, height, 2):
        img_row[i, :] = (0, 0, 0)  # black
    # cv2.imwrite("./pattern/row.bmp", img_row1)
    im = Image.fromarray(img_row)
    im.convert('RGB').save(os.path.join(output_folder, "Zebra_1.bmp"))

    # Zebra2
    img_row = np.ones((height, width, 3), dtype=np.uint8) * 255  # white
    for i in range(0, height, 4):
        img_row[i:i + 2, :] = (0, 0, 0)  # black
    # cv2.imwrite("./pattern/row.bmp", img_row1)
    im = Image.fromarray(img_row)
    im.convert('RGB').save(os.path.join(output_folder, "Zebra_2.bmp"))

    # Zebra3
    img_row = np.ones((height, width, 3), dtype=np.uint8) * 255  # white
    for i in range(0, height, 6):
        img_row[i:i + 3, :] = (0, 0, 0)  # black
    # cv2.imwrite("./pattern/row.bmp", img_row1)
    im = Image.fromarray(img_row)
    im.convert('RGB').save(os.path.join(output_folder, "Zebra_3.bmp"))

    # Zebra5
    img_row = np.ones((height, width, 3), dtype=np.uint8) * 255  # white
    for i in range(0, height, 10):
        img_row[i:i + 5, :] = (0, 0, 0)  # black
    # cv2.imwrite("./pattern/row.bmp", img_row1)
    im = Image.fromarray(img_row)
    im.convert('RGB').save(os.path.join(output_folder, "Zebra_5.bmp"))

    # Zebra 10
    img_row = np.ones((height, width, 3), dtype=np.uint8) * 255  # white
    for i in range(0, height, 20):
        img_row[i:i + 10, :] = (0, 0, 0)  # black
    # cv2.imwrite("./pattern/row.bmp", img_row1)
    im = Image.fromarray(img_row)
    im.convert('RGB').save(os.path.join(output_folder, "Zebra_10.bmp"))

    pass

def create_Zebra_patterns(output_path,width, height,black_num,white_num,flag_Row):
    # black
    img_zebra = np.ones((height, width, 3), dtype=np.uint8) * 255
    step = black_num + white_num
    if flag_Row:
        for i in range(0, height, step):
            img_zebra[i:i + black_num, :] = (0, 0, 0)  # black
    else:
        for i in range(0, height, step):
            img_zebra[:,i:i + black_num] = (0, 0, 0)  # black

    im = Image.fromarray(img_zebra)
    im.convert('RGB').save(output_path)

def create_Dot_patterns(output_path,width, height,dot_width,dot_height):

    img_dot = np.zeros((height, width, 3), dtype=np.uint8)  # black
    for i in range(0, height,dot_height):
        for j in range(0, width, 2*dot_width):
            if i % (dot_height*2) == 0:
                # img_dot[i:i + dot_height, j: j +dot_width] = (0, 0, 0)  # black
                img_dot[i:i + dot_height, j +dot_width : j + dot_width *2] = (255, 255, 255)  # white
            else:
                img_dot[i:i + dot_height, j: j +dot_width] = (255, 255, 255)  # white
                # img_dot[i:i + 2, j + 1] = (0, 0, 0)  # black


    im = Image.fromarray(img_dot)
    im.convert('RGB').save(output_path)




if __name__ == '__main__':
    path = r"C:\workspace\Bitbucket\ETS_Data_Analyser\pattern\custom"
    # create_Dot_patterns(path,1440,3440,60,20)
    create_CSOT_pattern(path,1080,2640)