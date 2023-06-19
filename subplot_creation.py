import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.patches import BoxStyle
import matplotlib as mpl
import numpy as np
from itertools import chain
import glob
import os
import inspect
import copy

from plot_functions import *

ns = [f.split("\\")[-1] for f in glob.glob(f'{file_plot(to_plot)}/*')]

# Crear un conjunto de subplots para cada material y cada valor de L
#Nombre del estilo: S1_Ei(A)P_Ag_air__L50_R5__lam_400_1200_3000

for n in ns:
    files = glob.glob(f'{file_plot(to_plot)}/{n}/*.dat')
    file_name = [f.split("\\")[-1].split('.')[0] for f in files]
    # Crear una lista de todos los valores únicos de material en los nombres de archivo

    materials = sorted(set([f.split('_')[2] for f in file_name]))

    for material in materials:
        L_files = [f for f in file_name if f.split('_')[2] == material]      #Alguna otra manera de hacerlo, definiendo una función con todos os elementos de un archivo separados?
        L_values = sorted(set([int(f.split('_')[5][1:])  for f in L_files]))        #Lista int ordenados

        n_L = len(L_values)
        figure = make_subfigures(n_L, material, n, magnitudes_plot, figure_title = False, packed = False, share_ax = 'tot', Visible_labels= False)

        axs_flattened_ = figure[0]
        fig_ = figure[1]
        nrows, ncols = figure[2]       
        mode = figure[3]

        lam0 = max(set([int(f.split('_')[-3]) for f in L_files]))
        lamf = max(set([int(f.split('_')[-2]) for f in L_files]))
        nlam = max(set([int(f.split('_')[-1]) for f in L_files]))
        
        n_Rmax = 0
        for li, L in enumerate(L_values):           # li corresponde a cada subplot. Accedemos a cada elemeto del array de axs. axs_E és un array
            R_values = sorted(set([int(f.split('_')[6][1:]) for f in L_files if int(f.split('_')[5][1:]) == L]))   #Coge los valores de R de los archivos con igual L


            color_palette_ = color_palettes(magnitudes_plot, R_values)  #Diccionario

            if len(R_values) > n_Rmax:
                n_Rmax = len(R_values)
                max_R_values = R_values
                color_max_ = color_palette_ #Para la leyenda        
            #print(axs_flattened_)
            ax_ = {}
            for k, sub_list in enumerate(magnitudes_plot):
                for mag in sub_list:    
                    #print(mag, sub_list)         
                    ax_[mag] = axs_flattened_[mag][li]
                    print(ax_[mag])
                    #ax_[mag].text(0.1, 0.9, f'L = {L} nm', color = 'purple', fontweight = 'bold', transform=ax_[mag].transAxes) # establecer títulos para cada subtrama

                    L_title = ax_[mag].legend([], title = f'L = {L} nm', fontsize = 'x-small', alignment = 'center', loc = 'upper left')
                    L_title.get_frame().set_edgecolor('black')
                    L_title.get_frame().set_facecolor('#E5E6FA')            
                    L_title.get_title().set_fontproperties({'family':'Times New Roman', 'size': 11}) #'weight': 'bold'

            #transform=plt.gca().transAxes is referencing the current axes using plt.gca(), which returns the last created axes. 
            #ax_E.set_ylim([0,400])

            lineas_unicas_ = {} # TypeError: unhashable type: 'list'” error is raised when you try to assign a list as a key in a dictionary. Assign a hashable object, such as a string or a tuple, as a key for a dictionary.
            for ri, R in enumerate(R_values):
                R_files = [f for f in L_files if int(f.split('_')[5][1:]) == L and int(f.split('_')[6][1:]) == R]
                color_ = {}
                


                for k, sub_list in enumerate(magnitudes_plot):
                    for mag in sub_list: 
                        color_[mag] = color_palette_[mag](ri)

                if not R_files:
                    continue    
                
                # Cargar los datos utilizando numpy.genfromtxt() y el convertidor personalizado
                data = np.genfromtxt(os.path.join(file_plot(to_plot), n, R_files[0] + ".dat"), 
                                     dtype=[float]*5 + [complex]*3, converters={-3: complex_converter, -2: complex_converter, -1: complex_converter}, 
                                     skip_header=2, unpack= True) #Se trata de un array de tuplas!
                #What is returned is called a structured ndarray.
                # This is because your data is not homogeneous, i.e. not all elements have the same type.
                #  Numpy arrays have to be homogeneous.
                #The structured array 'solves' this constraint of homogeneity by using tuples for each record or row, that's the reason the returned array is 1D

                
                #data = np.loadtxt(os.path.join(file_plot(to_plot), n, R_files[0] + ".dat"), dtype='float', skiprows=2) El limitador por defecto es " " en catnidad variable de espacios
                
                #Esto NO está bien
                #column_names = np.loadtxt(os.path.join(file_plot(to_plot), n, R_files[0] + ".dat"), 
                #        dtype=str, skiprows = 1, max_rows= 2)
                #for i in range(zip(list(chain(*magnitudes_plot)), column_names)):
                

                
                mags_data = np.loadtxt(os.path.join(file_plot(to_plot), n, R_files[0] + ".dat"), 
                                        dtype=str, skiprows = 1, max_rows= 1)[1:] # ['sext_t' 'sext_l' 'sabs_t' 'sabs_l' 'alpha_x' 'alpha_y' 'alpha_z']
                mag_col_num_ = {}

                
                for mag_key, mag_name in magnitudes_names_in_data_.items(): #Esto podria ir como función afuera
                        for c, column_mag_data in enumerate(mags_data):
                            if mag_name == column_mag_data:
                                mag_col_num_[mag_key] = c + 1
                print(mag_col_num_)
                print(0, mags_data)
                #print(1, S_magnitudes_names_in_data_)
                #print(2, mag_col_num_)
                #print(ax_)
                #print(mag_col_num_)
                for mag, col in mag_col_num_.items():
                    for sublist in magnitudes_plot:
                        if mag in sublist:
                            if mag.startswith('E') or mag.startswith('A') or mag.startswith('P') or mag.startswith('e'):
                                print(col, mag, ax_)
                                ax_[mag].plot(data[:][0], data[:][col], color = color_[mag], linestyle ='-', label=f'R = {R}') #supported values are '-', '--', '-.', ':', 'None', ' ', '', 'solid', 'dashed', 'dashdot', 'dotted'
                                lineas_unicas_[mag] = []
                            elif mag.startswith('p'):
                                linea_real, = ax_[mag].plot(data[:][0], np.real(data[:][col]), color = color_[mag], linestyle = '-', linewidth = 1.2, label = f'R = {R}')  #He quitado el label de f"R ={R}"
                                linea_imag, = ax_[mag].plot(data[:][0], np.imag(data[:][col]), color = color_[mag], linestyle = '--', linewidth = 1.2, label = f'R = {R}')
                                lineas_unicas_[mag] = []
                                if linea_real not in lineas_unicas_[mag]: #Como podria hacer esto más dinámica, y a parte?
                                    lineas_unicas_[mag].append(linea_real)
                                if linea_imag not in lineas_unicas_[mag]:
                                    lineas_unicas_[mag].append(linea_imag)         
                
                print(lineas_unicas_)
                                #ax_E.plot(data[:, 0], data[:, 1], label=f'R = {R}')
                                #lineas_unicas[0].set_color('black')
                #lineas_unicas[1].set_color('black')
                #También se podria:
                # lines, = ax.get_legend_handles_labels()

            #lineas_unicas_ = {'Et': [], 'El': [], 'At': [], 'Al': [], 'px': [<matplotlib.lines.Line2D object at 0x000001BF93BF6E60>, <matplotlib.lines.Line2D object at 0x000001BF93BF7100>], 'py': [<matplotlib.lines.Line2D object at 0x000001BF93BF73A0>, <matplotlib.lines.Line2D object at 0x000001BF93BF7640>], 'pz': [<matplotlib.lines.Line2D object at 0x000001BF93BF78E0>, <matplotlib.lines.Line2D object at 0x000001BF93BF7B80>]}

            for k, sub_list in enumerate(magnitudes_plot):
                for mag in sub_list: 

                    if li == 0: # 1º L
                        #ax_[mag].set_xlim(600,800)
                        print(mag, ax_[mag])
                        #ax_[mag].set_ylim(0,50)
                        #autoscale(ax_[mag], 'y', margin=0.1)

        #print(ax_, lineas_unicas_, color_max_)
        for k, sub_list in enumerate(magnitudes_plot):
            for mag in sub_list:
                #print(mag, ax_)

                #print(ax_[mag], lineas_unicas_[mag], color_max_[mag], max_R_values)   
                set_legend(ax_[mag], fig_[mag], mode, lineas_unicas_[mag], color_max_[mag], max_R_values, nrows, ncols)


        #bbox_to_anchor = (0, -0.1, 1, 1), bbox_transform = plt.gcf().transFigure
        #plt.figlegend([f"R = {value}" for value in max_R_values], loc='outside lower right', labelspacing=0.2,  prop={'size': 13} ) #bbox_to_anchor=(0.5, 0.0), borderaxespad=0.1. Distance of a legend from the bounding box edge is set by the borderaxespad argument





        #layout="constrained"   
        #plt.tight_layout()
        #Polarizability: Real: linea solida, imag dashed. diferentes colores para R. O si se hace un unico plot, diferentes tonalidades para R, y dif col para L
        
        filepath_ = {}
        for k, sub_list in enumerate(magnitudes_plot):
            for mag in sub_list:
                if tipo_plot == 'S':
                    filename = f'{mag}_{material}_{n}__lam_{lam0}_{lamf}_{nlam}.png'
                    filepath_[mag] = os.path.join(os.path.join(directorio_actual, to_plot),".plots", filename)
                elif tipo_plot == 'R':
                    filename = f'{mag}_{material}_{n}__lam_{lam0}_{lamf}_{nlam}.png'
                    filepath_[mag] = os.path.join(os.path.join(directorio_actual, to_plot),".plots", filename)

        #print(filename)
        if not os.path.exists(os.path.join(os.path.join(directorio_actual, to_plot),".plots")):
            os.makedirs(os.path.join(os.path.join(directorio_actual, to_plot),".plots"))

        for k, sub_list in enumerate(magnitudes_plot):
            for mag in sub_list:  
                fig_[mag].savefig(filepath_[mag], dpi=1500)

#plt.show()
