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

#Quitar titulo general del plot
#ncols, nrows de la funcón make_figure, global variables??
#Mirar si quitar el primer valor de la escala del ylabel
#Generalizar make_subfigures. Para que tome como argumentos E, P, etc.
#Remove ticks only if constrained y sin los valores de los ejes
#Que los graficos descentrados queden en el medio y aparte.
#Modificar el titulo del subplot. -Pintarlo de color
#titulo de L, color?. Leyendas de R, todas? una?. Leyenda de Im o Re. Leyenda más bonita
#PROBLEMAS con las leyendas: centrar el texto, modifiar el linewidth, posicionamiento de la leyenda.
#Cambiar los colores de los plots

#Separar EiP -> E, P -> título de los plots
#Mirar que rango de lambda plotear
#Si tengo una carpeta ST Plot de la tendencia entre s_max y lambda
#Implementar si la carpeta es R o S (lo que quiero plotear)
#Cuando calcule por primera vez un S, me incluya el codigo de subplot
#Testear si guardar la imagen como .pdf o .png o .jpg

#Falta ver el caso en que no quiera ploetar respecto de la longitud de onda !!

#Opcion para ajustar escalas que sean iguales, True or False, default True.


#Cambiar la escala para que sea la misma. Según el máximo pico de todos los plots.
#Añadir poner que tipo de material es y el medio. Titulo generico (activar/desactivar)


#ruta del directorio actual:  os.getcwd()
directorio_actual = os.path.dirname(os.path.abspath(__file__))
print(directorio_actual)

to_plot = 'R5'
#to_calc = [['El']]
to_calc = [['Pa', 'Pe']]

def obtener_magnitudes(plot_file = to_plot, magnitudes=None):
    if plot_file.startswith('S'):
        S_mags = [['El', 'Et'], ['Al', 'At'], ['px', 'py', 'pz']]  #Se podria añadir comprobar que las magnitudes de aquí concuerden con las del archivo abierto.
        if magnitudes is None:
            to_calc = S_mags
        else:
            to_calc = magnitudes
        tipo_plot = 'S'
    elif plot_file.startswith('R'):
        R_mags = [['Pa', 'ePa'], ['Pe', 'ePe'], ['ex', 'ey', 'ez'], ['Al', 'El', 'pz']]
        if magnitudes is None:
            to_calc = R_mags
        else:
            to_calc = magnitudes
        tipo_plot = 'R'
    else:
        print("Tipo de plots no válido. Debe ser 'S(num)(T)' o 'R(num)(T)'.")
        return None
    return to_calc, tipo_plot


magnitudes_plot, tipo_plot = obtener_magnitudes(plot_file = to_plot, magnitudes=to_calc)

def magnitudes_names_in_data(tipo_plot):
    if tipo_plot == 'S':
        S_magnitudes_names_in_data_ = {'Et': 'sext_t', 'El': 'sext_l', 
                                'At': 'sabs_t', 'Al': 'sabs_l', 
                                'px': 'alpha_x', 'py': 'alpha_y', 'pz': 'alpha_z'}
        return S_magnitudes_names_in_data_
    if tipo_plot == 'R':
        R_magnitudes_names_in_data_ = {'Pa': 'Pt_abs', 'ePa': 'erPt_abs', 
                                'Pe': 'Pt_ext', 'ePe': 'erPt_ext', 
                                'ex': 'ext_x', 'ey': 'ext_y', 'ez': 'ext_z', 
                                'Al': 'sabs_l', 'El': 'sext_l', 'pz': 'alpha_z'}
        return R_magnitudes_names_in_data_

magnitudes_names_in_data_ = magnitudes_names_in_data(tipo_plot)


