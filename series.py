class serieViejaMonofasica:
    headerDat = 'Equipo Nro:\t{filename}\t\tCódigo de Cliente: \tID. Subestación:\t        \nNumero de Serie:\t{serie}\tPeriodo:\t{periodo} {Utiempo}.\nTensión:     \t{tension} V\t\tFactor de Corrección: {TV}\nCorriente:\t{corriente} Amp\t\tFactor de Corrección: {TI}\nDia inicio:\t{inicio}\tDia fin:\t{final}\nHora inicio:\t{horaInicio}\tHora fin:\t{horaFinal}\n\nFecha	Hora\tU\tU Max\tU Min\tTHD1\tFlicker\tAnormalidad\n\t\tV\tV\tV\t%\t%\t\n'
    name = 'Vieja'

    largoErr = 7
    largoRegistro = 10
    largoHeaderCalibracion = 10
    unpackHeaderCalibracion = {'string':'HHHHH','indices':[0,1,2,3,4]}
    largosHeader = [36,0]
    variables = 5
    byteSeparador = '\xff'

    regex = '(?P<calibr>[^{byteSeparador}]{largoHeaderCalibracion})?{byteSeparador}(?P<header>[^{byteSeparador}]{largoHeader2}(?P<ffSeparated>{byteSeparador})?[^{byteSeparador}]{largoHeader1}(?={byteSeparador}))|(?P<reg>[^{byteSeparador}]{largoRegistro})|(?P<err>(?<={byteSeparador}).{largoErr}(?={byteSeparador}))'.format(byteSeparador=byteSeparador,largoErr='{%d}'%largoErr,largoHeader1='{%d}'%largosHeader[0],largoHeader2='{%d}'%largosHeader[1],largoHeaderCalibracion='{%d}'%largoHeaderCalibracion,largoRegistro='{%d}'%largoRegistro).encode('latin-1')
    
    maxValues = {'V':286,'Vmax':286,'Vmin':286,'thd':10,'flicker':2}
    
    formatoReg = '%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%s\n'
    formatoErr = '%s\t%s\n'
    
    unpackReg = '>HHHHH'
    regIndexes = {'flicker':0,'thd':1,'Vmin':2,'Vmax':3,'V':4}
    unpackHeader = '>8sx2s2s2s2s2s2s3x2s2s2s2s2sxx'
    unpackErr = '>BBBBBBB'

    headerMap = dict([reversed(x) for x in enumerate(['filename','periodo','diaInicio','mesInicio','añoInicio','horaInicio','minInicio','diaFin','mesFin','añoFin','horaFin','minFin'])])

    getTension = lambda self,V: V*0.07087628543376923
    getFlicker = lambda self,flickerRaw,calibrFlicker,V: ((flickerRaw*220*.02)/calibrFlicker)*(100/V)
    getThd = lambda self,V,thdRaw,calibrResiduo,calibrTension,vRaw,calibrThd: (100/V)*(abs(thdRaw-((calibrResiduo/calibrTension)*vRaw)))*18/calibrThd

    padding = True
    trifasico = False

