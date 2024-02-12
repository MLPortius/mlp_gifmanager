#%% IMPORTAR LIBRERIAS
import os
import time
import tqdm
import argparse
from PIL import Image


#%% CONFIGURAR ENTORNO
infolder = 'gif_builder/input/'
outfolder = 'gif_builder/output/'

f1 = 80
f2 = 60
f3 = 40
f4 = 30
f5 = 20

#%% CONFIGURAR SCRIPT
parser = argparse.ArgumentParser(description='Creates a GIF from images.')

parser.add_argument('-n', '--name', type=str, default='output',  help='Gif file name')
parser.add_argument('-e', '--extension', type=str, default='.png', help='Argument for extension.')
parser.add_argument('-l', '--loops', type=int, default=0, help='Number of loops')
parser.add_argument('-r', '--reset', type=int, choices=[0, 1], default=0, help='Reset input folder')
parser.add_argument('-v', '--verbose', type=int, choices=[0, 1], default=1, help='Verbosity of script')
parser.add_argument('-b', '--bounce', type=int, choices=[0, 1], default=0, help='Bounce')
parser.add_argument('-bm', '--bounce_method', type=str, choices=['full', 'cont'], default='cont', help='Bouncing method')

parser.add_argument('-sm', '--speed_method', type=str, choices=['choice', 'set'], default='choice', help='Method to set speed')
parser.add_argument('-sc', '--speed_choice', type=str, choices=['slower', 'slow', 'normal', 'fast', 'faster', 'all'], default='normal', help='Choice of speed')
parser.add_argument('-s', '--speed', type=int, default=30, help='Speed of gif')

args = parser.parse_args()

name = args.name
loops = args.loops
reset = args.reset
verbose = args.verbose
bounce = args.bounce

if bounce == 1:
    bounce_method = args.bounce_method

extension = args.extension
if extension[0] != '.':
    extension = '.' + extension

speed_method = args.speed_method

if speed_method == 'choice':

    if args.speed_choice is None:
        print('You didnt specify a speed, defaulting to normal ...')
        speed_choice = 'normal'

    else:
        speed_choice = args.speed_choice

elif speed_method == 'set':

    if args.speed is None:
        print('You didnt specify a speed, defaulting to 30 ...')
        speed_set = 30
    
    else:
        speed_set = args.speed

if speed_method == 'choice':
    
    if speed_choice =='slower':
        speed = f1

    elif speed_choice == 'slow':
        speed = f2
    
    elif speed_choice == 'normal':
        speed = f3
    
    elif speed_choice == 'fast':
        speed = f4
    
    elif speed_choice == 'faster':
        speed = f5

    elif speed_choice == 'all':
        speed_dict = {}
        speed_dict['slower'] = f1
        speed_dict['slow'] = f2
        speed_dict['normal'] = f3
        speed_dict['fast'] = f4
        speed_dict['faster'] = f5

elif speed_method == 'set':
    speed = speed_set 


#%% DEFINIR FUNCIONES MODULO PRINCIPAL

def read_files(folder):

    dicto = {}
    dicto['files'] = sorted(os.listdir(folder))
    dicto['paths'] = [os.path.join(folder, f) for f in dicto['files']]
    dicto['names'] = [f.split('.')[0] for f in dicto['files']]
    dicto['n'] = len(dicto['files'])

    return dicto

def reset_folder(folder):

    files = read_files(folder['paths'])
    nf = len(files)

    for i in tqdm.tqdm(range(nf), ncols=100):
        file = files[i]
        os.remove(file)

def clear_extension(ext):

    if ext[0] != '.':
        output = '.' + ext
    else:
        output = ext

    return output

def load_images(container, use_tqdm=True):

    images = []

    if use_tqdm == True:
        for i in tqdm.tqdm(range(container['n']), ncols=100):
            f = container['paths'][i]
            img = Image.open(f)
            images.append(img)

    else:
        for i in range(container['n']):
            f = container['paths'][i]
            img = Image.open(f)
            images.append(img)

    return images

def setup_bounce(list, method):

    if method == 'full':
        output = list + list[::-1]
    
    elif method == 'cont':
        output = list + list[::-1][1:-1]

    return output
    
def save_gif(path, container, s, l=0):

    container[0].save(path, save_all=True, append_images=container[1:], duration=s, loop=l)

#%% DEFINIR MODULO PRINCIPAL

def __main__():

    print('Starting process ...')
    
    # READ FILES
    if verbose == 1:
        print('\nReading files ...')
    files = read_files(infolder)

    # LOAD IMAGES
    if verbose == 1:
        print('\nLoading images ...')
        images = load_images(files, use_tqdm=False)
    else:
        images = load_images(files, use_tqdm=True)

    # SETUP BOUNCE
    if bounce == 1:
        if verbose == 1:
            print('\nSetting up bounce ...')
        images = setup_bounce(images, bounce_method)

    # SAVE GIF

    st = time.time()

    if verbose == 1:
        print('\nSaving GIF ...')

    if speed_method == 'choice':
        
        if speed_choice == 'all':
            for i in speed_dict.keys():
                save_gif(outfolder + name + '_' + i + '.gif', images, speed_dict[i], loops)
                print('     ...', i,'GIF saved!')
        else:
            save_gif(outfolder + name + '.gif', images, speed, loops)
            print('     ... GIF saved!')

    else:
        save_gif(outfolder + name + '.gif', images, speed, loops)
        print('     ... GIF saved!')

    et = time.time() - st
    seconds = round(et, 2)
    minutes = round(seconds / 60, 2)
    hours = round(minutes / 60, 2)

    # RESET INPUT FOLDER
    if reset == 1:
        if verbose == 1:
            print('\nResetting input folder...')
        reset_folder(infolder)
        if verbose == 1:
            print('     ... done!')

    # RUN LOG
    
    if speed_choice == 'all':
        ngifs = len(speed_dict.keys())
    else:
        ngifs = 1

    with open(outfolder + 'run.log', 'w') as file:
        file.write(f'\nRUN PARAMETERS LOG\n')
        file.write(f'Name: {name}\n')
        file.write(f'Frames: {len(images)}\n')
        file.write(f'Gifs: {ngifs}\n')
        file.write(f'Speed: {speed}\n')
        file.write(f'Bounce: {bounce}\n')

        file.write(f'\nGIF GENERATION TIME LOG\n')
        file.write(f'Seconds: {seconds}\n')
        file.write(f'Minutes: {minutes}\n')
        file.write(f'Hours: {hours}')

#%% EJECUTAR MODULO PRINCIPAL
            
if __name__ == '__main__':
    __main__()