def labels(magnitudes, tipo_plot = tipo_plot): #Incluir que si el nombre del archivo dice que está normalizado, añadir / A ó / V, sino no.
    labels = {}
    if tipo_plot == 'S':
        for sublista in magnitudes:
            for mag in sublista:
                if mag.startswith('E') or mag.startswith('A'):
                    prefix = '$\sigma^'
                    if mag.startswith('E'):
                        suffix = '{ext}' + f'_{mag[1]}$' + ' / A'
                    elif mag.startswith('A'):
                        suffix = '{abs}' + f'_{mag[1]}$' + ' / A'
                elif mag.startswith('p'):
                    prefix = '$\\alpha_'
                    suffix = mag[1] + '$' + ' / V'
                else:
                    raise TypeError('Hay variables no consideradas')
                
                labels[mag] = prefix + suffix 

    if tipo_plot == 'R':
        for sublista in magnitudes:
            for mag in sublista:
                if mag.startswith('P'):
                    prefix = '$P_'
                    if mag[1] == 'a':
                        suffix = '{abs}$'
                    elif mag[1] == 'e':
                        suffix = '{ext}$'
                elif mag.startswith('eP'):
                    suffix = ' error'
                    if mag[2] == 'a':
                        prefix = '$P_{t,abs}$'
                    elif mag[2] == 'e':
                        prefix = '$P_{t, ext}$'
                elif mag.startswith('e'):
                    prefix = 'Ext$_'
                    suffix = mag[1] + '$' + ' / A' #NOSE
            
                elif mag.startswith('E') or mag.startswith('A'):
                    prefix = '$\sigma^'
                    if mag.startswith('E'):
                        suffix = '{ext}' + f'_{mag[1]}$' + ' / A'
                    elif mag.startswith('A'):
                        suffix = '{abs}' + f'_{mag[1]}$' + ' / A'
                elif mag.startswith('p'):
                    prefix = '$\\alpha_'
                    suffix = mag[1] + '$' + ' / V'
                else:
                    raise TypeError('Hay variables no consideradas')
                labels[mag] = prefix + suffix 
    if not labels:
        print("El diccionario está vacío. Se han introducido mal las magnitudes a calcular.")
                
    return labels

def color_palettes(magnitudes, R_values):
    color_palette_ = {} 

    for i, sub_list in enumerate(magnitudes):
        for mag in sub_list:    
            if mag.startswith('E') or mag.startswith('A'):
                color_palette_[mag] = plt.cm.get_cmap('Accent', len(R_values))                
            elif mag.startswith('p'):
                color_palette_[mag] = plt.cm.get_cmap('Dark2', len(R_values)) 
            else:
                color_palette_[mag] = plt.cm.get_cmap('Set1', len(R_values)) 
    return color_palette_






def file_plot(to_plot): #Si hay mas de una carpeta parece da error.?
    dir = os.path.join(directorio_actual,to_plot)
    name = glob.glob(f"{dir}*")
    if len(name) == 1:
        name = name[0]
    else:
        raise TypeError("Hay más carpetas que coinciden con el patrón de 'to_plot'.")
    return name


def complex_converter(s):
    s = s.decode().replace("im", "j")
    return complex(s)

def is_prime(numero):
    if numero < 2:
        return False
    for i in range(2, int(numero ** 0.5) + 1):
        if numero % i == 0:
            return False
    return True