class serieViejaTrifasica:
    headerDat = 'Equipo Nro:\t{filename}\t\tCódigo de Cliente: \tID. Subestación:\t        \nNumero de Serie:\t{serie}\tPeriodo:\t{periodo} {Utiempo}.\nTensión:     \t{tension} V\t\tFactor de Corrección: {TV}\nCorriente:\t{corriente} Amp\t\tFactor de Corrección: {TI}\nDia inicio:\t{inicio}\tDia fin:\t{final}\nHora inicio:\t{horaInicio}\tHora fin:\t{horaFinal}\n\nFecha\tHora\tU1\tU1 Max\tU1 Min\tI1\tFP 1\tEA1\tU2\tU2 Max\tU2 Min\tI2\tFP 2\tEA2\tU3\tU3 Max\tU3 Min\tI3\tFP 3\tEA3\tTHD1\tFlicker1\tP Total\tEA Total\tAnormalidad\n\t\tV\tV\tV\tA\tp.u.\tKWh\tV\tV\tV\tA\tp.u.\tKWh\tV\tV\tV\tA\tp.u.\tKWh\t%\t%\tKW\tKWh\t\n'
    name = 'Vieja'

    byteSeparador = '\xff'
    largoRegistro = 42
    largoErr = 7
    largosHeader = [36,8]
    largoHeaderBasura = 13
    largoHeaderCalibracion = 14
    regex = '(?P<calibr>(?<={byteSeparador})[^{byteSeparador}]{largoHeaderCalibracion})?(?P<basura>[^{byteSeparador}]{largoHeaderBasura})(?P<header>[^{byteSeparador}]{largoHeader2}(?P<ffSeparated>{byteSeparador})?[^{byteSeparador}]{largoHeader1}(?={byteSeparador}))|(?P<reg>[^{byteSeparador}]{largoRegistro})|(?P<err>(?<={byteSeparador}).{largoErr}(?={byteSeparador}))'.format(byteSeparador=byteSeparador,largoErr='{%d}'%largoErr,largoHeader1='{%d}'%largosHeader[0],largoHeader2='{%d}'%largosHeader[1],largoHeaderCalibracion='{%d}'%largoHeaderCalibracion,largoRegistro='{%d}'%largoRegistro,largoHeaderBasura='{%d}'%largoHeaderBasura).encode('latin-1')
    print(regex)
    variables = 22
    
    formatoReg = '%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.3f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.3f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.3f\t%0.2f\t%0.3f\t%0.3f\t%0.3f\t%s\n'
    formatoErr = '%s\t%s\n'
    
    getTension = lambda self,V: V*0.008392460165229354
    getCorriente = lambda self,I: I*0.0050863404758274555
    getEnergia = lambda self,j,k,l: ((((j<<7)+k)<<7)+l)*0.015687283128499985/1000
    getCosPhi = lambda self,energia,I,V,periodo: energia/(I*V/1000*periodo/60)
    getFlicker = lambda self,flickerRaw,calibrFlicker,V: ((flickerRaw*220*.02)/calibrFlicker)*(100/V)
    getThd = lambda self,V,thdRaw,calibrResiduo,calibrTension,vRaw,calibrThd: (100/V)*(abs(thdRaw-((calibrResiduo/calibrTension)*vRaw)))*18/calibrThd
    
    unpackReg = '>xx x H 3b H HHH H 3b H HHH H 3b H HHH'
    unpackHeader = '>8s x 2s 2s2s2s2s2s 3x 2s2s2s2s2s 2x 8s'
    unpackHeaderSecundario = '>8s x 2s 2s2s2s2s2s 3x 2s2s2s2s2s 3x 8s'
    unpackHeaderCalibracion = {'string':'HHHHHHH','indices':[2,3,0,1,6]}
    unpackErr = '>BBBBBBB'

    headerMap = dict([reversed(x) for x in enumerate(['serie','periodo','diaInicio','mesInicio','añoInicio','horaInicio','minInicio','diaFin','mesFin','añoFin','horaFin','minFin','filename'])])
    regIndexes = {'thdT':0,'ETb1':1,'ETb2':2,'ETb3':3,'IT':4,'VTmin':5,'VTmax':6,'VT':7,'thdS':8,'ESb1':9,'ESb2':10,'ESb3':11,'IS':12,'VSmin':13,'VSmax':14,'VS':15,'thdR':16,'ERb1':17,'ERb2':18,'ERb3':19,'IR':20,'VRmin':21,'VRmax':22,'VR':23,}
    
    padding = False
    trifasico = True

