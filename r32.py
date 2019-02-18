<<<<<<< HEAD
import struct
from statistics import variance
import matplotlib.pyplot as plt
from math import ceil
from re import search
from time import mktime,strptime,localtime,strftime

dataSeries = {
            'Vieja':{
                        1:{
                            'largoRegistro':10,
                            'largoErr':7,
                            'largoHeaderCalibracion':10,
                            'byteSeparador':255,
                            'factorTension':lambda x: x*0.07087628543376923,
                            'getFlicker':lambda x,y,z: ((x*220*.02)/y)*(100/z),
                            'getThd':lambda u,v,w,x,y,z: (100/u)*(abs(v-((w/x)*y)))*18/z,
                            'unpackString':'>HHHHH',
                            'unpackErr':'>BBBBBBB',
                            'unpackHeaderCalibracion':'HHHHH',
                            'unpackHeader':'>8sx2s2s2s2s2s2s3x2s2s2s2s2sxx',
                            'headerMap':dict([reversed(x) for x in enumerate(['filename','periodo','diaInicio','mesInicio','añoInicio','horaInicio','minInicio','diaFin','mesFin','añoFin','horaFin','minFin'])]),
                            'regIndexes':{'flicker':0,'thd':1,'Vmin':2,'Vmax':3,'V':4},},
                        3:{
                            'largoRegistro':42,
                            'largoErr':7,
                            'byteSeparador':255,
                            'factorTension':lambda x: x*0.008392460165229354,
                            'factorCorriente':lambda x: x*0.005086235518683759,
                            'factorPotencia':lambda x,y: y*x,
                            # 'packString':'>HHHHHHHH HxHHHHH HxHHHHH',
                            'packString':'>HB HBH H HHH HBH H HHH HBH H HHH',
                            
                            # I1 v1min v1max v1 },
                            },
                    },
            '1104':{
                        1:{
                            'largoRegistro':19,
                            'largoErr':7,
                            'byteSeparador':255,
                            'factorTension':0.13422811996114395,
                            'factorFlicker':0.005705854589941206,
                            'factorThd':0.0014804170914708213,
                            'packString':'>HHxxxxxxxxxHHH',
                            'packHeader':'>8sx2s2s2s2s2s2s3x2s2s2s2s2sxx',
                            'headerMap':dict([reversed(x) for x in enumerate(['filename','periodo','diaInicio','mesInicio','añoInicio','horaInicio','minInicio','diaFin','mesFin','añoFin','horaFin','minFin'])]),},
                        3:{
                            'largoRegistro':54,
                            'largoErr':7,
                            'byteSeparador':255,
                            'factorTension':0.008392393539741385,
                            'factorCorriente':0.0050874767931571524,
                            'factorFlicker':0.0000037580872785202386,
                            'factorThd':0.000490629335175061,
                            'packString':'>HHxxxxxxxxHHHHxxxxxxxxxHHHHxxxxxxxxxHHHH'},
                    },
            '1605':{
                        1:{
                            'largoRegistro':10,
                            'largoErr':7,
                            'byteSeparador':255,
                            'factorTension':0,
                            'factorFlicker':0.0,
                            'factorThd':0.0,
                            'packString':'>HHHHH',
                            'packHeader':'',
                            'headerMap':dict([reversed(x) for x in enumerate(['filename','periodo','diaInicio','mesInicio','añoInicio','horaInicio','minInicio','diaFin','mesFin','añoFin','horaFin','minFin'])]),},
                        3:{
                            'largoRegistro':54,
                            'largoErr':7,
                            'byteSeparador':255,
                            'factorTension':0.00839227754373019,
                            'factorCorriente':0.005088869461694482,
                            'factorFlicker':0.0,
                            'factorThd':0.0,
                            'packString':'>HHHHHHHHHHxHHHHHHHHxBBBBBBBBHHHH'},},
            '1612':{},}
errCodes = {84:'Descarga de datos',
            83:'Cambio de Hora (Hora Anterior)',
            85:'Cambio de Hora (Hora Actual)',
            82:'Corte de Tensión',
            81:'Vuelta de Tensión',}

def feeder(data,largoRegistro,largoErr,byteSeparador):
    returnData = data[:]
    puntero = len(data)-1
    hold = puntero+1
    OPEN = False

    data = data[::-1]
    for byte in data:
        size = hold-puntero-1
        if OPEN and byte != byteSeparador: pass
        elif OPEN and byte == byteSeparador:
            if size > largoErr:
                yield ('header',returnData[puntero+1:hold])
            elif size == largoErr:
                yield ('err',returnData[puntero+1:hold])
            OPEN = False
            hold = puntero
        elif not OPEN and byte != byteSeparador:
            if size == largoRegistro:
                yield ('reg',returnData[puntero+1:hold])
                hold = puntero+1
        elif not OPEN and byte == byteSeparador:
            if size == largoRegistro:
                yield ('reg',returnData[puntero+1:hold])
                hold = puntero+1
            hold = puntero
            OPEN = True
        
        puntero -= 1

