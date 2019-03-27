from series import *
from errCodes import errCodes
from utils import *

import struct
from re import search,sub
from time import asctime,mktime,strptime,localtime,strftime

class Medicion:
    def __init__(self,fileName,inputFolder,outputFolder,TV,TI):
        self.fileName = fileName
        self.inputFolder = inputFolder
        self.outputFolder = outputFolder
        self.r32 = self.openR32()
        if not self.r32: return False
        self.TV = TV
        self.TI = TI
        serieClass = self.getSerie()
        self.serie = serieClass()
        if self.serie:
            self.serie1612 = True if self.serie.name == '1612' else False
        self.chunks = []
        self.registrosProcesados = []
        self.errsProcesados = []
        self.inicio = None
        self.final = None
        self.periodo = None
        self.uTimePeriodo = 'min'

    def openR32(self):
        try:
            with open(self.inputFolder+'/'+self.fileName,'rb') as f:
                return f.read()
        except FileNotFoundError:
            print('ERROR:\tNo se encontró el archivo "{}" en la carpeta "{}"\n'.format(self.fileName,self.inputFolder))
            return False

    def getSerie(self):
        if search(b'(?s)^\xff.{36}\xff.{35}\xff.\xff',self.r32):
            return serieViejaTrifasica
        elif search(b'(?s)^\xff.{36}\xff.{10}\xff',self.r32):
            return serieViejaMonofasica
        elif search(b'(?s)^\xff.{36}\xff.{28}\xff',self.r32):
            return serie1104Monofasica
        elif search(b'(?s)^\xff.{36}\xff.{37}\xff',self.r32):
            return serie1104Trifasica
        elif search(b'(?s)^\xff.{36}\xff.{54}\xff',self.r32):
            return serie1605Monofasica
        elif search(b'(?s)^.{68}\xff.{21}\xff',self.r32):
            return serie1612Trifasica
        else:
            print('Serie no reconocida',self.fileName)
            return None

    def analizar1612(self):
        pass


    def analizarR32(self):
        serie = self.serie
        timeInicioCorte = None
        timeFinCorte = None
        timeInicioReg = None
        timeFinReg = None
        ERR = False
        padded = True

        def pad(timeInicioReg,lastTime,timeInicioCorte,timeFinCorte):
            while True:
                timeFinReg = self.stampGen.send(None)
                timeInicioReg = self.inicio if not timeInicioReg else lastTime
                lastTime = timeFinReg
                if not inRange(timeFinCorte,(timeInicioReg,timeFinReg)):
                    if self.serie.padding:
                        regProcesado,_ = self.procesarReg(None,padding=True)
                        self.registrosProcesados.append({'timeFinReg':timeFinReg,'regProcesado':regProcesado,'Anomalia':True})
                else:
                    return timeInicioReg,timeFinReg            

        if self.serie1612:
            self.analizar1612()
            return
        for dataDict in feeder(self.r32,serie.regex):
            if dataDict['err']:
                self.chunks.append({'tipo':'err','data':dataDict['err'][::-1]})
            elif dataDict['reg']:
                self.chunks.append({'tipo':'reg','data':dataDict['reg'][::-1]})
            elif dataDict['header']:
                if dataDict['calibr']:
                    self.calibraciones(dataDict['calibr'][::-1])
                elif serie.name in ['1104','Vieja','1605']:
                    continue
                if dataDict['ffSeparated']: header = struct.unpack(serie.unpackHeaderSecundario,dataDict['header'][::-1])
                else: header = struct.unpack(serie.unpackHeader,dataDict['header'][::-1])
                
                self.headerData = dict(zip(list(serie.headerMap.keys()),[search('(?<=\').+(?=\')',str(header[serie.headerMap[x]])).group() for x in serie.headerMap]))
                headerData = self.headerData
                self.inicio = strptime(' '.join([headerData['diaInicio'],headerData['mesInicio'],headerData['añoInicio'],headerData['horaInicio'],headerData['minInicio']]),'%d %m %y %H %M')
                self.final = strptime(' '.join([headerData['diaFin'],headerData['mesFin'],headerData['añoFin'],headerData['horaFin'],headerData['minFin']]),'%d %m %y %H %M')
                self.periodo = int(self.headerData['periodo'])
                try:self.subestacion = self.headerData['subestacion'].replace('\x00','')
                except:pass
                self.stampGen = self.timeStampGen(self.inicio)

                lastTime = self.inicio
                for chunk in self.chunks:
                    if chunk['tipo'] == 'err':
                        dataErr = self.procesarErr(chunk['data'])
                        if dataErr['codigo'] in [84,83]: continue
                        elif dataErr['codigo'] == 85: # Cambio de hora
                            self.inicio = dataErr['timeStamp']
                            lastTime = self.inicio
                            timeInicioReg = self.inicio
                            timeFinReg = self.inicio
                            self.stampGen.close()
                            self.stampGen = self.timeStampGen(self.inicio)
                        elif dataErr['isCorte']:
                            ERR = True
                            timeInicioCorte = dataErr['timeStamp']
                            timeFinCorte = timeInicioCorte #Esto es para darle un valor nada más
                        elif not dataErr['isCorte']:
                            ERR = False
                            timeFinCorte = dataErr['timeStamp']
                            if not inRange(mktime(timeFinCorte),(mktime(timeInicioReg),mktime(timeFinReg))):
                                timeInicioReg,timeFinReg = pad(timeInicioReg,lastTime,timeInicioCorte,timeFinCorte)
                                lastTime = timeInicioReg
                                padded = True
    
                    elif chunk['tipo'] == 'reg' and not ERR:
                        if not timeFinReg:
                            # timeFinReg = self.inicio
                            continue
                        elif not padded:
                            timeFinReg = self.stampGen.send(None)
                        padded = False
                        timeInicioReg = self.inicio if not timeInicioReg else lastTime
                        lastTime = timeFinReg 

                        regProcesado,_ = self.procesarReg(chunk['data'])
                        anomalia = (inRange(timeInicioCorte,(timeInicioReg,timeFinReg)) | inRange(timeFinCorte,(timeInicioReg,timeFinReg)))
                        self.registrosProcesados.append({'timeFinReg':timeFinReg,'regProcesado':regProcesado,'Anomalia':anomalia})

                if not self.registrosProcesados: continue
                self.genDat()
                self.genErr()
                self.stampGen.close()

    def calibraciones(self,data):
        self.headerCalibracion = struct.unpack(self.serie.unpackHeaderCalibracion['string'],data)
        [self.calibrTension,
        self.calibrTensionNo220,
        self.calibrThd,
        self.calibrResiduo,
        self.calibrFlicker] = [self.headerCalibracion[x] for x in self.serie.unpackHeaderCalibracion['indices']]
        self.calibrTension = 220.0 if (self.serie.name in ['Vieja','1104'] and self.serie.trifasico) else self.calibrTension

    def timeStampGen(self,startTime):
        cantidadPeriodos,_ = divmod(mktime(startTime),(self.periodo*60))
        stampSeconds = cantidadPeriodos*(self.periodo*60)
        while True:
            stampSeconds += (self.periodo*60)
            yield localtime(stampSeconds)
    
    def genHeader(self):
        return self.serie.headerDat.format(
            filename=self.headerData['filename'],
            serie=self.headerData['serie'] if self.headerData.__contains__('serie') else 'ND',
            periodo=self.periodo,
            Utiempo=self.uTimePeriodo,
            tension='220',
            TV=self.TV,TI=self.TI,
            corriente='35',
            inicio=strftime('%d/%m/%Y',self.inicio),
            final=strftime('%d/%m/%Y',self.final),
            horaInicio=strftime('%H:%M',self.inicio),
            horaFinal=strftime('%H:%M',self.final),
            subestacion='' if self.serie.name != '1612' else self.subestacion
            )
        
    def genDat(self):
        with open(self.outputFolder+'/'+self.headerData['filename']+'.dat','w',encoding='utf-8') as datDump:
            datDump.write(self.genHeader())
            for reg in self.registrosProcesados:
                lista = (strftime('%d/%m/%y\t%H:%M',reg['timeFinReg']),) + tuple(reg['regProcesado']) + ('A' if reg['Anomalia'] else '',)
                datDump.write(sub('\.',',',self.serie.formatoReg%lista))

    def genErr(self):
        headerData = self.headerData
        with open(self.outputFolder+'/'+headerData['filename']+'.err','w',encoding='utf-8') as errDump:
            inicio = strptime(' '.join([headerData['diaInicio'],headerData['mesInicio'],headerData['añoInicio'],headerData['horaInicio'],headerData['minInicio']]),'%d %m %y %H %M')
            errDump.write('\t'.join([strftime('%d/%m/%y\t%H:%M:%S',inicio),'Comienzo del Registro.','\n']))
            for timeStamp,codigo in self.errsProcesados:
                lista = (strftime('%d/%m/%y\t%H:%M:%S',timeStamp),errCodes[codigo])
                if self.serie.name == '1612': continue
                else: errDump.write(self.serie.formatoErr%lista)
        
    def procesarErr(self,err):
        self.horaCambiada = False
        err = struct.unpack(self.serie.unpackErr,err)
        err = [str(hex(i)) for i in err]
        err = [search('(?<=x).+',x).group().zfill(2) for x in err]

        timeStamp = strptime(''.join(err[1:]),'%S%M%H%d%m%y')
        codigo = int(err[0])
        self.errsProcesados.append((timeStamp,codigo))

        if codigo == 85:
            if not self.horaCambiada:
                self.horaCambiada = True
            else:
                self.horaCambiada = False
            return {'codigo':codigo,'isCorte':False,'timeStamp':timeStamp}
        elif codigo == 84: return {'codigo':codigo,'isCorte':False,'timeStamp':timeStamp} 
        elif codigo == 83: return {'codigo':codigo,'isCorte':False,'timeStamp':timeStamp}
        elif codigo == 85 and self.horaCambiada:
            return {'codigo':codigo,'isCorte':False,'timeStamp':timeStamp}
        elif codigo == 82:
            return {'codigo':codigo,'isCorte':True,'timeStamp':timeStamp}
        elif codigo == 81:
            return {'codigo':codigo,'isCorte':False,'timeStamp':timeStamp}
        else:print('err no reconocido',codigo,timeStamp)

    def procesarReg(self,reg,padding=False):
        if padding:
            return [0.0 for _ in range(self.serie.variables)],None
        data = struct.unpack(self.serie.unpackReg,reg)
        dataRaw = dict(zip(self.serie.regIndexes,[data[x] for x in self.serie.regIndexes.values()]))

        if self.serie.trifasico:
            if self.serie1612:
                VR,VS,VT = data[0:3]
                VRmax,VSmax,VTmax = data[4:7]
                VRmin,VSmin,VTmin = data[8:11]
                IR,IS,IT = data[23:26]
                cosasRaras = list(map(lambda x: x*5/0xffff,data[34:42]))
                thd = list(map(lambda x: x*500/0xffff,data[42:50]))[2]
                desb = list(map(lambda x: x*100/0xffff,data[50:60]))
                potencia = list(map(lambda x: x/1000,data[60:85]))
                potencia2 = data[85:93]
                potenciaMM = list(map(lambda x: x/1000,data[93:111]))
                fases = list(map(lambda x: x*360/0xffff,data[111:119]))
                flicker = list(map(lambda x: x**0.5,data[127:130]))[0]
                frecuencias = data[130:]
                energiaR=energiaS=energiaT=cosPhiR=cosPhiS=cosPhiT=totalEnergia=totalPotencia=0
            else:
                VR = self.serie.getTension(dataRaw['VR'])
                VRmax =self.serie.getTension(dataRaw['VRmax'])
                VRmin =self.serie.getTension(dataRaw['VRmin'])
                IR = self.serie.getCorriente(dataRaw['IR'])
                energiaR = self.serie.getEnergia(dataRaw['ERb1'],dataRaw['ERb2'],dataRaw['ERb3'])
                cosPhiR = self.serie.getCosPhi(energiaR,IR,VR,self.periodo)

                VS = self.serie.getTension(dataRaw['VS'])
                VSmax =self.serie.getTension(dataRaw['VSmax'])
                VSmin =self.serie.getTension(dataRaw['VSmin'])
                IS = self.serie.getCorriente(dataRaw['IS'])
                energiaS = self.serie.getEnergia(dataRaw['ESb1'],dataRaw['ESb2'],dataRaw['ESb3'])
                cosPhiS = self.serie.getCosPhi(energiaS,IS,VS,self.periodo)

                VT = self.serie.getTension(dataRaw['VT'])
                VTmax =self.serie.getTension(dataRaw['VSmax'])
                VTmin =self.serie.getTension(dataRaw['VSmin'])
                IT = self.serie.getCorriente(dataRaw['IT'])
                energiaT = self.serie.getEnergia(dataRaw['ETb1'],dataRaw['ETb2'],dataRaw['ETb3'])
                cosPhiT = self.serie.getCosPhi(energiaT,IT,VT,self.periodo)

                thdR = self.serie.getThd(VR,dataRaw['thdR'],self.calibrResiduo,self.calibrTension,self.calibrThd)
                thdS = self.serie.getThd(VS,dataRaw['thdS'],self.calibrResiduo,self.calibrTension,self.calibrThd)
                thdT = self.serie.getThd(VT,dataRaw['thdT'],self.calibrResiduo,self.calibrTension,self.calibrThd)
                thd=thdR
                flicker = self.serie.getFlicker(dataRaw['flicker'],self.calibrFlicker,VR)
                if thd>10: thd = 10.0
                if flicker>2: flicker = 2.0

                totalEnergia = sum((energiaR,energiaS,energiaT))
            if self.serie.name not in ['1612','1104']:
                totalPotencia = sum((VR*IR*cosPhiR/1000,VS*IS*cosPhiS/1000,VT*IT*cosPhiT/1000,))
                return (VR,VRmax,VRmin,IR,cosPhiR,energiaR,VS,VSmax,VSmin,IS,cosPhiS,energiaS,VT,VTmax,VTmin,IT,cosPhiT,energiaT,thd,flicker,totalPotencia,totalEnergia,),data
            else:
                return (VR,VRmax,VRmin,IR,cosPhiR,energiaR,VS,VSmax,VSmin,IS,cosPhiS,energiaS,VT,VTmax,VTmin,IT,cosPhiT,energiaT,thd,flicker,totalEnergia,),data

        else:
            V = self.serie.getTension(dataRaw['V'])
            Vmax = self.serie.getTension(dataRaw['Vmax'])
            Vmin = self.serie.getTension(dataRaw['Vmin'])
            if self.serie.name in ['1104','Vieja']:
                thd = self.serie.getThd(V,dataRaw['thd'],self.calibrResiduo,self.calibrTension,dataRaw['V'],self.calibrThd)
                flicker = self.serie.getFlicker(dataRaw['flicker'],self.calibrFlicker,V)
            elif self.serie.name in ['1605']:
                thd = self.serie.getThd(dataRaw['thd'])
                flicker = self.serie.getFlicker(dataRaw['flicker'])
            if thd>10: thd = 10.0
            if flicker>2: flicker = 2.0
            return (V,Vmax,Vmin,thd,flicker),data

