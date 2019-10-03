class Serie():
    largoRegistroErr = 7
    largoHeaderData = 36
    deltaMax = 0.3
    vCap = 220*(1+deltaMax)
    fkrCap = 2.0
    thdCap = 10.0
    # FORMAT STRINGS
    errFormatString = '{}\t{}\t{}\n'
    regFormatStringTrif = '%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.3f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.3f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.3f\t%0.2f\t%0.3f\t%0.3f\t%s\n'
    # MAPAS
    errMap = ['codigo','S','M','H','d','m','y']
    headerMap = ['fileName','equipo','periodo','dStrt','mStrt','yStrt','hStrt','minStrt','dEnd','mEnd','yEnd','hEnd','minEnd']
    # UNPACK STRINGS
    unpackHeaderData = '>8s B 2s 2s2s2s2s2s 3x 2s2s2s2s2s 2x'
    unpackErr = '>BBBBBBB'

    def limitar(self,v,tv):
        vCap = self.vCap*tv
        return v if v<vCap else vCap

class Serie12(Serie):
    largoRegistro = 46
    largoHeaderCalibracion = 28
    iCoef = 0.008549096062779427
    eCoef = 0.15416666865348816
    unpackHeaderCalibracion = 'H H H xxxxxx H H H xxxxxxxxxx'# cV1, cV2, cV3, cThd, cRes, cFkr
    unpackReg = '>H H 3b 3b H HHH 3b 3b H HHH 3b 3b H HHH'
    regMap = ['fkrRaw','thdRaw','i3b1','i3b2','i3b3','e3b1','e3b2','e3b3','i3Raw','v3MinRaw','v3MaxRaw','v3Raw','i2b1','i2b2','i2b3','e2b1','e2b2','e2b3','i2Raw','v2MinRaw','v2MaxRaw','v2Raw','i1b1','i1b2','i1b3','e1b1','e1b2','e1b3','i1Raw','v1MinRaw','v1MaxRaw','v1Raw']
    regDatMap = ['v1', 'v1Max', 'v1Min', 'i1', 'phi1', 'e1', 'v2', 'v2Max', 'v2Min', 'i2', 'phi2', 'e2', 'v3', 'v3Max', 'v3Min', 'i3', 'phi3', 'e3', 'thd', 'fkr', 'pTotal','eTotal']
    calibrMap = ['cV1','cV2','cV3','cThd','cRes','cFkr']
    reverse = True
    
    regex = b'(?P<calibr>[^\xff]{28}(?=\xff))?\xff(?P<header>(?<=\xff)[^\xff]{36}(?=\xff))|(?P<err>(?<=\xff)[^\xff]{7}(?=\xff))|(?P<reg>[^\xff]{46})'

    regFormatString = '%s\t%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.2f\t%0.3f\t%0.3f\t%0.3f\t%s\n'
    headerFormatString = 'Equipo Nro:\t{}\t\tCódigo de Cliente: \tID. Subestación:\t{}\nNumero de Serie:\t{}\tPeriodo:\t{} {}.\nTensión:     \t{} V\t\tFactor de Corrección: {}\nCorriente:\t{} Amp\t\tFactor de Corrección: {}\nDia inicio:\t{}\tDia fin:\t{}\nHora inicio:\t{}\tHora fin:\t{}\n\nFecha\tHora\tU1\tU1 Max\tU1 Min\tIA1\tCosFi 1\tEA1\tU2\tU2 Max\tU2 Min\tIA2\tCosFi 2\tEA2\tU3\tU3 Max\tU3 Min\tIA3\tCosFi 3\tEA3\tTHD1\tFlicker1\tP Total\tEA Total\tAnormalidad\n\t\tV\tV\tV\tA\tp.u.\tKWh\tV\tV\tV\tA\tp.u.\tKWh\tV\tV\tV\tA\tp.u.\tKWh\t%\t%\tKW\tKWh\t\n'
    
    def analizarRegistroDat(self,reg,calibr,tv,ti,periodo):
        reg.v1 = reg.v1Raw*(220/calibr.cV1)*tv
        reg.v1Max = reg.v1MaxRaw*(220/calibr.cV1)*tv
        reg.v1Min = reg.v1MinRaw*(220/calibr.cV1)*tv
        if reg.v1 > reg.v1Max: reg.v1Max = reg.v1
        if reg.v1Min > reg.v1: reg.v1 = reg.v1Min
        reg.v1,reg.v1Max,reg.v1Min = (self.limitar(self,v,tv) for v in (reg.v1,reg.v1Max,reg.v1Min))

        reg.v2 = reg.v2Raw*(220/calibr.cV2)*tv
        reg.v2Max = reg.v2MaxRaw*(220/calibr.cV2)*tv
        reg.v2Min = reg.v2MinRaw*(220/calibr.cV2)*tv
        if reg.v2 > reg.v2Max: reg.v2Max = reg.v2
        if reg.v2Min > reg.v2: reg.v2 = reg.v2Min
        reg.v2,reg.v2Max,reg.v2Min = (self.limitar(self,v,tv) for v in (reg.v2,reg.v2Max,reg.v2Min))

        reg.v3 = reg.v3Raw*(220/calibr.cV3)*tv
        reg.v3Max = reg.v3MaxRaw*(220/calibr.cV3)*tv
        reg.v3Min = reg.v3MinRaw*(220/calibr.cV3)*tv
        if reg.v3 > reg.v3Max: reg.v3Max = reg.v3
        if reg.v3Min > reg.v3: reg.v3 = reg.v3Min
        reg.v3,reg.v3Max,reg.v3Min = (self.limitar(self,v,tv) for v in (reg.v3,reg.v3Max,reg.v3Min))

        reg.e1 = ((((reg.e1b1<<7)+reg.e1b2)<<7)+reg.e1b3)*self.eCoef/1000*tv*ti
        reg.e2 = ((((reg.e2b1<<7)+reg.e2b2)<<7)+reg.e2b3)*self.eCoef/1000*tv*ti
        reg.e3 = ((((reg.e3b1<<7)+reg.e3b2)<<7)+reg.e3b3)*self.eCoef/1000*tv*ti
        
        if reg.i1Raw: reg.i1 = reg.i1Raw*self.iCoef
        else:
            c1 = (((((reg.i1b1<<7)+reg.i1b2)<<7)+reg.i1b3)*3600/900)/1000*self.eCoef
            d1 = (((((reg.e1b1<<7)+reg.e1b2)<<7)+reg.e1b3)*3600/900)/1000*self.eCoef
            try:reg.i1 = ((d1*d1)+(c1*c1))**0.5*1000/reg.v1
            except ZeroDivisionError: reg.i1 = 0
        if reg.i2Raw: reg.i2 = reg.i2Raw*self.iCoef
        else:
            c2 = (((((reg.i2b1<<7)+reg.i2b2)<<7)+reg.i2b3)*3600/900)/1000*self.eCoef
            d2 = (((((reg.e2b1<<7)+reg.e2b2)<<7)+reg.e2b3)*3600/900)/1000*self.eCoef
            try:reg.i2 = ((d2*d2)+(c2*c2))**0.5*1000/reg.v2
            except ZeroDivisionError: reg.i2 = 0
        if reg.i3Raw: reg.i3 = reg.i3Raw*self.iCoef
        else:
            c3 = (((((reg.i3b1<<7)+reg.i3b2)<<7)+reg.i3b3)*3600/900)/1000*self.eCoef
            d3 = (((((reg.e3b1<<7)+reg.e3b2)<<7)+reg.e3b3)*3600/900)/1000*self.eCoef
            try:reg.i3 = ((d3*d3)+(c3*c3))**0.5*1000/reg.v3
            except ZeroDivisionError: reg.i3 = 0

        try:reg.phi1 = reg.e1/(reg.i1*reg.v1/1000*periodo/60)
        except ZeroDivisionError: reg.phi1 = 0.0
        try:reg.phi2 = reg.e2/(reg.i2*reg.v2/1000*periodo/60)
        except ZeroDivisionError: reg.phi2 = 0.0
        try:reg.phi3 = reg.e3/(reg.i3*reg.v3/1000*periodo/60)
        except ZeroDivisionError: reg.phi3 = 0.0

        reg.thd = abs((100/(reg.v1Raw*(220/calibr.cV1)))*((18/calibr.cThd)*(reg.thdRaw-((calibr.cRes/calibr.cV1)*reg.v1Raw))))
        reg.fkr = ((reg.fkrRaw*220*.02)/calibr.cFkr)*(100/reg.v1)

        reg.pTotal = (reg.v1*reg.i1*reg.phi1+reg.v2*reg.i2*reg.phi2+reg.v3*reg.i3*reg.phi3)/1000
        reg.eTotal = sum((reg.e1,reg.e2,reg.e3))

        return reg