def inRange(listaValores,*arg):
    flag = False
    for range in arg:
        for numero in listaValores:
            if numero > range[0] and numero < range[1]:
                flag = True
            else:
                flag = False
                break
                
        if not flag: return False
        else: continue
    if flag: return True

class Medicion():
    def __init__(self,fileName):
        self.r32 = self.openR32(fileName)
        self.serie = self.getSerie()
        self.headerCalibracion = self.calibraciones()
        [self.calibrTension,
        self.calibrTensionNo220,
        self.calibrThd,
        self.calibrResiduo,
        self.calibrFlicker] = struct.unpack(self.serie['unpackHeaderCalibracion'],self.headerCalibracion)
    
    registrosProcesados = []
    errs = []
    regs = []
    raws = []
    inicio = None
    final = None
    periodo = None
    rangosCortes = []

    def openR32(self,fileName):
        with open(fileName,'rb') as f:
            return f.read()

    def getSerie(self):
        return dataSeries['Vieja'][1]

    def analizarR32(self):
        index = 0
        serie = self.serie
        for index,[tipo,data] in enumerate(feeder(self.r32,serie['largoRegistro'],serie['largoErr'],serie['byteSeparador'])):
            if tipo == 'header':
                self.header = data
                self.procesar()
                self.errs,self.regs = [],[]
            if tipo == 'err':
                self.errs.append([index,data])
            if tipo == 'reg':
                self.regs.append([index,data])

    def calibraciones(self):
        puntero = 0
        hold = 0
        OPEN = False
        for byte in self.r32:
            size = puntero-hold
            if OPEN and byte == self.serie['byteSeparador']:
                OPEN = False
                hold = puntero
                pass
            elif not OPEN and byte != self.serie['byteSeparador']:
                if size == self.serie['largoHeaderCalibracion'] and  self.r32[puntero+1] == self.serie['byteSeparador']:
                    return  self.r32[hold+1:puntero+1]
            elif not OPEN and byte == self.serie['byteSeparador']:
                OPEN = True
                hold = puntero
            puntero += 1

    def timeStampGen(self,startTime):
        cuartosDeHora,resto = divmod(mktime(startTime),(15*60))
        stampSeconds = cuartosDeHora*(15*60)
        while True:
            stampSeconds += (15*60)
            yield localtime(stampSeconds)
    
    def procesarErrs(self):
        corteInicio = None
        corteFin = None
        lastTimeStamp = None
        errDump = open(self.headerData['filename']+'.err','w')
        errDump.write('\t'.join([strftime('%d/%m/%y\t%H:%M:%S',self.inicio),'Comienzo del Registro.','\n']))
        for index,err in self.errs:
            err = struct.unpack(self.serie['unpackErr'],err)
            err = [str(hex(i)) for i in err]
            err = [search('(?<=x).+',x).group().zfill(2) for x in err]
            timeSamp = strptime(''.join(err[1:]),'%S%M%H%d%m%y')
            if timeSamp == lastTimeStamp: continue
            errDump.write('\t'.join([strftime('%d/%m/%y\t%H:%M:%S',timeSamp),errCodes[int(err[0])],'\n']))
            codigo = int(err[0])
            if codigo == 82: corteInicio = timeSamp
            if codigo == 81:
                corteFin = timeSamp
                self.rangosCortes.append((mktime(corteInicio),mktime(corteFin)))
                corteFin = None
                corteInicio = None
            lastTimeStamp = timeSamp
        print(self.rangosCortes)


    def procesar(self):
        serie = self.serie
        header = struct.unpack(serie['unpackHeader'],self.header)
        self.headerData = dict(zip(list(serie['headerMap'].keys()),[search('(?<=\').+(?=\')',str(header[serie['headerMap'][x]])).group() for x in serie['headerMap']]))
        headerData = self.headerData

        self.inicio = strptime(' '.join([headerData['diaInicio'],headerData['mesInicio'],headerData['añoInicio'],headerData['horaInicio'],headerData['minInicio']]),'%d %m %y %H %M')
        self.final = strptime(' '.join([headerData['diaFin'],headerData['mesFin'],headerData['añoFin'],headerData['horaFin'],headerData['minFin']]),'%d %m %y %H %M')
        self.periodo = int(self.headerData['periodo'])

        self.procesarErrs()
        for index,reg in reversed(self.regs):
            a = struct.unpack(serie['unpackString'],reg)
            VRaw = a[serie['regIndexes']['V']]
            VmaxRaw = a[serie['regIndexes']['Vmax']]
            VminRaw = a[serie['regIndexes']['Vmin']]
            thdRaw = a[serie['regIndexes']['thd']]
            flickerRaw = a[serie['regIndexes']['flicker']]

            V = serie['factorTension'](VRaw)
            Vmax = serie['factorTension'](VmaxRaw)
            Vmin = serie['factorTension'](VminRaw)

            thd = serie['getThd'](V,thdRaw,self.calibrResiduo,self.calibrTension,VRaw,self.calibrThd)
            if thd>10: thd = 10.0
            flicker = serie['getFlicker'](flickerRaw,self.calibrFlicker,V)
            if flicker>2: flicker = 2.0
            
            self.registrosProcesados.append((V,Vmax,Vmin,thd,flicker))
            self.raws.append(a)


