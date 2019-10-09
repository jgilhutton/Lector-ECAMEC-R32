from os import walk
from os.path import isdir
from re import findall

import Series
from Registros import *
from Tools import *

mapaEquipos = {0xB1: Series.Serie04,
               0xDB: Series.Serie12,
               0x9C: Series.Serie1F,
               0x91: Series.Serie20,
               0x9B: Series.Serie0A,
               0x21: Series.Serie15,
               0x01: Series.Serie13,
               0xB3: '\x05', 0xD3: '\x06', 0xF3: '\x06',
               0xCB: '\x0D', 0xEE: '\x0B', 0x60: '\x0F', 0x61: '\x10', 0x63: '\x11', 0x65: '\x12',
               0x02: '\x14', 0x04: '\x16', 0xA0: '\x17', 0xAB: '\x18', 0xAD: '\x19', 0x5B: '\x0C', 0xFF: '\x1A',
               0x82: '\x1B', 0x05: '\x1C', 0x84: '\x1D', 0x45: '\x1E',
               0x92: '\x21', 0x48: '\x1E', 0x49: '\x1E', 0x50: '\x1E', 0x51: '\x1E',
               0x00: '\x00'}


class R32:
    def __init__(self, path, file):
        pathToFile = path + '/' + file
        self.fileName = file
        self.openR32(pathToFile)
        self.getEquipo()

    def openR32(self, pathToFile):
        with open(pathToFile, 'rb') as f:
            self.rawData = f.read()

    def getEquipo(self):
        headers = findall(b'(?<=\xff)[^\xff]{36}(?=\xff)', self.rawData)
        if not headers: headers = findall(b'[^\xff]{21}(?=\x55\x55\x55\xaa)', self.rawData)
        if not headers: pass
        series = [x[8] for x in headers]
        if len(set(series)) > 1:
            print('multiples series detectadas')
            print(series)
        self.serie = series[0]
        self.tipoEquipo = mapaEquipos[self.serie]