class Serie1F(Serie):
    largoRegistro = 19
    largoHeaderCalibracion = 28
    unpackHeaderCalibracion = '12xHHHH8x' # cThd, cRes, cFkr, cV
    unpackReg = '>H H 9x HHH'
    regMap = ['fkrRaw','thdRaw','v1MinRaw','v1MaxRaw','v1Raw']
    regDatMap = ['v1', 'v1Max', 'v1Min', 'thd', 'fkr']
    calibrMap = ['cThd','cRes','cFkr','cV']
    reverse = True
    regex = b'(?P<calibr>[^\xff]{28}(?=\xff))?\xff(?P<header>(?<=\xff)[^\xff]{36}(?=\xff))|(?P<err>(?<=\xff)[^\xff]{7}(?=\xff))|(?P<reg>[^\xff]{19})'
    headerFormatString = 'Equipo Nro:\t{}\t\tCódigo de Cliente: \tID. Subestación:\t{}\nNumero de Serie:\t{}\tPeriodo:\t{} {}.\nTensión:     \t{} V\t\tFactor de Corrección: {}\nCorriente:\t{} Amp\t\tFactor de Corrección: {}\nDia inicio:\t{}\tDia fin:\t{}\nHora inicio:\t{}\tHora fin:\t{}\n\nFecha	Hora\tV\tV Max\tV Min\tTHD1\tFlicker\tAnormalidad\n\t\tV\tV\tV\t%\t%\t\n'
    regFormatString = '%s\t%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%s\n'

    def analizarRegistroDat(self,reg,calibr,tv,ti,periodo):
        reg.v1 = reg.v1Raw*(220/calibr.cV)*tv
        reg.v1Max = reg.v1MaxRaw*(220/calibr.cV)*tv
        reg.v1Min = reg.v1MinRaw*(220/calibr.cV)*tv
        if reg.v1 > reg.v1Max: reg.v1Max = reg.v1
        if reg.v1Min > reg.v1: reg.v1 = reg.v1Min
        reg.v1,reg.v1Max,reg.v1Min = (self.limitar(self,v,tv) for v in (reg.v1,reg.v1Max,reg.v1Min))
        reg.thd = abs((100/(reg.v1Raw*(220/calibr.cV)))*((18/calibr.cThd)*(reg.thdRaw-((calibr.cRes/calibr.cV)*reg.v1Raw))))
        reg.fkr = ((reg.fkrRaw*220*.02)/calibr.cFkr)*(100/reg.v1)
        return reg
    
