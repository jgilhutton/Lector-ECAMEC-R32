import struct

dataSeries = {'Vieja':{
                        3:{'largoRegistro':42,'largoErr':7,'byteSeparador':255,'factorTension':0.008392429613633932,'factorCorriente':0.005080833735381121,'factorE':0.00000792810057793741,'packString':'>HHHHHHHH HxHHHHH HxHHHHH'},
                        # flicker, thd, [,I,Vmax,Vmin,V]x3
                        1:{'largoRegistro':10,'largoErr':7,'byteSeparador':255,'factorTension':0.07087550450170754,'factorCorriente':0.005080833735381121,'factorFlicker':0.00058,'factorThd':0.002253337675024422,'packString':'>HBBHHH'},
                    },
            '1104':{
                        1:{'largoRegistro':19,'largoErr':7,'byteSeparador':255,'factorTension':0.07087550450170754,'factorCorriente':0.005080833735381121,'factorFlicker':0.00058,'factorThd':0.002253337675024422,'packString':'>HHxxxxxxxxxHHH'},
            }
}

file = 'Serie 1104 M/010288O1.r32'
# file = 'Serie vieja T/mini.r32'

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
    return dataSeries['1104'][1]

serie = getSerie(r32)
for tipo,data in feeder(r32,serie['largoRegistro'],serie['largoErr'],serie['byteSeparador']):
    if tipo == 'err': print(data)
    # if tipo == 'reg':
    #     a = struct.unpack(serie['packString'],data)
    #     print(a)
        
