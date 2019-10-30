# BuiltIns
from time import strftime, strptime, mktime
from struct import unpack

# Custom
from Tools import convert

errCodes = {0x84: 'Descarga de datos',
            0x83: 'Cambio de Hora (Hora Anterior)',
            0x85: 'Cambio de Hora (Hora Actual)',
            0x82: 'Corte de Tensión',
            0x81: 'Vuelta de Tensión',
            -1: 'Anormalidad', }
iNominales = {0x30: 5, 0x31: 200, 0x32: 2, 0x33: 35, 0x34: 500, 0x35: 70, 0x36: 800, 0x37: 1500,
              0x38: 300, 0x39: 100, }
vNominales = {0x30: 110, 0x31: 220, 0x32: 600, 0x33: 7620, 0x34: 19050}
mapaPeriodos = {16: 1, 17: 5, 18: 15, 19: 30}

class Registro:
    def __init__(self, unpackStr, regRaw, regMap):
        self.regRaw = regRaw
        self.unpackStr = unpackStr
        dataRaw = unpack(unpackStr, regRaw)
        for id, attr in enumerate(regMap, start=0):
            setattr(self, attr, dataRaw[id])


class Header(Registro):
    def setData(self):
        try:
            self.fileName = self.fileName.strip(b'\x00').decode('utf-8')
        except AttributeError:
            pass

        self.periodo, self.dStrt, self.mStrt, self.yStrt, self.hStrt, self.minStrt, self.dEnd, self.mEnd, self.yEnd, self.hEnd, self.minEnd = (
            int(x.decode('utf-8')) for x in (
            self.periodo, self.dStrt, self.mStrt, self.yStrt, self.hStrt, self.minStrt, self.dEnd, self.mEnd, self.yEnd,
            self.hEnd, self.minEnd))

        if self.periodo in mapaPeriodos:
            self.periodo = int(mapaPeriodos[self.periodo]/60)
            self.unidad = 'seg'
        else:
            self.unidad = 'min'

        self.timeStampStart = strptime(
            ','.join((str(x) for x in (self.dStrt, self.mStrt, self.yStrt, self.hStrt, self.minStrt))),
            '%d,%m,%y,%H,%M')
        self.timeStampEnd = strptime(
            ','.join((str(x) for x in (self.dEnd, self.mEnd, self.yEnd, self.hEnd, self.minEnd))), '%d,%m,%y,%H,%M')
        self.fechaInicio = strftime('%d/%m/%y', self.timeStampStart)
        self.horaInicio = strftime('%H:%M', self.timeStampStart)
        self.fechaFin = strftime('%d/%m/%y', self.timeStampEnd)
        self.horaFin = strftime('%H:%M', self.timeStampEnd)
        self.vNom = vNominales[self.vNomRaw]
        self.iNom = iNominales[self.iNomRaw]


class RegistroErr(Registro):
    def setData(self):
        self.d, self.m, self.y, self.H, self.M, self.S = map(convert, (self.d, self.m, self.y, self.H, self.M, self.S))
        self.timeStamp = strptime(','.join((str(x) for x in (self.d, self.m, self.y, self.H, self.M, self.S))),
                                  '%d,%m,%y,%H,%M,%S')
        self.timeStampSegundos = mktime(self.timeStamp)
        self.fecha = strftime('%d/%m/%y', self.timeStamp)
        self.hora = strftime('%H:%M:%S', self.timeStamp)
        self.detalle = errCodes[self.codigo]


class EscalasCalibracion(Registro):
    pass


class RegistroDat(Registro):
    anormalidad = ''
    last = False

    def setTimeStamp(self, timeStampTuple):
        self.timeStampTuple = timeStampTuple
        self.timeStampSecs = mktime(timeStampTuple)
        self.fecha = strftime('%d/%m/%y', timeStampTuple)
        self.hora = strftime('%H:%M', timeStampTuple)
