from series import *
from errCodes import errCodes
from utils import *

import struct
from re import search,sub
from time import asctime,mktime,strptime,localtime,strftime

class Medicion():
    def __init__(self,fileName,TV,TI):
        self.r32 = self.openR32(fileName)
        self.TV = TV
        self.TI = TI
        self.serie = self.getSerie()
        
        if self.serie.name in ['Vieja','1104']:
            self.headerCalibracionRaw = self.calibraciones()
            self.headerCalibracion = struct.unpack(self.serie.unpackHeaderCalibracion['string'],self.headerCalibracionRaw)
            [self.calibrTension,
            self.calibrTensionNo220,
            self.calibrThd,
            self.calibrResiduo,
            self.calibrFlicker] = [self.headerCalibracion[x] for x in self.serie.unpackHeaderCalibracion['indices']]
    
    registrosProcesados = []
    errsProcesados = []
    chunks = []
    inicio = None
    final = None
    periodo = None
    uTimePeriodo = 'min'
    
    def openR32(self,fileName):
        with open(fileName,'rb') as f:
            return f.read()

    def getSerie(self):
        return serie1605Monofasica()

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
        
        def reset():
            self.chunks = []
            self.registrosProcesados = []
            self.errsProcesados = []
            self.stampGen.close()

        for tipo,data in feeder(self.r32,serie.largoRegistro,serie.largoErr,struct.calcsize(serie.unpackHeaderSecundario),struct.calcsize(serie.unpackHeaderCalibracion['string']),serie.byteSeparador):
            if tipo in ['err','reg']:
                self.chunks.append({'tipo':tipo,'data':data})
            elif tipo == 'header':
                try: header = struct.unpack(serie.unpackHeader,data)
                except: header = struct.unpack(serie.unpackHeaderSecundario,data)

                self.headerData = dict(zip(list(serie.headerMap.keys()),[search('(?<=\').+(?=\')',str(header[serie.headerMap[x]])).group() for x in serie.headerMap]))
                headerData = self.headerData
                self.inicio = strptime(' '.join([headerData['diaInicio'],headerData['mesInicio'],headerData['añoInicio'],headerData['horaInicio'],headerData['minInicio']]),'%d %m %y %H %M')
                self.final = strptime(' '.join([headerData['diaFin'],headerData['mesFin'],headerData['añoFin'],headerData['horaFin'],headerData['minFin']]),'%d %m %y %H %M')
                self.periodo = int(self.headerData['periodo'])

                self.stampGen = self.timeStampGen(self.inicio)

                lastTime = self.inicio
                for chunk in self.chunks:
                    if chunk['tipo'] == 'err':
                        dataErr = self.procesarErr(chunk['data'])
                        if dataErr['codigo'] in [84,83]: continue
                        elif dataErr['codigo'] == 85: # Cambio de hora
                            self.inicio = dataErr['timeStamp']
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
                        if self.serie.name in ['1104','Vieja'] and not self.serie.trifasico:
                            if chunk['data'] == self.headerCalibracionRaw[-len(chunk['data']):]: continue
                        if not padded: timeFinReg = self.stampGen.send(None)
                        padded = False
                        timeInicioReg = self.inicio if not timeInicioReg else lastTime
                        lastTime = timeFinReg 

                        regProcesado,_ = self.procesarReg(chunk['data'])
                        anomalia = (inRange(timeInicioCorte,(timeInicioReg,timeFinReg)) | inRange(timeFinCorte,(timeInicioReg,timeFinReg)))
                        self.registrosProcesados.append({'timeFinReg':timeFinReg,'regProcesado':regProcesado,'Anomalia':anomalia})

                if not self.registrosProcesados: continue
                self.genDat()
                self.genErr()
                reset()

    def calibraciones(self):
        puntero = 0
        hold = 0
        OPEN = False
        for byte in self.r32:
            size = puntero-hold
            if OPEN and byte == self.serie.byteSeparador:
                OPEN = False
                hold = puntero
                pass
            elif not OPEN and byte != self.serie.byteSeparador:
                if size == struct.calcsize(self.serie.unpackHeaderCalibracion['string']) and  self.r32[puntero+1] == self.serie.byteSeparador:
                    return  self.r32[hold+1:puntero+1]
            elif not OPEN and byte == self.serie.byteSeparador:
                OPEN = True
                hold = puntero
            puntero += 1

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
            horaFinal=strftime('%H:%M',self.final))

    def genDat(self):
        with open(self.headerData['filename']+'.dat','w',encoding='utf-8') as datDump:
            datDump.write(self.genHeader())
            for reg in self.registrosProcesados:
                lista = (strftime('%d/%m/%y\t%H:%M',reg['timeFinReg']),) + tuple(reg['regProcesado']) + ('A' if reg['Anomalia'] else '',)
                datDump.write(sub('\.',',',self.serie.formatoReg%lista))

    def genErr(self):
        headerData = self.headerData
        with open(headerData['filename']+'.err','w',encoding='utf-8') as errDump:
            inicio = strptime(' '.join([headerData['diaInicio'],headerData['mesInicio'],headerData['añoInicio'],headerData['horaInicio'],headerData['minInicio']]),'%d %m %y %H %M')
            errDump.write('\t'.join([strftime('%d/%m/%y\t%H:%M:%S',inicio),'Comienzo del Registro.','\n']))
            for timeStamp,codigo in self.errsProcesados:
                lista = (strftime('%d/%m/%y\t%H:%M:%S',timeStamp),errCodes[codigo])
                if self.serie.name == '1612': continue
                else: errDump.write(self.serie.formatoErr%lista)
        
    def procesarErr(self,err):
        horaCambiada = False
        err = struct.unpack(self.serie.unpackErr,err)
        err = [str(hex(i)) for i in err]
        err = [search('(?<=x).+',x).group().zfill(2) for x in err]

        timeStamp = strptime(''.join(err[1:]),'%S%M%H%d%m%y')
        codigo = int(err[0])
        self.errsProcesados.append((timeStamp,codigo))

        if codigo == 85 and not horaCambiada:
            horaCambiada = True
            return {'codigo':codigo,'isCorte':False,'timeStamp':timeStamp}
        elif codigo == 84: return {'codigo':codigo,'isCorte':False,'timeStamp':timeStamp} 
        elif codigo == 83: return {'codigo':codigo,'isCorte':False,'timeStamp':timeStamp}
        elif codigo == 85 and horaCambiada:
            return {'codigo':codigo,'isCorte':False,'timeStamp':timeStamp}
        elif codigo == 82:
            return {'codigo':codigo,'isCorte':True,'timeStamp':timeStamp}
        elif codigo == 81:
            return {'codigo':codigo,'isCorte':False,'timeStamp':timeStamp}
        else:print('err no reconocido',codigo,timeStamp)

    def procesarReg(self,reg,padding=False):
        if padding:
            return [0.0 for _ in range(self.serie.variables)],None
        data = struct.unpack(self.serie.unpackString,reg)
        dataRaw = dict(zip(self.serie.regIndexes,[data[x] for x in self.serie.regIndexes.values()]))

        if self.serie.trifasico:
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

            totalEnergia = sum((energiaR,energiaS,energiaT))
            totalPotencia = sum((VR*IR*cosPhiR/1000,VS*IS*cosPhiS/1000,VT*IT*cosPhiT/1000,))

            thd = 1.666
            flicker = self.serie.getFlicker(dataRaw['flicker'],self.calibrFlicker,V)
            
            return (VR,VRmax,VRmin,IR,cosPhiR,energiaR,VS,VSmax,VSmin,IS,cosPhiS,energiaS,VT,VTmax,VTmin,IT,cosPhiT,energiaT,thd,flicker,totalPotencia,totalEnergia,),data

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