#La raiz cuadrada de un numero establece un "nodo de simetria". Divisores a la derecha y izquierda, en mismas posiciones, multiplicados entre ellos dan ese numero.
def divisores(numero):
    lista_divisores = []
    for i in range(1, int(np.sqrt(numero)) + 1):
        if numero % i == 0:
            lista_divisores.append(i)
            if i != numero // i:
                lista_divisores.append(numero // i)
    lista_divisores.sort()
    return lista_divisores
#math.isqrt: rounds a square root number downwards to the nearest integer

def divisores_cercanos_raiz(numero): 
    lista_divisores = divisores(numero)
    raiz = np.sqrt(numero)
    dif_min = float('inf')
    divisor1 = None
    divisor2 = None
    if raiz == int(raiz):
      return int(raiz), int(raiz)  # Si es un cuadrado perfecto, devuelve la raíz repetida

    for divisor in lista_divisores:
        diferencia = abs(raiz - divisor)
        if diferencia < dif_min and divisor < raiz:
            dif_min = diferencia
            divisor1 = divisor
        elif diferencia < dif_min and divisor > raiz:
            dif_min = diferencia
            divisor1 = divisor
            divisor2 = None

    if divisor2 is None:
        for divisor in lista_divisores:
            if divisor != divisor1 and divisor > raiz:
                divisor2 = divisor
                break
    return divisor1, divisor2

#the difference is that the code always checks to see if an 'if' statement 
# is true, checks 'elif' statements only if each 'if' and 'elif' statement above 
# it is false, and 'else' runs only when the conditions for all attached 'if' and 'elif' statements are false.

def remove_ticks_labels(ax, ticks, labels, remove_x=True, remove_y=True, perimeter=False):

    if isinstance(ax, list):
        if not any(isinstance(item, list) for item in ax): #Si es solo una lista, es una unica fila de varias columnas
            ax = [ax]
        ax = np.array(ax) #Así acceder a los indices de un array: ax[i,j]
        rows = ax.shape[0] if ax.shape[0] > 1 else 1
        cols = ax.shape[1] if len(ax.shape) > 1 else 1 

    elif isinstance(ax, plt.axes): #Si es un array significa que la figura se ha hecho como matriz en make_figure
        gs = ax[0].get_gridspec()
        rows = gs.nrows
        cols = gs.ncols
    else:
      raise TypeError("Solo se admiten listas de axes o matriz de axes")

    #rows = np.size(ax, 0)
    #cols = np.size(ax, 1)
    if rows == 1 and cols == 1:
        pass
    elif rows == 1 and cols > 1:
        if remove_y:
            for j in range(cols):
                if ticks == True:
                    ax[0,j].yaxis.set_ticks_position('left' if j == 0 else 'none') #Supongo que no es necesario ax[i,0]
                if labels == True:
                    ax[0,j].tick_params(labelleft=True if j == 0 else False)

    elif cols == 1 and rows > 1:
        if remove_x:
            for i in range(rows):
              if ticks == True:
                  ax[i,0].xaxis.set_ticks_position('bottom' if i == rows - 1 else 'none')
                  if labels == True:
                      ax[i,0].tick_params(labelbottom=True if i == rows - 1 else False)
                
    else: 
        for i in range(rows):  # Eliminar líneas de ticks
            for j in range(cols):
                if remove_x:
                    if ticks == True:
                        ax[i, j].xaxis.set_ticks_position('bottom' if i == rows - 1 else 'none')
                    if labels == True:
                        ax[i,j].tick_params(labelbottom = True if i == rows - 1 else False)

                if remove_y:
                    if ticks == True:
                        ax[i, j].yaxis.set_ticks_position('left' if j == 0 else 'none')
                    if labels == True:
                        ax[i,j].tick_params(labelleft = True if j == 0 else False)
        
                if perimeter: #Aqui hay algo del todo no correcto Podria hacerse más compacto.
                    if remove_x or remove_y:
                        pass
                    else:
                        if i == 0:
                            ax[i, j].xaxis.set_ticks_position('top')
                            plt.setp(ax[i, j].get_xticklabels(), visible=False)
                        elif i == rows - 1:
                            ax[i, j].xaxis.set_ticks_position('bottom')
                        else:
                            ax[i, j].xaxis.set_ticks_position('none')

                        if j == 0:
                            ax[i, j].yaxis.set_ticks_position('left')
                        elif j == cols - 1:
                            ax[i, j].yaxis.set_ticks_position('right')
                            plt.setp(ax[i, j].get_yticklabels(), visible=False)
                        else:
                            ax[i, j].yaxis.set_ticks_position('none')

    return

def delete_external_ticklabels(): #No la he usado
  for ax in plt.gcf().axes:
    try:
      ax.label_outer()

      # Ocultar los ticks en los ejes interiores
      #x_ticks = ax.get_xticks()
      #y_ticks = ax.get_yticks()     
      #ax.set_xticks(x_ticks[1:-1])
      #ax.set_yticks(y_ticks[1:-1])
    except:
      pass

    
def share_axis(axs, prev_ax, share_all = 'True'): #prev_ax = axs_[mag][0][0]    #Only for list of lists or list of axes

    # Obtener el nombre de la variable proporcionada a la función  
    for nombre, valor in inspect.currentframe().f_back.f_locals.items():
        if valor is axs:
            axs_name = nombre
            break

    if isinstance(axs, list) and all(isinstance(ax, list) for ax in axs):
        rows = len(axs)  # Número de filas es igual a la longitud de la lista principal
        columns = len(axs[0]) #Mismo numero de elementos en las sublistas
        print(axs)
        for r in range(0, rows ):
            for c, ax in enumerate(axs[r][:]):
                    axs[r][0].get_shared_y_axes().join(axs[r][0], ax) #o simplement *axs_E to link all in the same row
            # row_E[0].get_shared_x_axes().join(row_E[0], *row_E)

        for c in range(0, columns): #No entiendo porque cols-1
            for r, ax in enumerate(axs[:][c-1]): # No entiendo porque  if r (c) != 0: lo hace mal
                    axs[0][c].get_shared_x_axes().join(axs[0][c], ax)
                    #print(295, c, [r, ax])
            #print(296, enumerate(axs[r][:]))

        if share_all:
            for c, ax in enumerate(axs[0][:]):
                    axs[0][0].get_shared_x_axes().join(axs[0][0], ax) # Cuidado! ahora es al revés. Igual compartim amb el ax[0][0] que despres fem autoscale
            for r, ax in enumerate(axs[:][0]):
                    axs[r-1][0].get_shared_y_axes().join(axs[r-1][0], ax) #No entiendo porque así si que funciona.
    elif isinstance(axs, list):
        for r, ax in enumerate(axs):
            if r != 0:
                axs[0].get_shared_y_axes().join(axs[0], ax)
                axs[0].get_shared_x_axes().join(axs[0], ax) #o simplement *axs_E to link all in the same row
        # Verificar si el nombre de la variable cumple con ciertas condiciones
        if share_all:
            if axs_name.startswith("axs_"):
                pass
            elif axs_name.startswith('rowunc'):
                axs[0].get_shared_y_axes().join(axs[0], prev_ax)
                axs[0].get_shared_x_axes().join(axs[0], prev_ax)         #MEJOR MANERA?
                return axs_name
    else:
        raise TypeError("El argumento 'axs' debe ser una lista o una lista de listas.")
    
#ax[i].spines['right'.set_visible(False)]
#ax.set_xticklabels([])




            #axs_E[0][0].autoscale()
            #axs_P[0][0].autoscale()
        #for i in range (columns):
        #        for j in range(rows-2):
        #            axs_E[j][i].sharey(axs_E[j][rows-1]) if j != 0 else None
        #            axs_P[j][i].sharey(axs_P[j][rows-1]) if j != 0 else None      

#Si he compartido los ejes por completo al primer axe, hacer un autoscale en solo el primer

def autoscale(ax=None, axis='y', margin=0.1):
    '''Autoscales the x or y axis of a given matplotlib ax object
    to fit the margins set by manually limits of the other axis,
    with margins in fraction of the width of the plot

    Defaults to current axes object if not specified.
    '''

    
    if ax is None:
        ax = plt.gca()
    newlow, newhigh = np.inf, -np.inf

    for artist in ax.collections + ax.lines:
        x,y = get_xy(artist)
        if axis == 'y':
            setlim = ax.set_ylim
            lim = ax.get_xlim()
            fixed, dependent = x, y
        else:
            setlim = ax.set_xlim
            lim = ax.get_ylim()
            fixed, dependent = y, x

        low, high = calculate_new_limit(fixed, dependent, lim)
        newlow = low if low < newlow else newlow
        newhigh = high if high > newhigh else newhigh

    margin = margin*(newhigh - newlow)

    setlim(newlow-margin, newhigh+margin)

def calculate_new_limit(fixed, dependent, limit):
    '''Calculates the min/max of the dependent axis given 
    a fixed axis with limits
    '''
    if len(fixed) > 2:
        mask = (fixed>limit[0]) & (fixed < limit[1]) & (~np.isnan(dependent)) & (~np.isnan(fixed))
        window = dependent[mask]
        try:
            low, high = window.min(), window.max()
        except ValueError:  # Will throw ValueError if `window` has zero elements
            low, high = np.inf, -np.inf
    else:
        low = dependent[0]
        high = dependent[-1]
        if low == 0.0 and high == 1.0:
            # This is a axhline in the autoscale direction
            low = np.inf
            high = -np.inf
    return low, high

def get_xy(artist):
    '''Gets the xy coordinates of a given artist
    '''
    if "Collection" in str(artist):
        x, y = artist.get_offsets().T
    elif "Line" in str(artist):
        x, y = artist.get_xdata(), artist.get_ydata()
    else:
        raise ValueError("This type of object isn't implemented yet")
    return x, y

#In the case of subplots with sharex=True, it doesn't matter which specific axes you choose to autoscale.
# Since all the subplots share the same x-axis, autoscaling any one of the subplots will update the x-axis limits for all the subplots.

class ExtendedTextBox_v2:
    """
    制作自己的box类，以提供调整width功能
    参考：
    https://stackoverflow.com/questions/40796117/how-do-i-make-the-width-of-the-title-box-span-the-entire-plot
    https://matplotlib.org/stable/gallery/userdemo/custom_boxstyle01.html?highlight=boxstyle+_style_list
    """

    def __init__(self, pad=0.3, width=500.):
        """
        The arguments must be floats and have default values.

        Parameters
        ----------
        pad : float
            amount of padding
        """
        self.width = width
        self.pad = pad
        super(ExtendedTextBox_v2, self).__init__()

    def __call__(self, x0, y0, width, height, mutation_size):
        """
        Given the location and size of the box, return the path of the box
        around it.

        Rotation is automatically taken care of.

        Parameters
        ----------
        x0, y0, width, height : float
            Box location and size.
        mutation_size : float
            Reference scale for the mutation, typically the text font size.
        """
        # padding
        pad = mutation_size * self.pad
        # width and height with padding added
        #width = width + 2.*pad
        height = height + 2.*pad
        # boundary of the padded box
        y0 = y0 - pad
        y1 = y0 + height
        _x0 = x0
        x0 = _x0 +width /2. - self.width/2.
        x1 = _x0 +width /2. + self.width/2.
        # return the new path

        cp = [(x0, y0),
              (x1, y0), (x1, y1), (x0, y1),
              (x0, y0)]

        com = [Path.MOVETO,
               Path.LINETO, Path.LINETO, Path.LINETO,
               Path.CLOSEPOLY]

        path = Path(cp, com)
        
        return path

def make_subfigures(n_L, magnitudes, figure_title, packed, share_ax = 'tot', Visible_labels = True): #Añadir que coja los titulos de eje según el nombre de archivo. EiP, lam
    fig_ = {}
    axs_ = {}

    if n_L == 3 or n_L == 2 or n_L ==1:
        columns = 1
        rows = n_L
    elif not is_prime(n_L):
        columns = divisores_cercanos_raiz(n_L)[0]
        rows = divisores_cercanos_raiz(n_L)[1]

    if not is_prime(n_L) and rows <= columns + 2:   #UnboundLocalError: local variable 'rows' referenced before assignment        #No sobren subplots en aquest cas 
        for i, sub_list in enumerate(magnitudes):
            for mag in sub_list:
                if share_ax == 'tot' or share_ax =='blocs': #Sempre que no "sobrin" suplots, es el que vull
                    fig_[mag], axs_[mag] = plt.subplots(rows, columns, figsize=(8, 8), sharex = True, sharey = True)  #No es posible poner la condición dentro?

                    if packed == True:
                        fig_[mag].subplots_adjust(hspace = 0, wspace = 0) # plt.subplots_adjust(hspace = 0, wspace = 0)
                        remove_ticks_labels(axs_[mag], ticks = True, labels = False, remove_x = True, remove_y = True, perimeter = False) #FUNCIONA BIEN. PENSAR SI QUITAR O NO  #remove_ticklabels  if sharex = True (adelantado), las labels se quitan automaticamente
                    elif Visible_labels == True:
                        axs_[mag].tick_params(labelbottom=True, labelleft = True) #NO SEGURO

                elif share_ax == 'cap':
                    fig_[mag], axs_[mag] = plt.subplots(rows, columns, figsize=(8, 8))
                    if packed == True:
                        raise TypeError("Para n_L = 3, 2 no acepto empaquetar y no compartir ejes.")
                else:
                    raise TypeError("El argumento 'share_ax' debe ser: 'tot', 'blocs', 'cap'.")
                
                #En caso de cambiar autoscale, se tendria que hacer aquí axs_[mag][0]
        #Retorna: tuple[Figure, ndarray] . ndarray (np.array) contrasta amb lista de listas


        if n_L == 1:
            for i, sub_list in enumerate(magnitudes):
                for mag in sub_list:                
                    axs_[mag] = [axs_[mag]]

        axs_flattened = {}
        ylabel = labels(magnitudes_plot, tipo_plot) #Diccionari PONER AL FINAL
        for mag in ylabel.keys():
            fig_[mag].supylabel(ylabel[mag])
            fig_[mag].supxlabel("wavalength $\lambda$ (nm)")
            if n_L != 1:
                axs_flattened[mag] = axs_[mag].flatten() #convertir una matriz array de ejes (Axes) en un arreglo unidimensional.
            elif n_L ==1:
                axs_flattened[mag] = axs_[mag]
            if figure_title == True:
                text_box = ExtendedTextBox_v2(pad =0.4, width = 0.8 * fig_[mag].get_window_extent().width) #pad: anchura vertical rectangulo
                title = fig_[mag].suptitle(f"{material} in {n}", position=(.5, 0.98), bbox={'facecolor': 'mistyrose', 'edgecolor': 'black', 'boxstyle': text_box})
                
            fig_[mag].tight_layout()
            #si no es packed poner si hacer que se vean todas o no.
            #ax_E.set_xlabel('wavalegth $\lambda$')
            #ax_E.set_ylabel('$\sigma^{ext}$ / $A$')

        return [axs_flattened, fig_, [rows, columns], 1]
        #n_L ==1 [{'Pa': [<Axes: >]}, {'Pa': <Figure size 800x800 with 1 Axes>}, [1, 1], 1]
        
        #axs_E[0].set_yticks(axs_E[0].get_yticks()[1:])
        #plt.subplots_adjust(hspace = 0, wspace = 0)
        #gs.update(hspace = 0)
        #fig.tight_layout()
        #fig_E.suptitle("Título del eje x", fontsize=12, ha='center')
        #No és necessari el flattened?

    else: #Si es primo o con 2 filas de mas que columnas. "Sobraran" subplots. NO ME INCLUYE SI rows > columns +2 !!!

        columns = int(np.round(np.sqrt(n_L)))   #np. round(). Redondea a unfloat, no quiero. The main difference is that round is a ufunc of the ndarray class, while np.around is a module-level function.
        rows = int(np.ceil(n_L / columns)) #D'aquesta manera, la figura que surt presenta la major proporció quadrada amb preferència de columna per ser la de menor nombre de dimensió             
        empty_subplots = rows * columns - n_L
        leftover_subplots = n_L - (rows - 1) * columns

            #Eliminar valores de las escalas que se cruzan
            #axs_E[0].set_yticks(axs_E[0].get_yticks()[1:])
            #gs = fig.add_gridspec(3, 3)
            #También gridspec.GridSpec() 

            #if packed all
            #gs_E.update(wspace = 0, hspace = 0)
            # Crear los subplots compartiendo el eje x

        for i, sub_list in enumerate(magnitudes):
            for mag in sub_list:
                if packed == False:
                    gs_top = mpl.gridspec.GridSpec(rows, 2 * columns) #Crear un nuevo diccionario  para cada magnitud ??
                if packed == True:
                    gs_top = mpl.gridspec.GridSpec(rows, 2 * columns, hspace = 0, wspace = 0)

                fig_[mag] = plt.figure(figsize=(8,8)) #DUDA . plt.subplot o plt.figure

                axs_[mag] = []

                for r in range(0, rows - 1):
                    row = []    
                    for c in range(0, columns):
                        ax = fig_[mag].add_subplot(gs_top[r, 2 * c:2 * c + 2])
                        row.append(ax)
                    axs_[mag].append(row)

                if share_ax == 'tot' or share_ax == 'blocs':
                    share_axis(axs_[mag], prev_ax = None, share_all= True) # share_all tant per columnes con files. en un mateix bloc
                    if packed == True:
                        remove_ticks_labels(axs_[mag], ticks = True, labels = True, remove_x = True, remove_y = True, perimeter = False) #FUNCIONA BIEN. PENSAR SI QUITAR O NO
                        #gs.update(wspace = 0, hspace = 0)
                    elif Visible_labels == False: #Los ticks se quedan
                        remove_ticks_labels(axs_[mag], ticks = False, labels = True, remove_x = True, remove_y = True, perimeter = False)

                if packed == False:
                    gs_bottom = mpl.gridspec.GridSpec(rows, 2 * columns)
                if packed == True:
                    gs_bottom = mpl.gridspec.GridSpec(rows, 2 * columns, wspace = 0)

                rowunc = []

                for r in range(0, leftover_subplots):
                    ax = fig_[mag].add_subplot(gs_bottom[rows - 1, empty_subplots + 2 * r:empty_subplots + 2 * r + 2])
                    rowunc.append(ax)

                if share_ax =='tot':
                    share_axis(rowunc, axs_[mag][0][0])
                    if packed == True:
                        remove_ticks_labels(rowunc, ticks = True, labels = True, remove_x = True, remove_y = True, perimeter = False) #FUNCIONA BIEN. PENSAR SI QUITAR O NO
                        #gs.update(wspace = 0, hspace = 0)  #Si ya se ha puesto antes, quizas ya está puesto, no hace falta ponerlo ahora
                    elif Visible_labels == False:
                        remove_ticks_labels(rowunc, ticks = False, labels = True, remove_x = True, remove_y = True, perimeter = False) 


                elif share_ax == 'blocs':
                    share_axis(rowunc, prev_ax = None, share_all= False) #Potser està malament
                    if packed == True:
                        remove_ticks_labels(rowunc, ticks = True, labels = True, remove_x = True, remove_y = True, perimeter = False) #FUNCIONA BIEN. PENSAR SI QUITAR O NO
                    elif Visible_labels == False:
                        remove_ticks_labels(rowunc, ticks = False, labels = True, remove_x = True, remove_y = True, perimeter = False)             
                    
                elif share_ax == 'cap' and packed == True:
                    raise TypeError("No acepto empaquetar y no compartir ejes.")
                elif share_ax == 'cap':
                    pass     
                else:
                    raise TypeError("Només s'admet 'share axis' segons 'tot', 'blocs' o 'cap'.")
                
                
                axs_[mag].append(rowunc) #Lista de listas
                #axs_P = np.r_[axs_P,rowunc_P] Solo funciona si ambos tienen la misma dimensión

        #BoxStyle._style_list["ext"] = ExtendedTextBox_v2
        axs_flattened = {}
        ylabel = labels(magnitudes_plot, tipo_plot)
        for mag in ylabel.keys():   
            fig_[mag].supylabel(ylabel[mag])
            fig_[mag].supxlabel("wavalength $\lambda$ (nm)") #NO ESTAN CENTRADOS
            axs_flattened[mag] = list(chain(*axs_[mag])) #Flatten the list using list comprehension and itertools.chain
            if figure_title == True:
                text_box = ExtendedTextBox_v2(pad =0.4, width = 0.8 * fig_[mag].get_window_extent().width) #pad: anchura vertical rectangulo
                title = fig_[mag].suptitle(f"{material} in {n}", position=(.5, 0.98), bbox={'facecolor': 'mistyrose', 'edgecolor': 'black', 'boxstyle': text_box})
                
            #title.get_bbox_patch().set_boxstyle("ext", pad=0.4, width= 0.8 * fig_[mag].get_window_extent().width )

            #def on_resize(event):
            #    title.get_bbox_patch().set_boxstyle("ext", pad=0.4, width=fig_[mag].get_window_extent().width )

            #cid = plt.gcf().canvas.mpl_connect('resize_event', on_resize)

            fig_[mag].tight_layout()  
            #fig_[mag].subplots_adjust(top=1)
                #Aqui solo afecta al último gráfico!! En caso de querer hacerlo en todos, poner un for
        return [axs_flattened, fig_, [rows, columns], 2]




def set_legend(ax_, fig_, mode, lineas_unicas_, color_max_, max_R_values):
    if mode == 1:

        ax_.legend(frameon=False, fontsize = 'small', labelspacing=0.2, loc = 'best')  #prop={'size':10}



    if mode == 2:
        def pos_leg(leg):           #Está mal. Posición relativa!
            if leg == 1 or leg == 2:
                adjust_x, adjust_y = 0.25, 0.35
            elif leg == 3:
                adjust_x, adjust_y = 0.53, 0.12

            pos_x = ((nrows*ncols - n_L)/2 + (n_L-(nrows-1)*ncols) + adjust_x/(ncols)) * 1/(ncols)
            pos_y = 1 - (nrows-1 + adjust_y) * 1/nrows
            if leg == 2:
                return 1-pos_x, pos_y    
            return pos_x, pos_y

        handles_1  = [mpatches.Patch(color=color_max_(i), label=f"{R}") for i, R in enumerate(max_R_values)] #Podria llamar: handles, labels = ax.get_legend_handles_labels() 
        #handles_copy = [copy.copy(ha) for ha in handles_1] No funciona
        #[ha.set_linewidth(1) for ha in handles_copy]
        leg_1= fig_.legend(handles = handles_1, loc='center', mode = 'expand', bbox_to_anchor= [pos_leg(1)[0], pos_leg(1)[1], 0.14,0], labelspacing=0.2,  fontsize = 'medium') #bbox_to_anchor=(0.5, 0.0), borderaxespad=0.1. Distance of a legend from the bounding box edge is set by the borderaxespad argument
        #title="Aspect ratio, R"    #markerscale = 0.1
        leg_1.get_frame().set_edgecolor('black')
        leg_1.get_frame().set_facecolor('#FFFFCB')

        #shift = max([t.get_window_extent().width for t in leg_1.get_texts()])
        #for t in leg_1.get_texts():
        #    t.set_ha('center') # ha is alias for horizontalalignment
        #    t.set_position((shift,0))

        h = leg_1.legend_handles
        t = leg_1.texts
        renderer = fig_.canvas.get_renderer()

        for i in range(len(h)):
            hbbox = h[i].get_window_extent(renderer) # bounding box of handle
            tbbox = t[i].get_window_extent(renderer) # bounding box of text

            x = tbbox.width *3 # keep default horizontal position    
            #y = (hbbox.height - tbbox.height) / 2. + hbbox.y0 # vertically center the
            # bbox of the text to the bbox of the handle.

            t[i].set_position((x, 0)) # set new position of the text

        #for text in leg_1.get_texts():
        #    text.set_ha('right')

        #leg_1.get_linewidth().set_linewidth(1.0). 'Legend' object has no attribute 'get_linewidth'
        #for line in leg_1.get_lines(): #Not doing anytihng
        #    line.set_linewidth(1.0)
        fig_.gca().add_artist(leg_1)


                    #plt.gca() devuelve el objeto de los ejes (axes) actuales en la figura actual, lo que permite 
        #realizar modificaciones al conjunto de ejes, como agregar elementos gráficos, establecer etiquetas de ejes, cambiar límites de ejes, entre otros.
        etiquetas = ['Re', 'Im']
        leg_2 = fig_.legend(lineas_unicas_, etiquetas, loc='center', bbox_to_anchor= [pos_leg(2)[0], pos_leg(2)[1]], labelspacing=0.2,  fontsize = 'medium', frameon = False) 
        for marker in leg_2.legend_handles:
            marker.set_color('black')   
        #mpl.rc('font', family = 'Times New Roman') Changes font to all axes legends The default settings of matplotlib
        
        #leg_title = fig_.legend([], title = 'Aspect ratio, R', fontsize = 'xx-small', loc = 'center', bbox_to_anchor= [pos_leg(3)[0], pos_leg(3)[1]])
        #leg_title.get_title().set_multialignment('center')
        #leg_title.get_frame().set_edgecolor('black')
        #leg_title.get_frame().set_facecolor('#E5E6FA')            
        #leg_title.get_title().set_fontproperties({'family':'Times New Roman', 'size': 11}) #'weight': 'bold'



        #for text in leg_title.get_texts():
        #    text.set_va('right')
        #for i, alpha in enumerate(np.linspace(0, 1, 11)):
        #    ax.add_patch(Rectangle((i, 0.05), 0.8, 0.6, alpha=alpha, zorder=0))
    return None




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
        figure = make_subfigures(n_L, magnitudes_plot, figure_title = False, packed = False, share_ax = 'tot', Visible_labels= False)

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


        for k, sub_list in enumerate(magnitudes_plot):
            for mag in sub_list:  
                print(mag, ax_)
                print(ax_[mag], lineas_unicas_[mag], color_max_[mag], max_R_values)   
                set_legend(ax_[mag], fig_[mag], mode, lineas_unicas_[mag], color_max_[mag], max_R_values)


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