class serie1104Monofasica:
    headerDat = 'Equipo Nro:\t{filename}\t\tCódigo de Cliente: \tID. Subestación:\t        \nNumero de Serie:\t{serie}\tPeriodo:\t{periodo} {Utiempo}.\nTensión:     \t{tension} V\t\tFactor de Corrección: {TV}\nCorriente:\t{corriente} Amp\t\tFactor de Corrección: {TI}\nDia inicio:\t{inicio}\tDia fin:\t{final}\nHora inicio:\t{horaInicio}\tHora fin:\t{horaFinal}\n\nFecha	Hora\tU\tU Max\tU Min\tTHD1\tFlicker\tAnormalidad\n\t\tV\tV\tV\t%\t%\t\n'
    name = '1104'

    largoErr = 7
    largoRegistro = 19
    variables = 5
    largosHeader = [36,0]
    byteSeparador = '\xff'
    largoHeaderCalibracion = 28
    unpackHeaderCalibracion = {'string':'HxxxxxxxxxxHxxHHxxxxHxx','indices':[3,0,1,4,2]}

    regex = '(?P<calibr>[^{byteSeparador}]{largoHeaderCalibracion})?{byteSeparador}(?P<header>[^{byteSeparador}]{largoHeader2}(?P<ffSeparated>{byteSeparador})?[^{byteSeparador}]{largoHeader1}(?={byteSeparador}))|(?P<reg>[^{byteSeparador}]{largoRegistro})|(?P<err>(?<={byteSeparador}).{largoErr}(?={byteSeparador}))'.format(byteSeparador=byteSeparador,largoErr='{%d}'%largoErr,largoHeader1='{%d}'%largosHeader[0],largoHeader2='{%d}'%largosHeader[1],largoHeaderCalibracion='{%d}'%largoHeaderCalibracion,largoRegistro='{%d}'%largoRegistro).encode('latin-1')
    
    maxValues = {'V':286,'Vmax':286,'Vmin':286,'thd':10,'flicker':2}
    
    formatoReg = '%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%s\n'
    formatoErr = '%s\t%s\n'
    
    unpackReg = '>HH 9x HHH'
    unpackHeader = '>8sx2s2s2s2s2s2s3x2s2s2s2s2sxx'
    unpackErr = '>BBBBBBB'

    headerMap = dict([reversed(x) for x in enumerate(['filename','periodo','diaInicio','mesInicio','añoInicio','horaInicio','minInicio','diaFin','mesFin','añoFin','horaFin','minFin'])])
    regIndexes = {'flicker':0,'thd':1,'Vmin':2,'Vmax':3,'V':4}

    getTension = lambda self,x: x*0.1342281848192215
    getFlicker = lambda self,flickerRaw,calibrFlicker,V: ((flickerRaw*220*.02)/calibrFlicker)*(100/V)
    getThd = lambda self,V,thdRaw,calibrResiduo,calibrTension,vRaw,calibrThd: (100/V)*(abs(thdRaw-((calibrResiduo/calibrTension)*vRaw)))*18/calibrThd

    padding = True
    trifasico = False

class serie1104Trifasica:
    headerDat = 'Equipo Nro:\t{filename}\t\tCódigo de Cliente: \tID. Subestación:\t        \nNumero de Serie:\t{serie}\tPeriodo:\t{periodo} {Utiempo}.\nTensión:     \t{tension} V\t\tFactor de Corrección: {TV}\nCorriente:\t{corriente} Amp\t\tFactor de Corrección: {TI}\nDia inicio:\t{inicio}\tDia fin:\t{final}\nHora inicio:\t{horaInicio}\tHora fin:\t{horaFinal}\n\nFecha	Hora\tU\tU Max\tU Min\tTHD1\tFlicker\tAnormalidad\n\t\tV\tV\tV\t%\t%\t\n'
    name = '1104'

    largoErr = 7
    largoRegistro = 54
    variables = 5
    byteSeparador = '\xff'
    
    maxValues = {'V':286,'Vmax':286,'Vmin':286,'thd':10,'flicker':2}
    
    formatoReg = '%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%s\n'
    formatoErr = '%s\t%s\n'
    
    unpackReg = '>HHxxxxxxxxHHHHxxxxxxxxxHHHHxxxxxxxxxHHHH'
    unpackHeaderCalibracion = {'string':'HxxxxxxxxxxHxxHHxxxxHxx','indices':[3,0,1,4,2]}
    regIndexes = {'flicker':0,'thd':1,'Vmin':2,'Vmax':3,'V':4}
    unpackHeader = '>8sx2s2s2s2s2s2s3x2s2s2s2s2sxx'
    unpackHeaderSecundario = '>8sx2s2s2s2s2s2s3x2s2s2s2s2sxx'
    unpackErr = '>BBBBBBB'

    headerMap = dict([reversed(x) for x in enumerate(['filename','periodo','diaInicio','mesInicio','añoInicio','horaInicio','minInicio','diaFin','mesFin','añoFin','horaFin','minFin'])])


    getEnergia = lambda self,j,k,l: ((((j<<7)+k)<<7)+l)*0.015687283128499985/1000
    getCosPhi = lambda self,energia,I,V,periodo: energia/(I*V/1000*periodo/60)
    getTension = lambda self,V: V*0.008392393539741385
    getCorriente = lambda self,I: I*0.0050874767931571524
    getFlicker = lambda self,flickerRaw,calibrFlicker,V: ((flickerRaw*220*.02)/calibrFlicker)*(100/V)
    getThd = lambda self,V,thdRaw,calibrResiduo,calibrTension,vRaw,calibrThd: (100/V)*(abs(thdRaw-((calibrResiduo/calibrTension)*vRaw)))*18/calibrThd

    padding = True
    trifasico = True

