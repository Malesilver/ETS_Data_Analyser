import os
import time
import numpy as np
import matplotlib.pyplot as plt
import math
from itertools import cycle, islice

def check_if_plots_directory_exists(directory):

    plot_Directory = os.path.join(directory,'plots')

    Directory_exists = os. path. exists(plot_Directory)
    if not Directory_exists:
        os.makedirs(plot_Directory)

def Dart_Board(accuracy_error, graph_title, centre_error, edge_error, finger_size, directory):

    print('accuracy error', accuracy_error)
    print('graph title', graph_title)
    print('centre error', centre_error)
    print('full error', edge_error)
    max_error = math.ceil(abs(accuracy_error.max().max()))
    figure, axes = plt.subplots()
    axes.set_aspect(1)
    axes.plot(accuracy_error['X_delta'], accuracy_error['Y_delta'], 'o', color='r')
    # accuracy_error.plot(x=0, y=1, kind='scatter', color='r')
    theta = np.linspace(0, 2 * np.pi, 100)
    for i in np.arange(centre_error, max_error + 0.5, 0.5):
        # x1 = i * np.cos(theta)
        # x2 = i * np.sin(theta)
        # plt.plot(x1, x2, color='k')
        Drawing_uncolored_circle = plt.Circle((0, 0), i, fill=False, color='k')
        axes.add_patch(Drawing_uncolored_circle)
    axes.axhline(y=0, color='k')
    axes.axvline(x=0, color='k')
    axes.set_xlim([-edge_error - 0.5, edge_error + 0.5])
    axes.set_ylim([-edge_error - 0.5, edge_error + 0.5])
    graph_title_with_size = graph_title + '-' + str(finger_size)
    axes.set_title(graph_title_with_size)
    axes.set_xlabel('Accuracy Error X (mm)')
    axes.set_ylabel('Accuracy Error Y (mm)')

    check_if_plots_directory_exists(directory)
    filename = directory+'\\plots\\'+graph_title_with_size+'-Dart_Board'
    plt.savefig(filename)
    return figure

def Touch_Sensor_Plot(frame, touchxaxisname, touchyaxisname, robotxaxisname, robotyaxisname, graph_title, xaxislabel, yaxislabel, finger_size, directory):
    fig,ax = plt.subplots()
    frame.plot(x=touchxaxisname, y=touchyaxisname, kind='scatter', color='r',ax=ax)  # plot the touch sensor X and Y position
    frame.plot(x=robotxaxisname, y=robotyaxisname, kind='scatter', ax=ax)  # plot the X and Y robot data
    plt.legend(["touch sensor", "robot"])  # plot legend
    graph_title_with_size = graph_title+'-'+str(finger_size)
    plt.title(graph_title_with_size)
    plt.xlabel(xaxislabel)
    plt.ylabel(yaxislabel)
    plt.legend(["touch sensor", "robot"], bbox_to_anchor=(0.5, -0.2), loc=8)
    plt.tight_layout()
    check_if_plots_directory_exists(directory)
    filename = directory+'\\plots\\'+graph_title_with_size+'-Sensor_plot'
    plt.savefig(filename)
    return fig

def Scatter_Plot_df(data, xaxisname, yaxisname, title, xaxislabel, yaxislabel, finger_size, directory):
    fig, ax = plt.subplots()
    data.plot(x=xaxisname, y=yaxisname, kind='scatter', color='r',ax=ax)
    print('Title -', title)
    graph_title_with_size = title + '-' + str(finger_size)
    print(graph_title_with_size)
    plt.title(graph_title_with_size)
    plt.xlabel(xaxislabel)
    plt.ylabel(yaxislabel)
    check_if_plots_directory_exists(directory)
    filename = directory+'\\plots\\'+graph_title_with_size+'-Scatter_plot'
    plt.savefig(filename)
    return fig

def Scatter_Plot_List_of_Lists(data_list):
    plt.figure()
    for i in data_list:
        color_index = data_list.index(i)
        color = 'C' + str(color_index)
        plt.scatter(i[0], i[1], s=0.5, color=color)
        plt.title("Linearity")
        plt.xlabel('X lines')
        plt.ylabel('Y lines')
        plt.legend(range(data_list.index(i)+1), markerscale=10, bbox_to_anchor=(1.1, 1))
        plt.tight_layout()
        #plt.show()

def Line_Plot(data, col_index, title, finger_size, directory, speed):
    color = 'C' + str(col_index)
    plt.plot(data, color=color)
    plt.title(title+" - Line: " + str(col_index) + ' - ' + str(finger_size)+' - '+str(speed) + 'mmS')
    plt.xlabel('Frame Number')
    graph_title = title +'-Line:'+str(col_index)+'-'+ str(finger_size)+str(speed) + 'mmS'
    filename = directory+'\\plots\\'+graph_title+'-Line_plot'+'fart'
    plt.savefig(filename)
    plt.figure()
    #plt.show()

def Line_Plot_all(data_list,title, finger_size, directory, speed):
    figure, axes = plt.subplots()
    start_index = 0
    for i, data in enumerate(data_list):
        color = 'C' + str(i)
        x = np.arange(start_index, start_index + len(data))
        axes.plot(x, data, color=color)
        start_index += len(data) - 1
    plt.legend(range(len(data_list)+1), markerscale=10)
    graph_title = title + str(finger_size) + str(speed) + 'mmS'
    plt.title(graph_title)
    filename = directory + '\\plots\\' + graph_title + '-Line_plot.png'
    plt.savefig(filename)
    return figure

