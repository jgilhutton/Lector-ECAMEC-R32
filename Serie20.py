from Tools import limitar,calcularCantidadDeBytesMolestos
from re import search


class Serie20:
    largoRegistro = 54
    largoHeaderData = 36
    largoHeaderCalibracion = 37
    largoRegistroErr = 7
    iCoef = 6881
    eCoef = 366 / 23331
    deltaMax = 1.3
    fkrCap = 2.0
    thdCap = 10.0
    phiCap = 1.0
    reverse = True
    # FORMAT STRINGS
    headerFormatString = 'Equipo Nro:\t{}\t\tCódigo de Cliente: \tID. Subestación:\t{}\nNumero de Serie:\t{}\tPeriodo:\t{} {}.\nTensión:     \t{} V\t\tFactor de Corrección: {}\nCorriente:\t{} Amp\t\tFactor de Corrección: {}\nDia inicio:\t{}\tDia fin:\t{}\nHora inicio:\t{}\tHora fin:\t{}\n\nFecha\tHora\tU1\tU1 Max\tU1 Min\tIA1\tCosFi 1\tEA1\tU2\tU2 Max\tU2 Min\tIA2\tCosFi 2\tEA2\tU3\tU3 Max\tU3 Min\tIA3\tCosFi 3\tEA3\tTHD1\tFlicker1\tP Total\tEA Total\tAnormalidad\n\t\tV\tV\tV\tA\tp.u.\tKWh\tV\tV\tV\tA\tp.u.\tKWh\tV\tV\tV\tA\tp.u.\tKWh\t%\t%\tKW\tKWh\t\n'
    regFormatString = '%s\t%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.3f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.3f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.3f\t%0.2f\t%0.3f\t%0.3f\t%0.3f\t%s\n'
    errFormatString = '{}\t{}\t{}\n'
    # MAPAS
    regMap = ['fkrRaw', 'thdRaw3', 'e3b1', 'e3b2', 'e3b3', 'i3MinRaw', 'i3MaxRaw', 'i3Raw', 'v3MinRaw', 'v3MaxRaw',
              'v3Raw', 'thdRaw2', 'e2b1', 'e2b2', 'e2b3', 'i2MinRaw', 'i2MaxRaw', 'i2Raw', 'v2MinRaw', 'v2MaxRaw',
              'v2Raw', 'thdRaw1', 'e1b1', 'e1b2', 'e1b3', 'i1MinRaw', 'i1MaxRaw', 'i1Raw', 'v1MinRaw', 'v1MaxRaw',
              'v1Raw']
    regDatMap = ['v1', 'v1Max', 'v1Min', 'i1', 'phi1', 'e1', 'v2', 'v2Max', 'v2Min', 'i2', 'phi2', 'e2', 'v3', 'v3Max',
                 'v3Min', 'i3', 'phi3', 'e3', 'thd', 'fkr', 'pTotal', 'eTotal']
    calibrMap = ['fileName', 'cThd1', 'cRes1', 'cThd3', 'cRes3', 'cThd2', 'cRes2', 'cFkr']
    headerMap = ['serie', 'equipo', 'periodo', 'dStrt', 'mStrt', 'yStrt', 'hStrt', 'minStrt', 'vNomRaw', 'iNomRaw',
                 'dEnd', 'mEnd', 'yEnd', 'hEnd', 'minEnd']
    errMap = ['codigo', 'S', 'M', 'H', 'd', 'm', 'y']
    # UNPACK STRINGS
    unpackReg = '>x H H 3b HHH HHH  H 3b HHH HHH  H 3b HHH HHH'
    unpackHeaderCalibracion = '=16s xxxxx H H H H H H H xx'  # thd1 res1 thd3 res3 thd 2 res2 fkr
    unpackHeaderData = '>8s B 2s 2s2s2s2s2s x B B 2s2s2s2s2s 2x'
    unpackErr = '>BBBBBBB'

    def setRegex(self,raro=False):
        if raro:
            formatTuple = (self.qBytesMolestos,self.largoHeaderCalibracion, self.largoRegistroErr, self.largoRegistro)
        else:
            formatTuple = (self.qBytesMolestos,self.largoHeaderCalibracion, self.largoHeaderData, self.largoRegistroErr, self.largoRegistro)
        self.regex = self.regex % formatTuple

    def setVariante(self, rawData):
        self.qBytesMolestos = calcularCantidadDeBytesMolestos(self)
        initRe = '(?P<headerOk>(?<=ÿ)[^ÿ]{36})(?P<calibrFalso>[^ÿ]{21}(?=ÿ))'
        testRe = search(bytes(initRe, encoding='latin1'), rawData)
        if testRe:
            self.regex = '^(?P<bogus>[^\xff]{%s})|(?P<headerOk>(?<=\xff[^\xff]{21})[^\xff]{27}\x91[^\xff]{8}(?=\xff))|(?P<calibr>(?<=\xff)[^\xff]{%s}(?=\xff))|(?P<err>(?<=\xff)[^\xff]{%s}(?=\xff))|(?P<reg>(?!.+\x31\x91.+)[^\xff]{%s})' # Medio hardcodeado...
            self.setRegex(raro=True)
        else:
            self.regex = '^(?P<bogus>[^\xff]{%s})|(?P<calibr>[^\xff]{%s}(?=\xff))?\xff(?P<header>(?<=\xff)[^\xff]{%s}(?=\xff))|(?P<err>(?<=\xff)[^\xff]{%s}(?=\xff))|(?P<reg>[^\xff]{%s})'
            self.setRegex(raro=False)

    def analizarRegistroDat(self, reg, calibr, tv, ti, header):
        from math import floor
        calibr.cV = 26214 / (220 / header.vNom)
        reg.v1 = reg.v1Raw * (header.vNom / calibr.cV) * tv
        reg.v1Max = reg.v1MaxRaw * (header.vNom / calibr.cV) * tv
        reg.v1Min = reg.v1MinRaw * (header.vNom / calibr.cV) * tv
        if reg.v1 > reg.v1Max: reg.v1Max = reg.v1
        if reg.v1Min > reg.v1: reg.v1 = reg.v1Min
        reg.v1, reg.v1Max, reg.v1Min = (limitar(v, 0, header.vNom * self.deltaMax * tv) for v in
                                        (reg.v1, reg.v1Max, reg.v1Min))

        reg.v2 = reg.v2Raw * (header.vNom / calibr.cV) * tv
        reg.v2Max = reg.v2MaxRaw * (header.vNom / calibr.cV) * tv
        reg.v2Min = reg.v2MinRaw * (header.vNom / calibr.cV) * tv
        if reg.v2 > reg.v2Max: reg.v2Max = reg.v2
        if reg.v2Min > reg.v2: reg.v2 = reg.v2Min
        reg.v2, reg.v2Max, reg.v2Min = (limitar(v, 0, header.vNom * self.deltaMax * tv) for v in
                                        (reg.v2, reg.v2Max, reg.v2Min))

        reg.v3 = reg.v3Raw * (header.vNom / calibr.cV) * tv
        reg.v3Max = reg.v3MaxRaw * (header.vNom / calibr.cV) * tv
        reg.v3Min = reg.v3MinRaw * (header.vNom / calibr.cV) * tv
        if reg.v3 > reg.v3Max: reg.v3Max = reg.v3
        if reg.v3Min > reg.v3: reg.v3 = reg.v3Min
        reg.v3, reg.v3Max, reg.v3Min = (limitar(v, 0, header.vNom * self.deltaMax * tv) for v in
                                        (reg.v3, reg.v3Max, reg.v3Min))

        reg.i1 = reg.i1Raw * (header.iNom / self.iCoef)
        reg.i1Max = reg.i1MaxRaw * (header.iNom / self.iCoef)
        reg.i1Min = reg.i1MinRaw * (header.iNom / self.iCoef)
        reg.i2 = reg.i2Raw * (header.iNom / self.iCoef)
        reg.i2Max = reg.i2MaxRaw * (header.iNom / self.iCoef)
        reg.i2Min = reg.i2MinRaw * (header.iNom / self.iCoef)
        reg.i3 = reg.i3Raw * (header.iNom / self.iCoef)
        reg.i3Max = reg.i3MaxRaw * (header.iNom / self.iCoef)
        reg.i3Min = reg.i3MinRaw * (header.iNom / self.iCoef)

        if reg.i1 > reg.i1Max: reg.i1Max = reg.i1
        if reg.i1Min > reg.i1: reg.i1 = reg.i1Min
        if reg.i2 > reg.i2Max: reg.i2Max = reg.i2
        if reg.i2Min > reg.i2: reg.i2 = reg.i2Min
        if reg.i3 > reg.i3Max: reg.i3Max = reg.i3
        if reg.i3Min > reg.i3: reg.i3 = reg.i3Min

        calibr.cV = header.vNom
        try:
            thd1 = abs((100 / reg.v1) * (
                    (18 / (calibr.cThd1 - calibr.cRes1)) * (reg.thdRaw1 - (floor(calibr.cRes1 / calibr.cV) * reg.v1))))
        except ZeroDivisionError:
            thd1 = 0.0
        reg.thd = limitar(thd1, 0, self.thdCap)
        # thd2 = abs((100 / reg.v2) * (
        #         (18 / (calibr.cThd2-calibr.cRes2)) * (reg.thdRaw2 - (floor(calibr.cRes2 / calibr.cV) * reg.v2))))
        # thd3 = abs((100 / reg.v3) * (
        #         (18 / (calibr.cThd3-calibr.cRes3)) * (reg.thdRaw3 - (floor(calibr.cRes3 / calibr.cV) * reg.v3))))

        reg.e1 = ((((reg.e1b1 << 7) + reg.e1b2) << 7) + reg.e1b3) * (header.iNom / 35) * (self.eCoef / 1000) * tv * ti
        reg.e2 = ((((reg.e2b1 << 7) + reg.e2b2) << 7) + reg.e2b3) * (header.iNom / 35) * (self.eCoef / 1000) * tv * ti
        reg.e3 = ((((reg.e3b1 << 7) + reg.e3b2) << 7) + reg.e3b3) * (header.iNom / 35) * (self.eCoef / 1000) * tv * ti

        try:
            reg.phi1 = reg.e1 / (reg.i1 * reg.v1 / 1000 * header.periodo / 60)
        except ZeroDivisionError:
            reg.phi1 = 0.0
        try:
            reg.phi2 = reg.e2 / (reg.i2 * reg.v2 / 1000 * header.periodo / 60)
        except ZeroDivisionError:
            reg.phi2 = 0.0
        try:
            reg.phi3 = reg.e3 / (reg.i3 * reg.v3 / 1000 * header.periodo / 60)
        except ZeroDivisionError:
            reg.phi3 = 0.0
        reg.phi1, reg.phi2, reg.phi3 = (limitar(phi, 0, self.phiCap) for phi in
                                        (reg.phi1, reg.phi2, reg.phi3))

        try:
            fkr = ((reg.fkrRaw * header.vNom * .02) / calibr.cFkr) * (100 / reg.v1 * tv)
        except ZeroDivisionError:
            fkr = 0.0
        reg.fkr = limitar(fkr, 0, self.fkrCap) * (220 / header.vNom)

        reg.pTotal = (reg.v1 * reg.i1 * reg.phi1 + reg.v2 * reg.i2 * reg.phi2 + reg.v3 * reg.i3 * reg.phi3) / 1000
        reg.eTotal = sum((reg.e1, reg.e2, reg.e3))

        return reg