# file = 'Serie vieja T/ori.R32'
# fileDat = 'Serie vieja T/ori.dat'
file = 'Serie vieja M/mini.R32'
fileDat = 'Serie vieja M/mini.dat'

medicion = Medicion(file)
medicion.analizarR32()
# def getDatData(col=None):
#     global dataDat
#     with open(fileDat,'r') as f:
#         F = f.readlines()
#         if col:
#             dataDat = [y.split('\t')[col] for y in F[9:]]
#         else:
#             dataDat = [y.split('\t') for y in F[9:]]
#             dataDat = [[x[2],x[3],x[4],x[5],x[6]] for x in [y for y in dataDat] if float(x[2].replace(',','.'))]




    
    # getDatData()
    # # chunk = 0
    # offset = 1
    # for x,y,z in list(zip(dataDat,raws[offset:],registrosProcesados[offset:])):
    #     input([x,[round(i,3) for i in z],y])#[::-1])


# l = [[x,y] for x,y in list(zip(dataDat[:600],ps[offset:][:600]))]
# xs = [x for x,y in l if x<0.5][chunk:200+chunk]
# ys = [y for x,y in l if x<0.5][chunk:200+chunk]
# # ys = [y*c for x,y in l if x>0.4]
# plt.scatter(xs,ys,c='red',s=1)
# plt.scatter(xs,xs,c='black',s=1)
=======
import struct
from statistics import variance
import matplotlib.pyplot as plt
from math import ceil
from re import search
from time import mktime,strptime,localtime,strftime

dataSeries = {
            'Vieja':{
                        1:{
                            'largoRegistro':10,
                            'largoErr':7,
                            'largoHeaderCalibracion':10,
                            'byteSeparador':255,
                            'factorTension':lambda x: x*0.07087628543376923,
                            'getFlicker':lambda x,y,z: ((x*220*.02)/y)*(100/z),
                            'getThd':lambda u,v,w,x,y,z: (100/u)*(abs(v-((w/x)*y)))*18/z,
                            'unpackString':'>HHHHH',
                            'unpackErr':'>BBBBBBB',
                            'unpackHeaderCalibracion':'HHHHH',
                            'unpackHeader':'>8sx2s2s2s2s2s2s3x2s2s2s2s2sxx',
                            'headerMap':dict([reversed(x) for x in enumerate(['filename','periodo','diaInicio','mesInicio','añoInicio','horaInicio','minInicio','diaFin','mesFin','añoFin','horaFin','minFin'])]),
                            'regIndexes':{'flicker':0,'thd':1,'Vmin':2,'Vmax':3,'V':4},},
                        3:{
                            'largoRegistro':42,
                            'largoErr':7,
                            'byteSeparador':255,
                            'factorTension':lambda x: x*0.008392460165229354,
                            'factorCorriente':lambda x: x*0.005086235518683759,
                            'factorPotencia':lambda x,y: y*x,
                            # 'packString':'>HHHHHHHH HxHHHHH HxHHHHH',
                            'packString':'>HB HBH H HHH HBH H HHH HBH H HHH',
                            
                            # I1 v1min v1max v1 },
                            },
                    },
            '1104':{
                        1:{
                            'largoRegistro':19,
                            'largoErr':7,
                            'byteSeparador':255,
                            'factorTension':0.13422811996114395,
                            'factorFlicker':0.005705854589941206,
                            'factorThd':0.0014804170914708213,
                            'packString':'>HHxxxxxxxxxHHH',
                            'packHeader':'>8sx2s2s2s2s2s2s3x2s2s2s2s2sxx',
                            'headerMap':dict([reversed(x) for x in enumerate(['filename','periodo','diaInicio','mesInicio','añoInicio','horaInicio','minInicio','diaFin','mesFin','añoFin','horaFin','minFin'])]),},
                        3:{
                            'largoRegistro':54,
                            'largoErr':7,
                            'byteSeparador':255,
                            'factorTension':0.008392393539741385,
                            'factorCorriente':0.0050874767931571524,
                            'factorFlicker':0.0000037580872785202386,
                            'factorThd':0.000490629335175061,
                            'packString':'>HHxxxxxxxxHHHHxxxxxxxxxHHHHxxxxxxxxxHHHH'},
                    },
            '1605':{
                        1:{
                            'largoRegistro':10,
                            'largoErr':7,
                            'byteSeparador':255,
                            'factorTension':0,
                            'factorFlicker':0.0,
                            'factorThd':0.0,
                            'packString':'>HHHHH',
                            'packHeader':'',
                            'headerMap':dict([reversed(x) for x in enumerate(['filename','periodo','diaInicio','mesInicio','añoInicio','horaInicio','minInicio','diaFin','mesFin','añoFin','horaFin','minFin'])]),},
                        3:{
                            'largoRegistro':54,
                            'largoErr':7,
                            'byteSeparador':255,
                            'factorTension':0.00839227754373019,
                            'factorCorriente':0.005088869461694482,
                            'factorFlicker':0.0,
                            'factorThd':0.0,
                            'packString':'>HHHHHHHHHHxHHHHHHHHxBBBBBBBBHHHH'},},
            '1612':{},}
