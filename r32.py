import struct
from statistics import variance
import matplotlib.pyplot as plt
from math import ceil

dataSeries = {
            'Vieja':{
                        1:{
                            'largoRegistro':10,
                            'largoErr':7,
                            'byteSeparador':255,
                            'factorTension':lambda x: x*0.07087628543376923,
                            'factorFlicker':lambda x: x*0.00058,
                            'getThd':lambda u,v,w,x,y,z: (100/u)*(abs(v-((w/x)*y)))*18/z,
                            'unpackString':'>HHHHH',
                            'unpackErr':'>BBBBBBB',
                            'regIndexes':{'thd':1,'flicker':0,'Vmin':2,'Vmax':3,'V':4},},
                        3:{
                            'largoRegistro':42,
                            'largoErr':7,
                            'byteSeparador':255,
                            'factorTension':lambda x: x*0.008392460165229354,
                            'factorCorriente':lambda x: x*0.005086235518683759,
                            'factorPotencia':lambda x,y: y*x,
                            # 'packString':'>HHHHHHHH HxHHHHH HxHHHHH',
                            'packString':'>HB HBH H HHH HBH H HHH HBH H HHH',
                            'headerCalibracion':'>HHHHH'
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
            '1612':{}
}

# file = 'Serie vieja T/ori.R32'
# fileDat = 'Serie vieja T/ori.dat'
file = 'Serie vieja M/Originales/010388O1.R32'
fileDat = 'Serie vieja M/Originales/010388O1.dat'

with open(file,'rb') as f:
    r32 = f.read()

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

def getSerie(r32):
    return dataSeries['Vieja'][1]

def getDatData(col=None):
    global dataDat
    with open(fileDat,'r') as f:
        F = f.readlines()
        if col:
            dataDat = [y.split('\t')[col] for y in F[9:]]
        else:
            dataDat = [y.split('\t') for y in F[9:]]
            dataDat = [[x[2],x[3],x[4],x[5]] for x in [y for y in dataDat] if float(x[2].replace(',','.'))]

serie = getSerie(r32)

raws = []
regs = []
ignoreRegs = False
for tipo,data in feeder(r32,serie['largoRegistro'],serie['largoErr'],serie['byteSeparador']):
    # if tipo == 'header':
    #     header= struct.unpack(serie['packHeader'],data)
    #     headerData = dict(zip(list(serie['headerMap'].keys()),[header[serie['headerMap'][x]] for x in serie['headerMap']]))
    if tipo == 'err':
        err = struct.unpack(serie['unpackErr'],data)
        err = [int(str(hex(i)).split('x')[1]) for i in err]
        if err[0] == 82: ignoreRegs = True
        elif err[0] == 81 and ignoreRegs: ignoreRegs = False
    if tipo == 'reg' and not ignoreRegs:
        try:
            a = struct.unpack(serie['unpackString'],data)
            VRaw = a[serie['regIndexes']['V']]
            VmaxRaw = a[serie['regIndexes']['Vmax']]
            VminRaw = a[serie['regIndexes']['Vmin']]
            thdRaw = a[serie['regIndexes']['thd']]
            flickerRaw = a[serie['regIndexes']['flicker']]

            V = serie['factorTension'](VRaw)
            Vmax = serie['factorTension'](VmaxRaw)
            Vmin = serie['factorTension'](VminRaw)

            calibrTension = struct.unpack('>H',b'\x0c\x20')[0]
            calibrResiduo = struct.unpack('>H',b'\x00\xc8')[0]
            calibreThd = struct.unpack('>H',b'\x06\x65')[0]
            thd = serie['getThd'](V,thdRaw,calibrResiduo,calibrTension,VRaw,calibreThd)
            if thd>10: thd = 10.0
            # print(calibreThd,calibrResiduo,calibrTension,v6,v7,thd)

            # print(byte)
            regs.append((V,Vmax,Vmin,thd))
            raws.append(data)
        except Exception as e:
            print(e)

getDatData()
# chunk = 0
offset = 0
for x,y,z in list(zip(dataDat,raws[offset:],regs[offset:])):
    input([x,[round(i,2) for i in z],y])#[::-1])
    
# l = [[x,y] for x,y in list(zip(dataDat[:600],ps[offset:][:600]))]
# xs = [x for x,y in l if x<0.5][chunk:200+chunk]
# ys = [y for x,y in l if x<0.5][chunk:200+chunk]
# # ys = [y*c for x,y in l if x>0.4]
# plt.scatter(xs,ys,c='red',s=1)
# plt.scatter(xs,xs,c='black',s=1)
# plt.show()