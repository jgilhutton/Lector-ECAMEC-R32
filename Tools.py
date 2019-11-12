from time import mktime, localtime
from re import finditer
from os.path import isfile, isdir
from types import SimpleNamespace
from sys import argv


def printHelp(*args):
    help = """
    Modo de uso:    python ECAMEC.py -i [Directorio]|[Archivo] [Opcionales]
    Opcionales:
        -o  Directorio donde se guardan los archivos generados
            Valor por defecto: Directorio de los archivos R32
        -tv Factor de tensión   Valor por defecto: 1
        -ti Factor de corriente Valor por defecto: 1
        -v  Muestra más información en la pantalla durante el
            procesamiento.
        -vv Muestra aun más información
        -h  Muestra este mensaje

    Ejemplos:
    python ECAMEC.py -i "C:\Mediciones" -o "C:\Mediciones Procesadas"
    python ECAMEC.py -i MEDICION.R32 -tv 35 -ti 15.5

    """
    if args: print('\nERROR: ', ' '.join(args))
    print(help)
    exit()


def argParse():
    if len(argv) == 1:
        printHelp('Debe proporcionar los argumentos necesarios.')
    else:
        if '-h' in argv:
            printHelp()
        rutaProcesar = argv[argv.index('-i') + 1] if '-i' in argv else './'
        if not (isfile(rutaProcesar) or isdir(rutaProcesar)):
            printHelp('No se encontró el directorio o archivo ingresado.')
        outputDirectory = argv[argv.index('-o') + 1] if '-o' in argv else rutaProcesar if rutaProcesar != './' else './'
        if not isdir(outputDirectory):
            printHelp('No se encontró el directorio de salida "{}"'.format(outputDirectory))
        try:
            TV = float(argv[argv.index('-tv') + 1]) if '-tv' in argv else 1.0
        except ValueError:
            printHelp('TV debe ser un número (flotante o entero)')
        try:
            TI = float(argv[argv.index('-ti') + 1]) if '-ti' in argv else 1.0
        except ValueError:
            printHelp('TI debe ser un número (flotante o entero)')
        for arg in argv:
            if arg.startswith('-v'):
                verboseLevel = arg.count('v')
                break
        else: verboseLevel = 0

        return {'rutaProcesar': rutaProcesar.replace('\\','/'), 'outputDirectory': outputDirectory.replace('\\','/'), 'TV': TV, 'TI': TI,
                'verboseLevel': verboseLevel}


def genTimeStamp(startTime, periodo):
    stampSeconds = mktime(startTime) - mktime(startTime) % (periodo * 60)
    while True:
        stampSeconds += (periodo * 60)
        yield localtime(stampSeconds)


def feeder(regex, data, reverse=False):
    if reverse: data = data[::-1]
    regex = bytes(regex, encoding='latin1')
    for match in finditer(regex, data):
        yield SimpleNamespace(**match.groupdict())


def limitar(value, minimo, maximo):
    if minimo <= value <= maximo:
        return value
    elif value < minimo:
        return minimo
    else:
        return maximo


def inRange(value, boundaries):
    return boundaries[0] < value < boundaries[1]


def checkFileName(fileName, ext):
    return fileName + ext  # Temp
    if not isfile(''.join((self.path, '/', fileName, ext))): return fileName + ext
    ext = ext[:-1] + '%d'
    c = 0
    while True:
        if isfile(''.join((self.path, '/', fileName, ext % c))):
            c += 1
            continue
        break
    return fileName + ext % c


def convert(valor):
    if type(valor) is tuple:
        valor,tipo = valor
    else:
        tipo = 'default'
    try:
        valorConvertido = int(str(hex(valor))[2:])
    except ValueError:
        if tipo == 'año':
            mapa = {'c':20,'d':30}
            valor = str(hex(valor))
            valor = mapa[valor[2]]+int(valor[3],16)
        elif tipo == 'min':
            valor = str(hex(valor))
            valor = int(valor[2])*10 + int(valor[3], 16)
        valorConvertido = int(str(hex(valor))[2:],16)
    return valorConvertido


def setLast(medicion):
    from Registros import RegistroDat
    for reg in medicion[::-1]:
        if type(reg) == RegistroDat:
            reg.last = True
            break
    return medicion
