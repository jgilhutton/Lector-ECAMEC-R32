from Medicion import Medicion
from sys import argv
from os import walk

def printHelp(error = None):
    help = """
    Modo de uso:    python r32.py [-d Directorio]|[-f Archivo] [Opcionales]
    -d  Directorio con archivos .R32
    -f  Archivo .R32
    Opcionales:
        -o  Directorio donde se guardan los archivos generados
            Valor por defecto: Directorio de los archivos R32
        -tv Factor de tensión   Valor por defecto: 1
        -ti Factor de corriente Valor por defecto: 1
        -v  Muestra más información en la pantalla durante el
            procesamiento. Valor por defect: Falso
        -vv Igual que -v pero con información de depuración

    Los archivos pueden tener cualquier extensión.
    Lo que importa es la información que está dentro de ellos.
    Un archivo válido puede ser MEDICION.TXT, si se desea

    Ejemplos:
    python r32.py -d "C:\Mediciones" -o "C:\Mediciones Procesadas"
    python r32.py -f MEDICION.R32 -tv 35 -ti 15.5

    """
    if error:print('\nERROR: ',error)
    print(help)
    exit()

file,folder,oFolder = None,None,None

if '-d' in argv and '-f' in argv:
    printHelp('-d y -f no pueden estar juntos')
if '-d' in argv:
    folder = argv[argv.index('-d')+1]
elif '-f' in argv:
    file = argv[argv.index('-f')+1]
else: printHelp('Debe proporcionar los argumentos necesarios')

if file:
    folder = list(filter(lambda x:x,['\\'.join(file.split('\\')[:-1]),'/'.join(file.split('/')[:-1])]))
    if not folder: folder = '.'
    else: folder = folder[0]
    files = [file.split('\\')[-1].split('/')[-1]]
else:
    for root, directory, file in walk(folder):
        files = [x for x in file if x.lower().endswith('.r32')]
    if not files:
        printHelp('\nNo se encontraron archivos en el directorio.\n')


oFolder = argv[argv.index('-o')+1] if '-o' in argv else folder
try:    TV = float(argv[argv.index('-tv')+1]) if '-tv' in argv else 1.0
except: printHelp('TV debe ser un número (flotante o entero)')
try:    TI = float(argv[argv.index('-ti')+1]) if '-ti' in argv else 1.0
except: printHelp('TI debe ser un número (flotante o entero)')
verbose = True if '-v' in argv else False
debug = True if '-vv' in argv else False
if debug: verbose = True
        
for file in files:
    try:
        medicion = Medicion(file,folder,oFolder,TV,TI,verbose,debug)
        if medicion.serie:
            try:
                medicion.analizarR32()
            except Exception as e:
                print('ERROR:',e,'en',file)
    except TypeError as e:
        print(e)
        continue