class Serie04(Serie):
    largoRegistro = 10
    largoHeaderCalibracion = 10
    unpackHeaderCalibracion = 'HxxHHH'
    unpackReg = '>HHHHH'
    regMap = ['fkrRaw','thdRaw','v1MinRaw','v1MaxRaw','v1Raw']
    regDatMap = ['v1', 'v1Max', 'v1Min', 'thd', 'fkr']
    calibrMap = ['cV','cThd','cRes','cFkr']
    reverse = True
    regex = b'(?P<calibr>[^\xff]{10}(?=\xff))?\xff(?P<header>(?<=\xff)[^\xff]{36}(?=\xff))|(?P<err>(?<=\xff)[^\xff]{7}(?=\xff))|(?P<reg>[^\xff]{10})'
    headerFormatString = 'Equipo Nro:\t{}\t\tCódigo de Cliente: \tID. Subestación:\t{}\nNumero de Serie:\t{}\tPeriodo:\t{} {}.\nTensión:     \t{} V\t\tFactor de Corrección: {}\nCorriente:\t{} Amp\t\tFactor de Corrección: {}\nDia inicio:\t{}\tDia fin:\t{}\nHora inicio:\t{}\tHora fin:\t{}\n\nFecha	Hora\tV\tV Max\tV Min\tTHD1\tFlicker\tAnormalidad\n\t\tV\tV\tV\t%\t%\t\n'
    regFormatString = '%s\t%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%s\n'

    def analizarRegistroDat(self,reg,calibr,tv,ti,periodo):
        reg.v1 = reg.v1Raw*(220/calibr.cV)*tv
        reg.v1Max = reg.v1MaxRaw*(220/calibr.cV)*tv
        reg.v1Min = reg.v1MinRaw*(220/calibr.cV)*tv
        if reg.v1 > reg.v1Max: reg.v1Max = reg.v1
        if reg.v1Min > reg.v1: reg.v1 = reg.v1Min
        reg.v1,reg.v1Max,reg.v1Min = (self.limitar(self,v,tv) for v in (reg.v1,reg.v1Max,reg.v1Min))
        reg.thd = abs((100/(reg.v1Raw*(220/calibr.cV)))*((18/calibr.cThd)*(reg.thdRaw-((calibr.cRes/calibr.cV)*reg.v1Raw))))
        reg.fkr = ((reg.fkrRaw*220*.02)/calibr.cFkr)*(100/reg.v1)
        return reg

