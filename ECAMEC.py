# BuiltIns
from os import walk
from re import findall

# Custom
from Registros import *
from Tools import *
# Monof
from Serie15 import Serie15
from Serie1F import Serie1F
from Serie0A import Serie0A
from Serie04 import Serie04
# Trif
from Serie20 import Serie20
from Serie13 import Serie13

mapaEquipos = {
    # Monofásicas
    0xB1: Serie04,  # OK
    0x9C: Serie1F,  # OK
    0x9B: Serie0A,  # OK
    0x21: Serie15,  # OK

    # Trifasicas
    0xDB: 'Serie12',
    0x5B: 'Serie0C',
    0x91: Serie20,
    0x01: Serie13,
    0x50: '\x1E',  # Serie30,

    # Pendientes
    0xB3: '\x05', 0xD3: '\x06', 0xF3: '\x06',
    0xCB: '\x0D', 0xEE: '\x0B', 0x60: '\x0F', 0x61: '\x10', 0x63: '\x11', 0x65: '\x12',
    0x02: '\x14', 0x04: '\x16', 0xA0: '\x17', 0xAB: '\x18', 0xAD: '\x19', 0xFF: '\x1A',
    0x82: '\x1B', 0x05: '\x1C', 0x84: '\x1D', 0x45: '\x1E',
    0x92: '\x21', 0x48: '\x1E', 0x49: '\x1E', 0x51: '\x1E',
    0x00: '\x00'}


class R32:
    def __init__(self, path, file):
        pathToFile = path + '/' + file
        self.fileName = file

        with open(pathToFile, 'rb') as f:
            self.rawData = f.read()

        self.serie, Serie = self.getSerie()
        if type(Serie) is not str:
            self.tipoEquipo = Serie()
            self.tipoEquipo.qBytesMolestos = self.calcularCantidadDeBytesMolestos()
            self.tipoEquipo.setVariante(self.rawData)
        else:
            self.tipoEquipo = None

    def calcularCantidadDeBytesMolestos(self):
        contador = 0
        for byte in self.rawData[::-1]:
            if byte == 0xff:
                break
            else:
                contador += 1
        cantidad = contador % self.tipoEquipo.largoRegistro
        return cantidad

    def getSerie(self):
        headers = findall(b'(?<=\xff)[^\xff]{36}(?=\xff)', self.rawData)
        if not headers:
            # Try 1612
            return 0x50, ''
        else:
            serie = tuple(set([x[8] for x in headers]))
            if len(serie) > 1:
                print('multiples series detectadas')
                print(serie)
                return 0x50, ''
            return serie[0], mapaEquipos[serie[0]]


