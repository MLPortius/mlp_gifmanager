#%% IMPORTAR LIBRERIAS

import os
import time
import tqdm
import argparse
import shutil
import zipfile

import warnings
warnings.filterwarnings('ignore')

from moviepy.editor import VideoFileClip


#%% CONFIGURAR ENTORNO
infolder = 'video_builder/input/'
outfolder = 'video_builder/output/'

#%% CONFIGURAR SCRIPT
parser = argparse.ArgumentParser(description='Creates a video file from a gif file.')

sourcetype = 'gif' # ['zip', 'gif']

parser.add_argument('-s', '--sourcetype', type=str, default='gif', choices=['gif','zip'], help='Use input folder gifs or unzip a gif folder')
parser.add_argument('-v', '--verbose', action='store_true', type=bool, default=True, help='Activate verbosity of script')
parser.add_argument('-r', '--reset', action='store_true', type=bool, default=False, help='Reset the output')

args = parser.parse_args()

sourcetype = args.sourcetype
verbose = args.verbose
reset = args.reset

#%% DEFINIR FUNCIONES AUXILIARES

def unzip_file(inpath, outpath):
    with zipfile.ZipFile(inpath, 'r') as zip_ref:
        zip_ref.extractall(outpath)

def reset_output(output_folder):
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

def create_video(input, output, verbose):
    clip = VideoFileClip(input)
    if verbose:
        clip.write_videofile(output, codec='libx264')
    else:
        clip.write_videofile(output, codec='libx264', logger=None)
    clip.close()


#%% DEFINIR FUNCIONES MODULO PRINCIPAL

def setup_zip(input_folder):

    # Configurar carpeta
    try:
        unzip_exists = os.path.isdir(input_folder + 'unzip/')
    except:
        unzip_exists = False

    if unzip_exists:
        shutil.rmtree(input_folder + 'unzip/')
    else:
        os.mkdir(input_folder + 'unzip/')

    # Cargar carpetas zip
        
    zip_files = [x for x in os.listdir(input_folder) if x.endswith('.zip')]

    # Descomprimir los zip
    for f in zip_files:
        unzip_file(input_folder + f, input_folder + 'unzip/')

    return input_folder + 'unzip/'


def load_gifs(input_folder):
    
    # Leer archivos
    input_files = os.listdir(input_folder)

    # Crear diccionario
    input_names = [x.split('.gif')[0] for x in input_files]
    input_paths = [input_folder +  x for x in input_files]

    # Ordenar archivos
    gif_files = []
    for i in tqdm.tqdm(range(len(input_files)), ncols=100, desc='Loading gif files'):
        gif_files.append({'name':input_names[i], 'file':input_files[i], 'path':input_paths[i]})

    return gif_files

def setup_reset(input_folder, output_folder, reset_flag):

    input_files_list = [x for x in os.listdir(input_folder) if x.endswith('.gif')]
    output_files_list = [x for x in os.listdir(output_folder) if x.endswith('.mp4')]

    name_input_list = [x.split('.gif')[0] for x in input_files_list]

    if reset_flag:
        
        reset_output(output_folder=output_folder)
        
        # Definir nombres nuevos
        output_names_dict = {}
        for name in name_input_list:
            output_names_dict[name] = name

    else:
        
        # Revisar resultados anteriores
        ndict = {}
        for name in name_input_list:
            ofiles = [x for x in output_files_list if name in x]
            ndict[name] = {'n':len(ofiles), 'ofiles':ofiles}
        
        # Definir nombres nuevos
        output_names_dict = {}
        for name in name_input_list:

            # Cuando no tiene output
            if ndict[name]['n'] == 0:
                output_names_dict[name] = name

            # Cuando hay solo un output original
            elif ndict[name]['n'] == 1:
                if ndict[name]['ofiles'][0].split('.' + 'mp4')[0][-2:] != '_0':
                    output_names_dict[name] = name + '_0'
                else:
                    output_names_dict[name] = name

            # Cuando hay mas de un output
            else:
                output_names_dict[name] = name + '_' + str(ndict[name]['n'])

    return output_names_dict


#%% MODULO PRINCIPAL

def __main__():

    if verbose:
        print('Starting process ...')
    
    st = time.time()

    # Gestionar carpeta zip
    if sourcetype == 'zip':
        if verbose:
            print('     ... managing zip folder')
        new_infolder = setup_zip(input_folder=infolder)
        infolder = new_infolder

    # Configrar reseteo
    if verbose:
        print('     ... defining output')
    output_names = setup_reset(input_folder=infolder, output_folder=outfolder, reset_flag=reset)

    # Cargar gifs
    if verbose:
        print('     ... loading gif files')
    gif_files = load_gifs(infolder)

    # Crear videos
    if verbose:
        print('     ... creating videos')
        print('\n --------------------------------------')

    for i in range(len(gif_files)):

        input_value = gif_files[i]['path']
        output_value = outfolder + output_names[gif_files[i]['name']] + '.' + 'mp4'

        create_video(input_value, output_value, verbose=verbose)

        if verbose:
            print('\n --------------------------------------')

    if verbose:
        print('\nProcess completed in ' + str(round((time.time() - st) / 60, 2)) + ' minutes.')

#%% EJECUTAR MODULO PRINCIPAL
            
if __name__ == '__main__':
    __main__()