class Serie0A(Serie):
    largoRegistro = 15
    largoHeaderCalibracion = 28
    unpackHeaderCalibracion = '12xHHHH8x'
    unpackReg = '>HH 5x HHH'
    regMap = ['fkrRaw','thdRaw','v1MinRaw','v1MaxRaw','v1Raw']
    regDatMap = ['v1', 'v1Max', 'v1Min', 'thd', 'fkr']
    calibrMap = ['cThd','cRes','cFkr','cV']
    reverse = True
    regex = b'(?P<calibr>[^\xff]{28}(?=\xff))?\xff(?P<header>(?<=\xff)[^\xff]{36}(?=\xff))|(?P<err>(?<=\xff)[^\xff]{7}(?=\xff))|(?P<reg>[^\xff]{15})'
    headerFormatString = 'Equipo Nro:\t{}\t\tCódigo de Cliente: \tID. Subestación:\t{}\nNumero de Serie:\t{}\tPeriodo:\t{} {}.\nTensión:     \t{} V\t\tFactor de Corrección: {}\nCorriente:\t{} Amp\t\tFactor de Corrección: {}\nDia inicio:\t{}\tDia fin:\t{}\nHora inicio:\t{}\tHora fin:\t{}\n\nFecha	Hora\tV\tV Max\tV Min\tTHD1\tFlicker\tAnormalidad\n\t\tV\tV\tV\t%\t%\t\n'
    regFormatString = '%s\t%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%s\n'

    def analizarRegistroDat(self,reg,calibr,tv,ti,periodo):
        reg.v1 = reg.v1Raw*(220/calibr.cV)*tv
        reg.v1Max = reg.v1MaxRaw*(220/calibr.cV)*tv
        reg.v1Min = reg.v1MinRaw*(220/calibr.cV)*tv
        if reg.v1 > reg.v1Max: reg.v1Max = reg.v1
        if reg.v1Min > reg.v1: reg.v1 = reg.v1Min
        reg.v1,reg.v1Max,reg.v1Min = (self.limitar(self,v,tv) for v in (reg.v1,reg.v1Max,reg.v1Min))
        reg.thd = abs((100/(reg.v1Raw*(220/calibr.cV)))*((18/calibr.cThd)*(reg.thdRaw-((calibr.cRes/calibr.cV)*reg.v1Raw))))
        reg.fkr = ((reg.fkrRaw*220*.02)/calibr.cFkr)*(100/reg.v1)
        return reg

class Serie20(Serie): pass

class Serie15(Serie):
    largoRegistro = 12
    largoHeaderCalibracion = 54
    unpackHeaderCalibracion = '>17s HHHHH 27x' # cThd, cRes, cFkr, cV
    unpackReg = '2xHHHHH'
    regMap = ['fkrRaw','thdRaw','v1MinRaw','v1MaxRaw','v1Raw']
    regDatMap = ['v1', 'v1Max', 'v1Min', 'thd', 'fkr']
    calibrMap = ['fileName','cThd','cRes','cFkr','cV']
    headerMap = ['serie','equipo','periodo','dStrt','mStrt','yStrt','hStrt','minStrt','dEnd','mEnd','yEnd','hEnd','minEnd']
    reverse = True
    regex = b'(?P<bogus>(?<=\xff)[^\xff]{90}(?=\xff))|(?P<calibr>[^\xff]{54}(?=\xff))?\xff(?P<header>(?<=\xff)[^\xff]{36}(?=\xff))|(?P<err>(?<=\xff)[^\xff]{7}(?=\xff))|(?P<reg>[^\xff]{12})'
    headerFormatString = 'Equipo Nro:\t{}\t\tCódigo de Cliente: \tID. Subestación:\t{}\nNumero de Serie:\t{}\tPeriodo:\t{} {}.\nTensión:     \t{} V\t\tFactor de Corrección: {}\nCorriente:\t{} Amp\t\tFactor de Corrección: {}\nDia inicio:\t{}\tDia fin:\t{}\nHora inicio:\t{}\tHora fin:\t{}\n\nFecha	Hora\tV\tV Max\tV Min\tTHD1\tFlicker\tAnormalidad\n\t\tV\tV\tV\t%\t%\t\n'
    regFormatString = '%s\t%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%s\n'

    def analizarRegistroDat(self,reg,calibr,tv,ti,periodo):
        reg.v1 = ((300*reg.v1Raw)/65278)*tv
        reg.v1Max = ((300*reg.v1MaxRaw)/65278)*tv
        reg.v1Min = ((300*reg.v1MinRaw)/65278)*tv
        if reg.v1 > reg.v1Max: reg.v1Max = reg.v1
        if reg.v1Min > reg.v1: reg.v1 = reg.v1Min
        reg.v1,reg.v1Max,reg.v1Min = (self.limitar(self,v,tv) for v in (reg.v1,reg.v1Max,reg.v1Min))
        reg.thd = reg.thdRaw*(tv*tv)*50/65278
        reg.fkr = reg.fkrRaw*(tv*tv)*20/65278
        return reg

class Serie13(Serie): pass