class serie1605Monofasica:
    headerDat = 'Equipo Nro:\t{filename}\t\tCódigo de Cliente: \tID. Subestación:\t        \nNumero de Serie:\t{serie}\tPeriodo:\t{periodo} {Utiempo}.\nTensión:     \t{tension} V\t\tFactor de Corrección: {TV}\nCorriente:\t{corriente} Amp\t\tFactor de Corrección: {TI}\nDia inicio:\t{inicio}\tDia fin:\t{final}\nHora inicio:\t{horaInicio}\tHora fin:\t{horaFinal}\n\nFecha	Hora\tU\tU Max\tU Min\tTHD1\tFlicker\tAnormalidad\n\t\tV\tV\tV\t%\t%\t\n'
    name = '1605'

    largoErr = 7
    largoRegistro = 12
    variables = 5
    largosHeader = [36,8]
    largoHeaderBasura = 46
    byteSeparador = '\xff'

    regex = '(?P<calibr>)|(?P<basura>[^{byteSeparador}]{largoHeaderBasura})?(?P<header>[^{byteSeparador}]{largoHeader2}(?P<ffSeparated>{byteSeparador})?[^{byteSeparador}]{largoHeader1}(?={byteSeparador}))|(?P<reg>[^{byteSeparador}]{largoRegistro})|(?P<err>(?<={byteSeparador}).{largoErr}(?={byteSeparador}))'.format(byteSeparador=byteSeparador,largoErr='{%d}'%largoErr,largoHeader1='{%d}'%largosHeader[0],largoHeader2='{%d}'%largosHeader[1],largoHeaderBasura='{%d}'%largoHeaderBasura,largoRegistro='{%d}'%largoRegistro).encode('latin-1')

    maxValues = {'V':286,'Vmax':286,'Vmin':286,'thd':10,'flicker':2}
    
    formatoReg = '%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%s\n'
    formatoErr = '%s\t%s\n'
    
    unpackReg = 'IHHHH'
    regIndexes = {'flicker':0,'thd':1,'Vmin':2,'Vmax':3,'V':4}
    unpackHeader = '8s 1x 2s 2s2s2s 2s2s 3x 2s2s2s 2s2s 2x 8s'
    unpackHeaderSecundario = '8s 1x 2s 2s2s2s 2s2s 3x 2s2s2s 2s2s 3x 8s'
    unpackErr = '>BBBBBBB'

    headerMap = dict([reversed(x) for x in enumerate(['serie','periodo','diaInicio','mesInicio','añoInicio','horaInicio','minInicio','diaFin','mesFin','añoFin','horaFin','minFin','filename'])])

    getTension =  lambda self,x: x*0.00459564208984375
    getFlicker = lambda self,x:x*4.664380212779652e-09
    getThd = lambda self,x: x*0.0007659912109375

    padding = False
    trifasico = False