class Ecamec:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        if isdir(self.rutaProcesar):
            for root, _, files in walk(self.rutaProcesar):
                self.path = root
                self.archivos = [x for x in files if x.lower().endswith('.r32')]
                break
        elif isfile(self.rutaProcesar):
            splittedPath = self.rutaProcesar.split('/')
            self.path = '/'.join(splittedPath[:-1])
            self.archivos = [splittedPath[-1], ]

    def procesarR32(self, file):
        self.r32 = R32(self.path, file)
        if not self.r32.tipoEquipo:
            return
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
            datGenerator.send(None)
            errGenerator.send(None)
            datGenerator.send(header)
            tStampGenerator = genTimeStamp(header.timeStampStart, header.periodo)
            procesar = lambda r: self.r32.tipoEquipo.analizarRegistroDat(r, calibraciones,
                                                                         self.TV, self.TI, header)
            corte = None
            holdReg = None
            anormalidadErr = None

            for registro in medicion:
                if type(registro) == RegistroErr:
                    anormalidadErr = errGenerator.send(registro)
                    errGenerator.send(None)
                    if registro.codigo == 0x82:
                        timeStampInicioCorte = registro.timeStampSegundos
                        if timeStampInicioCorte < mktime(header.timeStampStart):
                            timeStampInicioCorte = mktime(header.timeStampStart)
                        cd = {'inicio': timeStampInicioCorte, 'enProgreso': True, 'justStarted': True,
                              'justFinished': None}
                        corte = SimpleNamespace(**cd)
                    elif registro.codigo == 0x81:
                        timeStampFinCorte = registro.timeStampSegundos
                        if timeStampFinCorte < mktime(header.timeStampStart):
                            timeStampFinCorte = mktime(header.timeStampStart)
                        if corte:
                            corte.fin = timeStampFinCorte
                            corte.enProgreso = False
                            corte.justStarted = False
                            corte.justFinished = True
                    elif registro.codigo == 0x85:
                        tStampGenerator.close()
                        header.resetInicio(registro.timeStamp)
                        tStampGenerator = genTimeStamp(header.timeStampStart, header.periodo)

                elif type(registro) == RegistroDat:
                    if anormalidadErr:
                        registro.anormalidad = 'A'
                        anormalidadErr = False
                    if corte:
                        if corte.justStarted:
                            if not holdReg:
                                registro.setTimeStamp(tStampGenerator.send(None))
                            else:
                                registro.setTimeStamp(holdReg.timeStampTuple)
                            if not registro.last:
                                holdReg = registro
                                continue
                            else:
                                if registro.timeStampSecs > corte.inicio:
                                    registro.anormalidad = 'A'
                        elif corte.justFinished:
                            if holdReg and holdReg.timeStampSecs > corte.fin:
                                registro.setTimeStamp(holdReg.timeStampTuple)
                                holdReg = None
                                registro.anormalidad = 'A'
                            else:
                                if not holdReg:
                                    tStampTuple = tStampGenerator.send(None)
                                    tStamp = mktime(tStampTuple)
                                else:
                                    tStamp = holdReg.timeStampSecs
                                    tStampTuple = holdReg.timeStampTuple
                                    holdReg.anormalidad = 'A'
                                while tStamp < corte.fin:
                                    tStampTuple = tStampGenerator.send(None)
                                    tStamp = mktime(tStampTuple)
                                registro.setTimeStamp(tStampTuple)
                                registro.anormalidad = 'A'
                            corte = None
                    elif not corte:
                        registro.setTimeStamp(tStampGenerator.send(None))
                    if holdReg:
                        holdReg = procesar(holdReg)
                        datGenerator.send(holdReg)
                        holdReg = None
                    registro = procesar(registro)
                    datGenerator.send(registro)

    def genDat(self, fileName):
        datName = checkFileName(fileName, '.dat')
        outputFile = open(self.outputDirectory + '/' + datName, 'w', encoding='latin1')
        header = yield
        headerStr = self.r32.tipoEquipo.headerFormatString.format(header.fileName, '-',
                                                                  header.serie.decode('latin1') if hasattr(header,
                                                                                                           'serie') else 'ND',
                                                                  header.periodo, header.unidad, header.vNom,
                                                                  '{0:.2f}'.format(float(self.TV)).replace('.', ','),
                                                                  header.iNom,
                                                                  '{0:.2f}'.format(float(self.TI)).replace('.', ','),
                                                                  header.fechaInicio, header.fechaFin,
                                                                  header.horaInicio, header.horaFin)
        outputFile.write(headerStr)
        while True:
            reg = yield
            arguments = (reg.fecha, reg.hora) + tuple((getattr(reg, x) for x in self.r32.tipoEquipo.regDatMap)) + (
                reg.anormalidad,)
            regStr = self.r32.tipoEquipo.regFormatString % arguments
            regStr = regStr.replace('.', ',')
            outputFile.write(regStr)

    def genErr(self, fileName):
        sinCambioDeHoraAnterior = True
        first = True
        primerCambioDeHora = None
        errName = checkFileName(fileName, '.err')
        outputFile = open(self.outputDirectory + '/' + errName, 'w', encoding='latin1')
        while True:
            reg = yield
            if type(reg) != RegistroErr:
                break
            if reg.codigo == 0x85:
                if primerCambioDeHora:
                    primerCambioDeHora = False
                    sinCambioDeHoraAnterior = True
                elif sinCambioDeHoraAnterior:
                    reg.detalle = 'Anormalidad'
                else:
                    sinCambioDeHoraAnterior = True
            elif reg.codigo == 0x83:
                if not primerCambioDeHora and first:
                    primerCambioDeHora = True
                    first = False
                sinCambioDeHoraAnterior = False
            regStr = self.r32.tipoEquipo.errFormatString.format(reg.fecha, reg.hora, reg.detalle)
            outputFile.write(regStr)
            yield True if reg.detalle == 'Anormalidad' else False
        outputFile.close()

    def extraerData(self):
        calibre = None
        header = None
        registros = []
        calibrFalso = None
        try:
            reverse = self.r32.tipoEquipo.reverse
        except AttributeError:
            return

        for chunk in feeder(self.r32.tipoEquipo.regex, self.r32.rawData, reverse=reverse):
            if chunk.calibr:
                unpackStr = self.r32.tipoEquipo.unpackHeaderCalibracion
                mapa = self.r32.tipoEquipo.calibrMap
                data = chunk.calibr
                if reverse:
                    data = data[::-1]
                reg = EscalasCalibracion(unpackStr, data, mapa)
                calibre = reg
                if calibrFalso:
                    registros.append(calibre)
                    registros.append(header)
                    yield registros
                    registros = []
                    calibre = None
                    header = None
                    continue
            if hasattr(chunk, 'header') and chunk.header:
                unpackStr = self.r32.tipoEquipo.unpackHeaderData
                mapa = self.r32.tipoEquipo.headerMap
                data = chunk.header
                if reverse: data = data[::-1]
                reg = Header(unpackStr, data, mapa)
                header = reg
                reg.setData()
                registros.append(calibre)
                registros.append(header)
                registros = setLast(registros)
                yield registros
                registros = []
                calibre = None
                header = None
            if hasattr(chunk, 'headerOk') and chunk.headerOk:
                unpackStr = self.r32.tipoEquipo.unpackHeaderData
                mapa = self.r32.tipoEquipo.headerMap
                data = chunk.headerOk
                if reverse: data = data[::-1]
                reg = Header(unpackStr, data, mapa)
                header = reg
                reg.setData()
                registros.append(reg)
                registros = setLast(registros)
                calibrFalso = True
                continue
            elif chunk.err:  # and not calibrFalso:
                unpackStr = self.r32.tipoEquipo.unpackErr
                mapa = self.r32.tipoEquipo.errMap
                data = chunk.err
                if reverse: data = data[::-1]
                reg = RegistroErr(unpackStr, data, mapa)
                reg.setData()
                registros.append(reg)
            elif chunk.reg:
                unpackStr = self.r32.tipoEquipo.unpackReg
                mapa = self.r32.tipoEquipo.regMap
                data = chunk.reg
                if reverse: data = data[::-1]
                reg = RegistroDat(unpackStr, data, mapa)
                registros.append(reg)


if __name__ == '__main__':
    # args = argParse()
    ruta = './Extras/Barras/'
    file = 'M34591234.R32'
    args = {'rutaProcesar': ruta + file, 'outputDirectory': ruta, 'TV': 1, 'TI': 1,
            'verboseLevel': 0}
    ecamec = Ecamec(**args)
    for archivo in ecamec.archivos:
        print(archivo)
        ecamec.procesarR32(archivo)
