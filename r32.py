#commit prueba
import struct
from statistics import variance
import matplotlib.pyplot as plt
from math import ceil
from re import search
from time import asctime,mktime,strptime,localtime,strftime

dataSeries = {
            'Vieja':{
                        1:{
                            'largoRegistro':10,
                            'headerDat':'Equipo Nro:\t{filename}\t\tCódigo de Cliente: \tID. Subestación:\t        \nNumero de Serie:\tND\tPeriodo: {periodo} {Utiempo}.\nTensión:     \t{tension} V\t\tFactor de Corrección: {TV}\nCorriente:\t{corriente} Amp\t\tFactor de Corrección: {TI}\nDia inicio:\t{inicio}\tDia fin:\t{final}\nHora inicio:\t{horaInicio}\tHora fin:\t{horaFinal}\n\n',
                            'largoErr':7,
                            'largoHeaderCalibracion':10,
                            'byteSeparador':255,
                            'cantidadDeVariables':5,
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

def inRange(valor,*arg):
    if not valor: return False
    flag = False
    for range in arg:
        if valor > range[0] and valor < range[1]:
            flag = True
        else:
            flag = False
            break             
        if not flag: return False
    if flag: return True

class Medicion():
    def __init__(self,fileName,TV,TI):
        self.r32 = self.openR32(fileName)
        self.TV = TV
        self.TI = TI
        self.serie = self.getSerie()
        self.headerCalibracion = self.calibraciones()
        [self.calibrTension,
        self.calibrTensionNo220,
        self.calibrThd,
        self.calibrResiduo,
        self.calibrFlicker] = struct.unpack(self.serie['unpackHeaderCalibracion'],self.headerCalibracion)
    
    registrosProcesados = []
    errsProcesados = []
    chunks = []
    raws = []
    es1612 = False
    inicio = None
    final = None
    periodo = None
    uTimePeriodo = 'min'
    horaCambiada = False
    
    def openR32(self,fileName):
        with open(fileName,'rb') as f:
            return f.read()

    def getSerie(self):
        return dataSeries['Vieja'][1]

    def analizarR32(self):
        serie = self.serie
        timeInicioCorte = None
        timeFinCorte = None
        timeInicioReg = None
        timeFinReg = None
        flagAnomalia = False

        def pad(timeInicioReg,lastTime,timeInicioCorte,timeFinCorte):
            while True:
                timeFinReg = self.stampGen.send(None)
                timeInicioReg = self.inicio if not timeInicioReg else lastTime
                lastTime = timeFinReg
                enPeriodo = inRange(timeFinCorte,(timeInicioReg,timeFinReg))
                if not enPeriodo:
                    regProcesado,regRaw = self.procesarReg(None,padding=True)
                    self.registrosProcesados.append({'timeFinReg':timeFinReg,'regProcesado':regProcesado,'Anomalia':True})
                else:
                    return timeFinReg
        
        def reset():
            self.chunks = []
            self.registrosProcesados = []
            self.errsProcesados = []
            self.stampGen.close()
            self.horaCambiada = False

        for tipo,data in feeder(self.r32,serie['largoRegistro'],serie['largoErr'],serie['byteSeparador']):
            if tipo in ['err','reg']:
                self.chunks.append({'tipo':tipo,'data':data})
            elif tipo == 'header':
                self.header = data
                header = struct.unpack(serie['unpackHeader'],self.header)
                self.headerData = dict(zip(list(serie['headerMap'].keys()),[search('(?<=\').+(?=\')',str(header[serie['headerMap'][x]])).group() for x in serie['headerMap']]))
                headerData = self.headerData

                self.inicio = strptime(' '.join([headerData['diaInicio'],headerData['mesInicio'],headerData['añoInicio'],headerData['horaInicio'],headerData['minInicio']]),'%d %m %y %H %M')
                self.final = strptime(' '.join([headerData['diaFin'],headerData['mesFin'],headerData['añoFin'],headerData['horaFin'],headerData['minFin']]),'%d %m %y %H %M')
                self.periodo = int(self.headerData['periodo'])

                self.stampGen = self.timeStampGen(self.inicio)

                lastTime = self.inicio
                for chunk in self.chunks:
                    if chunk['tipo'] == 'err':
                        isCorte,errTimeStamp = self.procesarErr(chunk['data'])
                        if all([not isCorte,not errTimeStamp]): continue
                        elif isCorte == None:
                            if errTimeStamp == True: lastTime = self.inicio
                            timeInicioReg = self.inicio
                            self.stampGen.close()
                            self.stampGen = self.timeStampGen(self.inicio)
                            continue
                        elif isCorte: timeInicioCorte = errTimeStamp
                        elif not isCorte:
                            timeFinCorte = errTimeStamp
                            if inRange(timeFinCorte,(timeInicioReg,timeFinReg)):
                                flagAnomalia = True
                            else:
                                timeFinReg = pad(timeInicioReg,lastTime,timeInicioCorte,timeFinCorte)
                                flagAnomalia = True

                    elif chunk['tipo'] == 'reg':
                        if flagAnomalia: flagAnomalia = False
                        else: timeFinReg = self.stampGen.send(None)
                         
                        timeInicioReg = self.inicio if not timeInicioReg else lastTime
                        lastTime = timeFinReg
                        enPeriodo = inRange(timeInicioCorte,(timeInicioReg,timeFinReg))
                        if enPeriodo:
                            regProcesado,regRaw = self.procesarReg(chunk['data'])
                            self.registrosProcesados.append({'timeFinReg':timeFinReg,'regProcesado':regProcesado,'Anomalia':True})
                        elif isCorte:
                            regProcesado,regRaw = self.procesarReg(None,padding=True)
                            self.registrosProcesados.append({'timeFinReg':timeFinReg,'regProcesado':regProcesado,'Anomalia':True})
                        elif not isCorte:
                            regProcesado,regRaw = self.procesarReg(chunk['data'])
                            self.registrosProcesados.append({'timeFinReg':timeFinReg,'regProcesado':regProcesado,'Anomalia':False})
                        else: print('MMMMMMMMMMMMMM')
                self.genDat()
                self.genErr()
                reset()

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
        cuartosDeHora,resto = divmod(mktime(startTime),(self.periodo*60))
        stampSeconds = cuartosDeHora*(self.periodo*60)
        while True:
            stampSeconds += (self.periodo*60)
            yield localtime(stampSeconds)
    
    def genHeader(self):
        return self.serie['headerDat'].format(
            filename=self.headerData['filename'],
            periodo=self.periodo,
            Utiempo=self.uTimePeriodo,
            tension='220',
            TV=self.TV,TI=self.TI,
            corriente='35',
            inicio=strftime('%d/%m/%Y',self.inicio),
            final=strftime('%d/%m/%Y',self.final),
            horaInicio=strftime('%H:%M',self.inicio),
            horaFinal=strftime('%H:%M',self.final))

    def genDat(self):
        headerData = self.headerData
        datDump =  open(headerData['filename']+'.dat','w',encoding='utf-8')
        datDump.write(self.genHeader())
        for i in self.registrosProcesados:
            datos = '\t'.join([str(x) for x in i['regProcesado']])
            time = strftime('%d/%m/%y\t%H:%M:%S',i['timeFinReg'])
            anomalia = 'A' if i['Anomalia'] else ''
            datDump.write('\t'.join([time,datos,anomalia,'\n']))

    def genErr(self):
        headerData = self.headerData
        errDump = open(headerData['filename']+'.err','w',encoding='utf-8')
        inicio = strptime(' '.join([headerData['diaInicio'],headerData['mesInicio'],headerData['añoInicio'],headerData['horaInicio'],headerData['minInicio']]),'%d %m %y %H %M')
        errDump.write('\t'.join([strftime('%d/%m/%y\t%H:%M:%S',inicio),'Comienzo del Registro.','\n']))
        for timeStamp,codigo in self.errsProcesados:
            if self.es1612: continue
            else: errDump.write('\t'.join([strftime('%d/%m/%y\t%H:%M:%S',timeStamp),errCodes[codigo],'\n']))
        
    def procesarErr(self,err):
        timeInicioCorte = None
        timeFinCorte = None
       
        err = struct.unpack(self.serie['unpackErr'],err)
        err = [str(hex(i)) for i in err]
        err = [search('(?<=x).+',x).group().zfill(2) for x in err]

        timeStamp = strptime(''.join(err[1:]),'%S%M%H%d%m%y')
        codigo = int(err[0])
        self.errsProcesados.append((timeStamp,codigo))
        
        if codigo == 85 and not self.horaCambiada:
            self.horaCambiada = True
            return None,None
        elif codigo == 84: return 'DD',timeStamp 
        elif codigo == 83: return None,None
        elif codigo == 85 and self.horaCambiada:
            self.inicio = timeStamp
            return None,True
        elif codigo == 82:
            timeInicioCorte = timeStamp
            return True,timeInicioCorte
        elif codigo == 81:
            timeFinCorte = timeStamp
            return False,timeFinCorte

    def procesarReg(self,reg,padding=False):
        if padding:
            return [0.0 for _ in range(self.serie['cantidadDeVariables'])],None
        data = struct.unpack(self.serie['unpackString'],reg)
        VRaw = data[self.serie['regIndexes']['V']]
        VmaxRaw = data[self.serie['regIndexes']['Vmax']]
        VminRaw = data[self.serie['regIndexes']['Vmin']]
        thdRaw = data[self.serie['regIndexes']['thd']]
        flickerRaw = data[self.serie['regIndexes']['flicker']]

        V = self.serie['factorTension'](VRaw)
        Vmax = self.serie['factorTension'](VmaxRaw)
        Vmin = self.serie['factorTension'](VminRaw)
        thd = self.serie['getThd'](V,thdRaw,self.calibrResiduo,self.calibrTension,VRaw,self.calibrThd)
        if thd>10: thd = 10.0
        flicker = self.serie['getFlicker'](flickerRaw,self.calibrFlicker,V)
        if flicker>2: flicker = 2.0
        
        return (V,Vmax,Vmin,thd,flicker),data

# file = 'Serie vieja T/ori.R32'
# fileDat = 'Serie vieja T/ori.dat'
file = 'Serie vieja M/Originales/010388O1.R32'
fileDat = 'Serie vieja M/Originales/010388O1.dat'

medicion = Medicion(file,1,1)
try:
    medicion.analizarR32()
except KeyboardInterrupt:
    for i in medicion.registrosProcesados:
        print(i)
    exit()