class Ecamec:
    def __init__(self, *args, **kwargs):
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])
        if not hasattr(self, 'TV'): self.TV = 1.0
        if not hasattr(self, 'TI'): self.TI = 1.0
        for arg in args:
            if isdir(arg):
                for root, _, files in walk(arg):
                    self.path = root
                    self.archivos = [x for x in files if x.lower().endswith('.r32')]
                    break
            if isfile(arg):
                splittedPath = arg.split('/')
                self.path = '/'.join(splittedPath[:-1])
                self.archivos = [splittedPath[-1], ]
        if not hasattr(self, 'outputDirectory'): self.outputDirectory = self.path

    def procesarR32(self, file):
        self.r32 = R32(self.path, file)
        extractor = self.extraerData()
        for medicion in extractor:
            header = medicion.pop()
            try:
                calibraciones = medicion.pop()
            except IndexError:
                continue
            if hasattr(calibraciones, 'fileName'):
                header.fileName = calibraciones.fileName.strip(b'\x00').decode('utf-8')
            datGenerator = self.genDat(header.fileName)
            errGenerator = self.genErr(header.fileName)
            tStampGenerator = genTimeStamp(header.timeStampStart, header.periodo)
            datGenerator.send(None)
            errGenerator.send(None)
            datGenerator.send(header)
            timeStampPrevia, timeStampInicioCorte, timeStampFinCorte = 0, None, None
            corteEnProgreso, justFinished, justStarted = None, None, None
            for registro in medicion:
                if type(registro) == RegistroErr:
                    errGenerator.send(registro)
                    if registro.codigo == 0x82:
                        corteEnProgreso = True
                        justStarted = True
                        timeStampInicioCorte = registro.timeStampSegundos
                        timeStampFinCorte = timeStampInicioCorte
                    elif registro.codigo == 0x81:
                        corteEnProgreso = False
                        justFinished = True
                        timeStampFinCorte = registro.timeStampSegundos
                elif type(registro) == RegistroDat:
                    registro = self.r32.tipoEquipo.analizarRegistroDat(self.r32.tipoEquipo, registro, calibraciones,
                                                                       self.TV, self.TI, header.periodo)
                    registro.setTimeStamp(tStampGenerator.send(None))
                    if justStarted and (timeStampPrevia < timeStampInicioCorte < registro.timeStampSegundos):
                        registro.anormalidad = 'A'
                        justStarted = False
                    elif justFinished and (timeStampPrevia < timeStampFinCorte < registro.timeStampSegundos):
                        registro.anormalidad = 'A'
                        justFinished = False
                    elif justFinished:
                        while timeStampInicioCorte < timeStampPrevia < registro.timeStampSegundos < timeStampFinCorte:
                            registro.setTimeStamp(tStampGenerator.send(None))
                            registro.anormalidad = 'A'

                    timeStampPrevia = registro.timeStampSegundos
                    datGenerator.send(registro)

    def genDat(self, fileName):
        self.datName = checkFileName(fileName, '.dat')
        outputFile = open(self.outputDirectory + '/' + self.datName, 'w', encoding='utf-8')
        header = (yield)
        headerStr = self.r32.tipoEquipo.headerFormatString.format(header.fileName, '-',
                                                                  header.serie.decode('utf-8') if hasattr(header,
                                                                                                          'serie') else 'ND',
                                                                  header.periodo, 'min', '220', self.TV, '5', self.TI,
                                                                  header.fechaInicio, header.fechaFin,
                                                                  header.horaInicio, header.horaFin)
        outputFile.write(headerStr)
        while True:
            reg = (yield)
            arguments = (reg.fecha, reg.hora) + tuple((getattr(reg, x) for x in self.r32.tipoEquipo.regDatMap)) + (
                reg.anormalidad,)
            regStr = self.r32.tipoEquipo.regFormatString % arguments
            regStr = regStr.replace('.', ',')
            outputFile.write(regStr)

    def genErr(self, fileName):
        self.errName = checkFileName(fileName, '.err')
        outputFile = open(self.outputDirectory + '/' + self.errName, 'w', encoding='utf-8')
        while True:
            reg = (yield)
            if type(reg) != RegistroErr: break
            regStr = self.r32.tipoEquipo.errFormatString.format(reg.fecha, reg.hora, reg.detalle)
            outputFile.write(regStr)
        outputFile.close()

    def extraerData(self):
        registros = []
        try:
            reverse = self.r32.tipoEquipo.reverse
        except:
            return
        for chunkDict in feeder(self.r32.tipoEquipo.regex, self.r32.rawData, reverse=reverse):
            for key in filter(lambda x: chunkDict[x], chunkDict):
                if key == 'calibr':
                    unpackStr = self.r32.tipoEquipo.unpackHeaderCalibracion
                    mapa = self.r32.tipoEquipo.calibrMap
                    data = chunkDict[key]
                    if reverse: data = data[::-1]
                    reg = EscalasCalibracion(unpackStr, data, mapa)
                    registros.append(reg)
                elif key == 'header':
                    unpackStr = self.r32.tipoEquipo.unpackHeaderData
                    mapa = self.r32.tipoEquipo.headerMap
                    data = chunkDict[key]
                    if reverse: data = data[::-1]
                    reg = Header(unpackStr, data, mapa)
                    reg.setData()
                    registros.append(reg)
                    yield registros
                    registros = []
                    break
                elif key == 'err':
                    unpackStr = self.r32.tipoEquipo.unpackErr
                    mapa = self.r32.tipoEquipo.errMap
                    data = chunkDict[key]
                    if reverse: data = data[::-1]
                    reg = RegistroErr(unpackStr, data, mapa)
                    reg.setData()
                    registros.append(reg)
                elif key == 'reg':
                    unpackStr = self.r32.tipoEquipo.unpackReg
                    mapa = self.r32.tipoEquipo.regMap
                    data = chunkDict[key]
                    if reverse: data = data[::-1]
                    reg = RegistroDat(unpackStr, data, mapa)
                    registros.append(reg)


ecamec = Ecamec('C:/Users/Ricardo/Desktop/Infosec/Lector ECAMEC/Extras/Mediciones Nuevas/03 de Agosto/030388O1.R32')
for archivo in ecamec.archivos:
    ecamec.procesarR32(archivo)