errCodes = {84:'Descarga de datos',
            83:'Cambio de Hora (Hora Anterior)',
            85:'Cambio de Hora (Hora Actual)',
            82:'Corte de Tensión',
            81:'Vuelta de Tensión',}

def feeder(data,largoRegistro,largoErr,byteSeparador):
    returnData = data[:]
    puntero = len(data)-1
    hold = puntero+1
    OPEN = False

    data = data[::-1]
    for byte in data:
        size = hold-puntero-1
        if OPEN and byte != byteSeparador: pass
        elif OPEN and byte == byteSeparador:
            if size > largoErr:
                yield ('header',returnData[puntero+1:hold])
            elif size == largoErr:
                yield ('err',returnData[puntero+1:hold])
            OPEN = False
            hold = puntero
        elif not OPEN and byte != byteSeparador:
            if size == largoRegistro:
                yield ('reg',returnData[puntero+1:hold])
                hold = puntero+1
        elif not OPEN and byte == byteSeparador:
            if size == largoRegistro:
                yield ('reg',returnData[puntero+1:hold])
                hold = puntero+1
            hold = puntero
            OPEN = True
        
        puntero -= 1

class Medicion():
    def __init__(self,fileName):
        self.r32 = self.openR32(fileName)
        self.serie = self.getSerie()
        self.headerCalibracion = self.calibraciones()
        [self.calibrTension,
        self.calibrTensionNo220,
        self.calibrThd,
        self.calibrResiduo,
        self.calibrFlicker] = struct.unpack(self.serie['unpackHeaderCalibracion'],self.headerCalibracion)
    
    registrosProcesados = []
    errs = []
    regs = []
    raws = []
    inicio = None
    final = None
    periodo = None
    rangosCortes = []

    def openR32(self,fileName):
        with open(fileName,'rb') as f:
            return f.read()

    def getSerie(self):
        return dataSeries['Vieja'][1]

    def analizarR32(self):
        serie = self.serie
        for tipo,data in feeder(self.r32,serie['largoRegistro'],serie['largoErr'],serie['byteSeparador']):
            if tipo == 'header':
                self.header = data
                self.procesar()
                self.errs,self.regs = [],[]
            if tipo == 'err':
                self.errs.append(data)
            if tipo == 'reg':
                self.regs.append(data)

    def calibraciones(self):
        puntero = 0
        hold = 0
        OPEN = False
        for byte in self.r32:
            size = puntero-hold
            if OPEN and byte == self.serie['byteSeparador']:
                OPEN = False
                hold = puntero
                pass
            elif not OPEN and byte != self.serie['byteSeparador']:
                if size == self.serie['largoHeaderCalibracion'] and  self.r32[puntero+1] == self.serie['byteSeparador']:
                    return  self.r32[hold+1:puntero+1]
            elif not OPEN and byte == self.serie['byteSeparador']:
                OPEN = True
                hold = puntero
            puntero += 1

    def timeStampGen(self,startTime):
        cuartosDeHora,resto = divmod(mktime(startTime),(15*60))
        stampSeconds = cuartosDeHora*(15*60)
        while True:
            stampSeconds += (15*60)
            yield localtime(stampSeconds)
    
    def procesarErrs(self):
        corteInicio = None
        corteFin = None
        lastTimeStamp = None
        errDump = open(self.headerData['filename']+'.err','w')
        errDump.write('\t'.join([strftime('%d/%m/%y\t%H:%M:%S',self.inicio),'Comienzo del Registro.','\n']))
        for err in self.errs:
            err = struct.unpack(self.serie['unpackErr'],err)
            err = [str(hex(i)) for i in err]
            err = [search('(?<=x).+',x).group().zfill(2) for x in err]
            timeSamp = strptime(''.join(err[1:]),'%S%M%H%d%m%y')
            if timeSamp == lastTimeStamp: continue
            errDump.write('\t'.join([strftime('%d/%m/%y\t%H:%M:%S',timeSamp),errCodes[int(err[0])],'\n']))
            codigo = int(err[0])
            if codigo == 82: corteInicio = timeSamp
            if codigo == 81:
                corteFin = timeSamp
                self.rangosCortes.append((mktime(corteInicio),mktime(corteFin)))
                corteFin = None
                corteInicio = None
            lastTimeStamp = timeSamp
        print(self.rangosCortes)


    def procesar(self):
        serie = self.serie
        header = struct.unpack(serie['unpackHeader'],self.header)
        self.headerData = dict(zip(list(serie['headerMap'].keys()),[search('(?<=\').+(?=\')',str(header[serie['headerMap'][x]])).group() for x in serie['headerMap']]))
        headerData = self.headerData

        self.inicio = strptime(' '.join([headerData['diaInicio'],headerData['mesInicio'],headerData['añoInicio'],headerData['horaInicio'],headerData['minInicio']]),'%d %m %y %H %M')
        self.final = strptime(' '.join([headerData['diaFin'],headerData['mesFin'],headerData['añoFin'],headerData['horaFin'],headerData['minFin']]),'%d %m %y %H %M')
        self.periodo = int(self.headerData['periodo'])

        self.procesarErrs()
        for reg in reversed(self.regs):
            a = struct.unpack(serie['unpackString'],reg)
            VRaw = a[serie['regIndexes']['V']]
            VmaxRaw = a[serie['regIndexes']['Vmax']]
            VminRaw = a[serie['regIndexes']['Vmin']]
            thdRaw = a[serie['regIndexes']['thd']]
            flickerRaw = a[serie['regIndexes']['flicker']]

            V = serie['factorTension'](VRaw)
            Vmax = serie['factorTension'](VmaxRaw)
            Vmin = serie['factorTension'](VminRaw)

            thd = serie['getThd'](V,thdRaw,self.calibrResiduo,self.calibrTension,VRaw,self.calibrThd)
            if thd>10: thd = 10.0
            flicker = serie['getFlicker'](flickerRaw,self.calibrFlicker,V)
            if flicker>2: flicker = 2.0
            
            self.registrosProcesados.append((V,Vmax,Vmin,thd,flicker))
            self.raws.append(a)


