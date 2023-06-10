import numpy as np
from pylnk import parser
import os, winshell, win32com.client, Pythoncom
import glob

#desktop = winshell.desktop()
#path = os.path.join(desktop, 'File Shortcut Demo.lnk')

directorio_actual = os.path.dirname(os.path.abspath(__file__))

target = 'S'

if target == 'S':
    files = glob.glob('S*')
elif target == 'R':
    files = glob.glob('R*')

#files_name = os.path.basename(files)

def create_shortcut(in_path, out_path):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(out_path)
    shortcut.Targetpath = in_path
    shortcut.IconLocation = in_path
    shortcut.save()

start_file_names = [f.split('_')[0] for f in files]
for f in files: 
    data_rutes = glob.glob(f'{f}/**/*.dat')
    data_names = [os.path.basename(i) for i in data_rutes] #S1_Ei(A)p_Ag_air__L50_R5__lam_400_1200_3000
    values_list = [[f.split('_')] for f in data_names]
    for n in values_list[n][3]:
        path_n = os.path.join('ST', f'{n}')
        for material in values_list[n][2]:
            path_material = os.path.join(path_n, f'{material}')
            for L in values_list[n][4][1:]:
                path_L = os.path.join(path_material, f'{L}')
                for f in data_rutes:
                    in_path = data_rutes[f]
                    for R in values_list[n][5][1:]
                        "%s_EAp_%s_%s__L%d_R%d__lam_%d_%d_%d.dat", start_file_names[f], material, n, L, R, 

                    out_path = path_L
                    create_shortcut(in_path, out_path)

                    max_sigmas = np.loadtxt(in_path, dtype=str, skiprows = 0, max_rows= 0)[1:]
                    #Separar texto
                    








def read_file_from_shortcut(shortcut_path):
    shortcut = parser.parse(shortcut_path)
    original_file_path = shortcut.local_path.replace("\\", "/")  # Reemplaza las barras invertidas por barras inclinadas

    with open(original_file_path, 'r') as file:
        content = file.read()

    