# file = 'Serie vieja T/ori.R32'
# fileDat = 'Serie vieja T/ori.dat'
file = 'Serie vieja M/mini.R32'
fileDat = 'Serie vieja M/mini.dat'

medicion = Medicion(file)
medicion.analizarR32()
# def getDatData(col=None):
#     global dataDat
#     with open(fileDat,'r') as f:
#         F = f.readlines()
#         if col:
#             dataDat = [y.split('\t')[col] for y in F[9:]]
#         else:
#             dataDat = [y.split('\t') for y in F[9:]]
#             dataDat = [[x[2],x[3],x[4],x[5],x[6]] for x in [y for y in dataDat] if float(x[2].replace(',','.'))]




    
    # getDatData()
    # # chunk = 0
    # offset = 1
    # for x,y,z in list(zip(dataDat,raws[offset:],registrosProcesados[offset:])):
    #     input([x,[round(i,3) for i in z],y])#[::-1])


# l = [[x,y] for x,y in list(zip(dataDat[:600],ps[offset:][:600]))]
# xs = [x for x,y in l if x<0.5][chunk:200+chunk]
# ys = [y for x,y in l if x<0.5][chunk:200+chunk]
# # ys = [y*c for x,y in l if x>0.4]
# plt.scatter(xs,ys,c='red',s=1)
# plt.scatter(xs,xs,c='black',s=1)
>>>>>>> 18427e99bbbd7faab74e10a650abe819d0f2b9a3
# plt.show()