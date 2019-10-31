class Serie:
    largoRegistroErr = 7
    largoHeaderData = 36
    deltaMax = 0.3
    vCap = 220 * (1 + deltaMax)
    iCoef = 4095
    eCoef = 370 / 2400
    fkrCap = 2.0
    thdCap = 10.0
    # FORMAT STRINGS
    errFormatString = '{}\t{}\t{}\n'
    regFormatStringTrif = '%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.3f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.3f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.3f\t%0.2f\t%0.3f\t%0.3f\t%s\n'
    # MAPAS
    errMap = ['codigo', 'S', 'M', 'H', 'd', 'm', 'y']
    headerMap = ['fileName', 'equipo', 'periodo', 'dStrt', 'mStrt', 'yStrt', 'hStrt', 'minStrt', 'vNomRaw', 'iNomRaw',
                 'dEnd', 'mEnd', 'yEnd', 'hEnd', 'minEnd']
    # UNPACK STRINGS
    unpackHeaderData = '>8s B 2s 2s2s2s2s2s x B B 2s2s2s2s2s 2x'
    unpackErr = '>BBBBBBB'

    limitar = lambda self, value, cap: value if value < cap else cap


class Serie12(Serie):
    largoRegistro = 46
    largoHeaderCalibracion = 28
    iCoef = 4095
    eCoef = 370 / 2400
    unpackHeaderCalibracion = 'H H H xxxxxx H H H xxxxxxxxxx'  # cV1, cV2, cV3, cThd, cRes, cFkr
    unpackReg = '>H H 3b 3b H HHH 3b 3b H HHH 3b 3b H HHH'
    regMap = ['fkrRaw', 'thdRaw', 'i3b1', 'i3b2', 'i3b3', 'e3b1', 'e3b2', 'e3b3', 'i3Raw', 'v3MinRaw', 'v3MaxRaw',
              'v3Raw', 'i2b1', 'i2b2', 'i2b3', 'e2b1', 'e2b2', 'e2b3', 'i2Raw', 'v2MinRaw', 'v2MaxRaw', 'v2Raw', 'i1b1',
              'i1b2', 'i1b3', 'e1b1', 'e1b2', 'e1b3', 'i1Raw', 'v1MinRaw', 'v1MaxRaw', 'v1Raw']
    regDatMap = ['v1', 'v1Max', 'v1Min', 'i1', 'phi1', 'e1', 'v2', 'v2Max', 'v2Min', 'i2', 'phi2', 'e2', 'v3', 'v3Max',
                 'v3Min', 'i3', 'phi3', 'e3', 'thd', 'fkr', 'pTotal', 'eTotal']
    calibrMap = ['cV1', 'cV2', 'cV3', 'cThd', 'cRes', 'cFkr']
    reverse = True

    regex = b'(?P<calibr>[^\xff]{28}(?=\xff))?\xff(?P<header>(?<=\xff)[^\xff]{36}(?=\xff))|(?P<err>(?<=\xff)[^\xff]{7}(?=\xff))|(?P<reg>[^\xff]{46})'

    regFormatString = '%s\t%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.2f\t%0.3f\t%0.3f\t%0.3f\t%s\n'
    headerFormatString = 'Equipo Nro:\t{}\t\tCódigo de Cliente: \tID. Subestación:\t{}\nNumero de Serie:\t{}\tPeriodo:\t{} {}.\nTensión:     \t{} V\t\tFactor de Corrección: {}\nCorriente:\t{} Amp\t\tFactor de Corrección: {}\nDia inicio:\t{}\tDia fin:\t{}\nHora inicio:\t{}\tHora fin:\t{}\n\nFecha\tHora\tU1\tU1 Max\tU1 Min\tIA1\tCosFi 1\tEA1\tU2\tU2 Max\tU2 Min\tIA2\tCosFi 2\tEA2\tU3\tU3 Max\tU3 Min\tIA3\tCosFi 3\tEA3\tTHD1\tFlicker1\tP Total\tEA Total\tAnormalidad\n\t\tV\tV\tV\tA\tp.u.\tKWh\tV\tV\tV\tA\tp.u.\tKWh\tV\tV\tV\tA\tp.u.\tKWh\t%\t%\tKW\tKWh\t\n'

    def analizarRegistroDat(self, reg, calibr, tv, ti, header):
        reg.v1, reg.v1Max, reg.v1Min = (x * (header.vNom / calibr.cV1) * tv for x in
                                        (reg.v1Raw, reg.v1MaxRaw, reg.v1MinRaw))
        if reg.v1 > reg.v1Max: reg.v1Max = reg.v1
        if reg.v1Min > reg.v1: reg.v1 = reg.v1Min
        reg.v1, reg.v1Max, reg.v1Min = (self.limitar(self, v, self.vCap * tv) for v in
                                        (reg.v1, reg.v1Max, reg.v1Min))

        reg.v2, reg.v2Max, reg.v2Min = (x * (header.vNom / calibr.cV2) * tv for x in
                                        (reg.v2Raw, reg.v2MaxRaw, reg.v2MinRaw))
        if reg.v2 > reg.v2Max: reg.v2Max = reg.v2
        if reg.v2Min > reg.v2: reg.v2 = reg.v2Min
        reg.v2, reg.v2Max, reg.v2Min = (self.limitar(self, v, self.vCap * tv) for v in
                                        (reg.v2, reg.v2Max, reg.v2Min))

        reg.v3, reg.v3Max, reg.v3Min = (x * (header.vNom / calibr.cV3) * tv for x in
                                        (reg.v3Raw, reg.v3MaxRaw, reg.v3MinRaw))
        if reg.v3 > reg.v3Max: reg.v3Max = reg.v3
        if reg.v3Min > reg.v3: reg.v3 = reg.v3Min
        reg.v3, reg.v3Max, reg.v3Min = (self.limitar(self, v, self.vCap * tv) for v in
                                        (reg.v3, reg.v3Max, reg.v3Min))

        reg.e1 = ((((reg.e1b1 << 7) + reg.e1b2) << 7) + reg.e1b3) * self.eCoef / 1000 * tv * ti
        reg.e2 = ((((reg.e2b1 << 7) + reg.e2b2) << 7) + reg.e2b3) * self.eCoef / 1000 * tv * ti
        reg.e3 = ((((reg.e3b1 << 7) + reg.e3b2) << 7) + reg.e3b3) * self.eCoef / 1000 * tv * ti

        reg.i1 = reg.i1Raw * (header.iNom / self.iCoef)
        c1 = (((((reg.i1b1 << 7) + reg.i1b2) << 7) + reg.i1b3) * 60 / 15) / 1000 * self.eCoef
        d1 = (((((reg.e1b1 << 7) + reg.e1b2) << 7) + reg.e1b3) * 60 / 15) / 1000 * self.eCoef
        try:
            reg.i1p = ((d1 * d1) + (c1 * c1)) ** 0.5 * 1000 / reg.v1
        except ZeroDivisionError:
            reg.i1p = 0
        if reg.i1 == 0:
            reg.i1 = reg.i1p

        reg.i2 = reg.i2Raw * (header.iNom / self.iCoef)
        c2 = (((((reg.i2b1 << 7) + reg.i2b2) << 7) + reg.i2b3) * 60 / 15) / 1000 * self.eCoef
        d2 = (((((reg.e2b1 << 7) + reg.e2b2) << 7) + reg.e2b3) * 60 / 15) / 1000 * self.eCoef
        try:
            reg.i2p = ((d2 * d2) + (c2 * c2)) ** 0.5 * 1000 / reg.v2
        except ZeroDivisionError:
            reg.i2p = 0
        if reg.i2 == 0:
            reg.i2 = reg.i2p

        reg.i3 = reg.i3Raw * (header.iNom / self.iCoef)
        c3 = (((((reg.i3b1 << 7) + reg.i3b2) << 7) + reg.i3b3) * 60 / 15) / 1000 * self.eCoef
        d3 = (((((reg.e3b1 << 7) + reg.e3b2) << 7) + reg.e3b3) * 60 / 15) / 1000 * self.eCoef
        try:
            reg.i3p = ((d3 * d3) + (c3 * c3)) ** 0.5 * 1000 / reg.v3
        except ZeroDivisionError:
            reg.i3p = 0
        if reg.i3 == 0:
            reg.i3 = reg.i3p

        try:
            reg.phi1 = reg.e1 / (reg.i1p * reg.v1 / 1000 * header.periodo / 60)
        except ZeroDivisionError:
            reg.phi1 = 0.0
        try:
            reg.phi2 = reg.e2 / (reg.i2p * reg.v2 / 1000 * header.periodo / 60)
        except ZeroDivisionError:
            reg.phi2 = 0.0
        try:
            reg.phi3 = reg.e3 / (reg.i3p * reg.v3 / 1000 * header.periodo / 60)
        except ZeroDivisionError:
            reg.phi3 = 0.0

        thd = abs((100 / (reg.v1Raw * (header.vNom / calibr.cV1))) * (
                (18 / calibr.cThd) * (reg.thdRaw - ((calibr.cRes / calibr.cV1) * reg.v1Raw))))
        fkr = ((reg.fkrRaw * header.vNom * .02) / calibr.cFkr) * (100 / reg.v1 * tv)
        reg.thd = self.limitar(self, thd, self.thdCap)
        reg.fkr = self.limitar(self, fkr, self.fkrCap)

        reg.pTotal = (reg.v1 * reg.i1 * reg.phi1 + reg.v2 * reg.i2 * reg.phi2 + reg.v3 * reg.i3 * reg.phi3) / 1000
        reg.eTotal = sum((reg.e1, reg.e2, reg.e3))

        return reg


class Serie1F(Serie):
    largoRegistro = 19
    largoHeaderCalibracion = 28
    unpackHeaderCalibracion = '12xHHHH8x'  # cThd, cRes, cFkr, cV
    unpackReg = '>H H 9x HHH'
    regMap = ['fkrRaw', 'thdRaw', 'v1MinRaw', 'v1MaxRaw', 'v1Raw']
    regDatMap = ['v1', 'v1Max', 'v1Min', 'thd', 'fkr']
    calibrMap = ['cThd', 'cRes', 'cFkr', 'cV']
    reverse = True
    regex = b'(?P<calibr>[^\xff]{28}(?=\xff))?\xff(?P<header>(?<=\xff)[^\xff]{36}(?=\xff))|(?P<err>(?<=\xff)[^\xff]{7}(?=\xff))|(?P<reg>[^\xff]{19})'
    headerFormatString = 'Equipo Nro:\t{}\t\tCódigo de Cliente: \tID. Subestación:\t{}\nNumero de Serie:\t{}\tPeriodo:\t{} {}.\nTensión:     \t{} V\t\tFactor de Corrección: {}\nCorriente:\t{} Amp\t\tFactor de Corrección: {}\nDia inicio:\t{}\tDia fin:\t{}\nHora inicio:\t{}\tHora fin:\t{}\n\nFecha	Hora\tV\tV Max\tV Min\tTHD1\tFlicker\tAnormalidad\n\t\tV\tV\tV\t%\t%\t\n'
    regFormatString = '%s\t%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%s\n'

    def analizarRegistroDat(self, reg, calibr, tv, ti, header):
        reg.v1 = reg.v1Raw * (header.vNom / calibr.cV) * tv
        reg.v1Max = reg.v1MaxRaw * (header.vNom / calibr.cV) * tv
        reg.v1Min = reg.v1MinRaw * (header.vNom / calibr.cV) * tv
        if reg.v1 > reg.v1Max: reg.v1 = reg.v1Max
        if reg.v1Min > reg.v1: reg.v1Min = reg.v1
        reg.v1, reg.v1Max, reg.v1Min = (self.limitar(self, v, self.vCap * tv) for v in (reg.v1, reg.v1Max, reg.v1Min))
        thd = abs((100 / (reg.v1Raw * (header.vNom / calibr.cV))) * (
                (18 / calibr.cThd) * (reg.thdRaw - ((calibr.cRes / calibr.cV) * reg.v1Raw))))
        fkr = ((reg.fkrRaw * header.vNom * .02) / calibr.cFkr) * (100 / reg.v1 * tv)
        reg.thd = self.limitar(self, thd, self.thdCap)
        reg.fkr = self.limitar(self, fkr, self.fkrCap)
        return reg


class Serie04(Serie):
    largoRegistro = 10
    largoHeaderCalibracion = 10
    unpackHeaderCalibracion = 'HxxHHH'
    unpackReg = '>HHHHH'
    regMap = ['fkrRaw', 'thdRaw', 'v1MinRaw', 'v1MaxRaw', 'v1Raw']
    regDatMap = ['v1', 'v1Max', 'v1Min', 'thd', 'fkr']
    calibrMap = ['cV', 'cThd', 'cRes', 'cFkr']
    reverse = True
    regex = b'(?P<calibr>[^\xff]{10}(?=\xff))?\xff(?P<header>(?<=\xff)[^\xff]{36}(?=\xff))|(?P<err>(?<=\xff)[^\xff]{7}(?=\xff))|(?P<reg>[^\xff]{10})'
    headerFormatString = 'Equipo Nro:\t{}\t\tCódigo de Cliente: \tID. Subestación:\t{}\nNumero de Serie:\t{}\tPeriodo:\t{} {}.\nTensión:     \t{} V\t\tFactor de Corrección: {}\nCorriente:\t{} Amp\t\tFactor de Corrección: {}\nDia inicio:\t{}\tDia fin:\t{}\nHora inicio:\t{}\tHora fin:\t{}\n\nFecha	Hora\tV\tV Max\tV Min\tTHD1\tFlicker\tAnormalidad\n\t\tV\tV\tV\t%\t%\t\n'
    regFormatString = '%s\t%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%s\n'

    def analizarRegistroDat(self, reg, calibr, tv, ti, header):
        reg.v1 = reg.v1Raw * (header.vNom / calibr.cV) * tv
        reg.v1Max = reg.v1MaxRaw * (header.vNom / calibr.cV) * tv
        reg.v1Min = reg.v1MinRaw * (header.vNom / calibr.cV) * tv
        if reg.v1 > reg.v1Max: reg.v1Max = reg.v1
        if reg.v1Min > reg.v1: reg.v1 = reg.v1Min
        reg.v1, reg.v1Max, reg.v1Min = (self.limitar(self, v, self.vCap * tv) for v in (reg.v1, reg.v1Max, reg.v1Min))
        thd = abs((100 / (reg.v1Raw * (header.vNom / calibr.cV))) * (
                (18 / calibr.cThd) * (reg.thdRaw - ((calibr.cRes / calibr.cV) * reg.v1Raw))))
        fkr = ((reg.fkrRaw * header.vNom * .02) / calibr.cFkr) * (100 / reg.v1 * tv)
        reg.thd = self.limitar(self, thd, self.thdCap)
        reg.fkr = self.limitar(self, fkr, self.fkrCap)
        return reg


class Serie0A(Serie):
    largoRegistro = 15
    largoHeaderCalibracion = 28
    unpackHeaderCalibracion = '12xHHHH8x'
    unpackReg = '>HH 5x HHH'
    regMap = ['fkrRaw', 'thdRaw', 'v1MinRaw', 'v1MaxRaw', 'v1Raw']
    regDatMap = ['v1', 'v1Max', 'v1Min', 'thd', 'fkr']
    calibrMap = ['cThd', 'cRes', 'cFkr', 'cV']
    reverse = True
    regex = b'(?P<calibr>[^\xff]{28}(?=\xff))?\xff(?P<header>(?<=\xff)[^\xff]{36}(?=\xff))|(?P<err>(?<=\xff)[^\xff]{7}(?=\xff))|(?P<reg>[^\xff]{15})'
    headerFormatString = 'Equipo Nro:\t{}\t\tCódigo de Cliente: \tID. Subestación:\t{}\nNumero de Serie:\t{}\tPeriodo:\t{} {}.\nTensión:     \t{} V\t\tFactor de Corrección: {}\nCorriente:\t{} Amp\t\tFactor de Corrección: {}\nDia inicio:\t{}\tDia fin:\t{}\nHora inicio:\t{}\tHora fin:\t{}\n\nFecha	Hora\tV\tV Max\tV Min\tTHD1\tFlicker\tAnormalidad\n\t\tV\tV\tV\t%\t%\t\n'
    regFormatString = '%s\t%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%s\n'

    def analizarRegistroDat(self, reg, calibr, tv, ti, header):
        reg.v1 = reg.v1Raw * (header.vNom / calibr.cV) * tv
        reg.v1Max = reg.v1MaxRaw * (header.vNom / calibr.cV) * tv
        reg.v1Min = reg.v1MinRaw * (header.vNom / calibr.cV) * tv
        if reg.v1 > reg.v1Max: reg.v1Max = reg.v1
        if reg.v1Min > reg.v1: reg.v1 = reg.v1Min
        reg.v1, reg.v1Max, reg.v1Min = (self.limitar(self, v, self.vCap * tv) for v in (reg.v1, reg.v1Max, reg.v1Min))
        thd = abs((100 / (reg.v1Raw * (header.vNom / calibr.cV))) * (
                (18 / calibr.cThd) * (reg.thdRaw - ((calibr.cRes / calibr.cV) * reg.v1Raw))))
        fkr = ((reg.fkrRaw * header.vNom * .02) / calibr.cFkr) * (100 / reg.v1 * tv)
        reg.thd = self.limitar(self, thd, self.thdCap)
        reg.fkr = self.limitar(self, fkr, self.fkrCap)
        return reg


class Serie15(Serie):
    largoRegistro = 12
    largoHeaderCalibracion = 54
    unpackHeaderCalibracion = '>17s HHHHH 27x'  # fileName, cThd, cRes, cFkr, cV
    unpackReg = '2xHHHHH'
    regMap = ['fkrRaw', 'thdRaw', 'v1MinRaw', 'v1MaxRaw', 'v1Raw']
    regDatMap = ['v1', 'v1Max', 'v1Min', 'thd', 'fkr']
    calibrMap = ['fileName', 'cThd', 'cRes', 'cFkr', 'cV']
    headerMap = ['serie', 'equipo', 'periodo', 'dStrt', 'mStrt', 'yStrt', 'hStrt', 'minStrt', 'vNomRaw', 'iNomRaw',
                 'dEnd', 'mEnd', 'yEnd', 'hEnd', 'minEnd']
    reverse = True
    regex = b'(?P<bogus>(?<=\xff)[^\xff]{90}(?=\xff))|(?P<calibr>[^\xff]{54}(?=\xff))?\xff(?P<header>(?<=\xff)[^\xff]{36}(?=\xff))|(?P<err>(?<=\xff)[^\xff]{7}(?=\xff))|(?P<reg>[^\xff]{12})'
    headerFormatString = 'Equipo Nro:\t{}\t\tCódigo de Cliente: \tID. Subestación:\t{}\nNumero de Serie:\t{}\tPeriodo:\t{} {}.\nTensión:     \t{} V\t\tFactor de Corrección: {}\nCorriente:\t{} Amp\t\tFactor de Corrección: {}\nDia inicio:\t{}\tDia fin:\t{}\nHora inicio:\t{}\tHora fin:\t{}\n\nFecha	Hora\tV\tV Max\tV Min\tTHD1\tFlicker\tAnormalidad\n\t\tV\tV\tV\t%\t%\t\n'
    regFormatString = '%s\t%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%s\n'

    def analizarRegistroDat(self, reg, calibr, tv, ti, header):
        reg.v1 = ((300 * reg.v1Raw) / 65278) * tv
        reg.v1Max = ((300 * reg.v1MaxRaw) / 65278) * tv
        reg.v1Min = ((300 * reg.v1MinRaw) / 65278) * tv
        if reg.v1 > reg.v1Max: reg.v1Max = reg.v1
        if reg.v1Min > reg.v1: reg.v1 = reg.v1Min
        reg.v1, reg.v1Max, reg.v1Min = (self.limitar(self, v, self.vCap * tv) for v in (reg.v1, reg.v1Max, reg.v1Min))
        thd = reg.thdRaw * 50 / 65278
        fkr = reg.fkrRaw * 20 / 65278
        reg.thd = self.limitar(self, thd, self.thdCap)
        reg.fkr = self.limitar(self, fkr, self.fkrCap)
        return reg


class Serie13(Serie):
    largoRegistro = 42
    largoHeaderCalibracion = 35
    iCoef = 4095
    eCoef = 370 / 2400
    #                                    thd1 res1 thd3 res3 thd2  res2 fkr
    unpackHeaderCalibracion = '=16s xxxxx H    H     H   H    H     H   H'
    unpackReg = '>x H H 3b H HHH H 3b H HHH H 3b H HHH'
    regMap = ['fkrRaw', 'thdRaw3', 'e3b1', 'e3b2', 'e3b3', 'i3Raw', 'v3MinRaw', 'v3MaxRaw',
              'v3Raw', 'thdRaw2', 'e2b1', 'e2b2', 'e2b3', 'i2Raw', 'v2MinRaw', 'v2MaxRaw', 'v2Raw', 'thdRaw1', 'e1b1',
              'e1b2', 'e1b3', 'i1Raw', 'v1MinRaw', 'v1MaxRaw', 'v1Raw']
    regDatMap = ['v1', 'v1Max', 'v1Min', 'i1', 'phi1', 'e1', 'v2', 'v2Max', 'v2Min', 'i2', 'phi2', 'e2', 'v3', 'v3Max',
                 'v3Min', 'i3', 'phi3', 'e3', 'thd', 'fkr', 'pTotal', 'eTotal']
    headerMap = ['serie', 'equipo', 'periodo', 'dStrt', 'mStrt', 'yStrt', 'hStrt', 'minStrt', 'vNomRaw', 'iNomRaw',
                 'dEnd', 'mEnd', 'yEnd', 'hEnd', 'minEnd']
    calibrMap = ['fileName', 'cThd1', 'cRes1', 'cThd3', 'cRes3', 'cThd2', 'cRes2', 'cFkr']
    reverse = True

    regex = b'(?P<bogus>(?<=\xff)[^\xff]{57}(?=\xff))|(?P<calibr>[^\xff]{35}(?=\xff))?\xff(?P<header>(?<=\xff)[^\xff]{36}(?=\xff))|(?P<err>(?<=\xff)[^\xff]{7}(?=\xff))|(?P<reg>[^\xff]{42})'

    regFormatString = '%s\t%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.3f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.3f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.3f\t%0.2f\t%0.3f\t%0.3f\t%0.3f\t%s\n'
    headerFormatString = 'Equipo Nro:\t{}\t\tCódigo de Cliente: \tID. Subestación:\t{}\nNumero de Serie:\t{}\tPeriodo:\t{} {}.\nTensión:     \t{} V\t\tFactor de Corrección: {}\nCorriente:\t{} Amp\t\tFactor de Corrección: {}\nDia inicio:\t{}\tDia fin:\t{}\nHora inicio:\t{}\tHora fin:\t{}\n\nFecha\tHora\tU1\tU1 Max\tU1 Min\tIA1\tCosFi 1\tEA1\tU2\tU2 Max\tU2 Min\tIA2\tCosFi 2\tEA2\tU3\tU3 Max\tU3 Min\tIA3\tCosFi 3\tEA3\tTHD1\tFlicker1\tP Total\tEA Total\tAnormalidad\n\t\tV\tV\tV\tA\tp.u.\tKWh\tV\tV\tV\tA\tp.u.\tKWh\tV\tV\tV\tA\tp.u.\tKWh\t%\t%\tKW\tKWh\t\n'

    def analizarRegistroDat(self, reg, calibr, tv, ti, header):
        from math import floor
        calibr.cV = 26214 / 2
        reg.v1 = reg.v1Raw * (header.vNom / calibr.cV) * tv
        reg.v1Max = reg.v1MaxRaw * (header.vNom / calibr.cV) * tv
        reg.v1Min = reg.v1MinRaw * (header.vNom / calibr.cV) * tv
        if reg.v1 > reg.v1Max: reg.v1Max = reg.v1
        if reg.v1Min > reg.v1: reg.v1 = reg.v1Min
        reg.v1, reg.v1Max, reg.v1Min = (self.limitar(self, v, self.vCap * tv) for v in (reg.v1, reg.v1Max, reg.v1Min))

        reg.v2 = reg.v2Raw * (header.vNom / calibr.cV) * tv
        reg.v2Max = reg.v2MaxRaw * (header.vNom / calibr.cV) * tv
        reg.v2Min = reg.v2MinRaw * (header.vNom / calibr.cV) * tv
        if reg.v2 > reg.v2Max: reg.v2Max = reg.v2
        if reg.v2Min > reg.v2: reg.v2 = reg.v2Min
        reg.v2, reg.v2Max, reg.v2Min = (self.limitar(self, v, self.vCap * tv) for v in (reg.v2, reg.v2Max, reg.v2Min))

        reg.v3 = reg.v3Raw * (header.vNom / calibr.cV) * tv
        reg.v3Max = reg.v3MaxRaw * (header.vNom / calibr.cV) * tv
        reg.v3Min = reg.v3MinRaw * (header.vNom / calibr.cV) * tv
        if reg.v3 > reg.v3Max: reg.v3Max = reg.v3
        if reg.v3Min > reg.v3: reg.v3 = reg.v3Min
        reg.v3, reg.v3Max, reg.v3Min = (self.limitar(self, v, self.vCap * tv) for v in (reg.v3, reg.v3Max, reg.v3Min))

        reg.i1 = reg.i1Raw * (header.iNom / self.iCoef)
        reg.i2 = reg.i2Raw * (header.iNom / self.iCoef)
        reg.i3 = reg.i3Raw * (header.iNom / self.iCoef)

        reg.e1 = ((((reg.e1b1 << 7) + reg.e1b2) << 7) + reg.e1b3) * self.eCoef / 1000 * tv * ti
        reg.e2 = ((((reg.e2b1 << 7) + reg.e2b2) << 7) + reg.e2b3) * self.eCoef / 1000 * tv * ti
        reg.e3 = ((((reg.e3b1 << 7) + reg.e3b2) << 7) + reg.e3b3) * self.eCoef / 1000 * tv * ti

        calibr.cV = 220  # Ver si esto es el header.vNom
        try:
            thd1 = abs((100 / reg.v1) * (
                    (18 / (calibr.cThd1 - calibr.cRes1)) * (reg.thdRaw1 - (floor(calibr.cRes1 / calibr.cV) * reg.v1))))
        except ZeroDivisionError:
            thd1 = 0.0
        reg.thd = self.limitar(self, thd1, self.thdCap)
        # thd2 = abs((100 / reg.v2) * (
        #         (18 / (calibr.cThd2-calibr.cRes2)) * (reg.thdRaw2 - (floor(calibr.cRes2 / calibr.cV) * reg.v2))))
        # thd3 = abs((100 / reg.v3) * (
        #         (18 / (calibr.cThd3-calibr.cRes3)) * (reg.thdRaw3 - (floor(calibr.cRes3 / calibr.cV) * reg.v3))))

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

        try:
            fkr = ((reg.fkrRaw * header.vNom * .02) / calibr.cFkr) * (100 / reg.v1 * tv)
        except ZeroDivisionError:
            fkr = 0.0
        reg.fkr = self.limitar(self, fkr, self.fkrCap)

        reg.pTotal = (reg.v1 * reg.i1 * reg.phi1 + reg.v2 * reg.i2 * reg.phi2 + reg.v3 * reg.i3 * reg.phi3) / 1000
        reg.eTotal = sum((reg.e1, reg.e2, reg.e3))

        return reg


class Serie0C(Serie):
    largoRegistro = 46
    largoHeaderCalibracion = 28
    unpackHeaderCalibracion = 'xxxxxxxxxxxx H xx H H H H H xx'  # cThd, cFkr, cV1, cV2, cV3, cRes
    unpackReg = '>H H 3b 3b H HHH 3b 3b H HHH 3b 3b H HHH'
    regMap = ['fkrRaw', 'thdRaw', 'i3b1', 'i3b2', 'i3b3', 'e3b1', 'e3b2', 'e3b3', 'i3Raw', 'v3MinRaw', 'v3MaxRaw',
              'v3Raw', 'i2b1', 'i2b2', 'i2b3', 'e2b1', 'e2b2', 'e2b3', 'i2Raw', 'v2MinRaw', 'v2MaxRaw', 'v2Raw',
              'i1b1', 'i1b2', 'i1b3', 'e1b1', 'e1b2', 'e1b3', 'i1Raw', 'v1MinRaw', 'v1MaxRaw', 'v1Raw']
    regDatMap = ['v1', 'v1Max', 'v1Min', 'i1', 'phi1', 'e1', 'v2', 'v2Max', 'v2Min', 'i2', 'phi2', 'e2', 'v3',
                 'v3Max', 'v3Min', 'i3', 'phi3', 'e3', 'thd', 'fkr', 'pTotal', 'eTotal']
    calibrMap = ['cThd', 'cFkr', 'cV1', 'cV2', 'cV3', 'cRes']
    reverse = True

    regex = b'(?P<calibr>[^\xff]{28}(?=\xff))?\xff(?P<header>(?<=\xff)[^\xff]{36}(?=\xff))|(?P<err>(?<=\xff)[^\xff]{7}(?=\xff))|(?P<reg>[^\xff]{46})'

    regFormatString = '%s\t%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%0.2f\t%0.3f\t%0.3f\t%0.3f\t%s\n'
    headerFormatString = 'Equipo Nro:\t{}\t\tCódigo de Cliente: \tID. Subestación:\t{}\nNumero de Serie:\t{}\tPeriodo:\t{} {}.\nTensión:     \t{} V\t\tFactor de Corrección: {}\nCorriente:\t{} Amp\t\tFactor de Corrección: {}\nDia inicio:\t{}\tDia fin:\t{}\nHora inicio:\t{}\tHora fin:\t{}\n\nFecha\tHora\tU1\tU1 Max\tU1 Min\tIA1\tCosFi 1\tEA1\tU2\tU2 Max\tU2 Min\tIA2\tCosFi 2\tEA2\tU3\tU3 Max\tU3 Min\tIA3\tCosFi 3\tEA3\tTHD1\tFlicker1\tP Total\tEA Total\tAnormalidad\n\t\tV\tV\tV\tA\tp.u.\tKWh\tV\tV\tV\tA\tp.u.\tKWh\tV\tV\tV\tA\tp.u.\tKWh\t%\t%\tKW\tKWh\t\n'

    def analizarRegistroDat(self, reg, calibr, tv, ti, header):
        reg.v1, reg.v1Max, reg.v1Min = (x * (header.vNom / calibr.cV1) * tv for x in
                                        (reg.v1Raw, reg.v1MaxRaw, reg.v1MinRaw))
        if reg.v1 > reg.v1Max: reg.v1Max = reg.v1
        if reg.v1Min > reg.v1: reg.v1 = reg.v1Min
        reg.v1, reg.v1Max, reg.v1Min = (self.limitar(self, v, self.vCap * tv) for v in
                                        (reg.v1, reg.v1Max, reg.v1Min))

        reg.v2, reg.v2Max, reg.v2Min = (x * (header.vNom / calibr.cV2) * tv for x in
                                        (reg.v2Raw, reg.v2MaxRaw, reg.v2MinRaw))
        if reg.v2 > reg.v2Max: reg.v2Max = reg.v2
        if reg.v2Min > reg.v2: reg.v2 = reg.v2Min
        reg.v2, reg.v2Max, reg.v2Min = (self.limitar(self, v, self.vCap * tv) for v in
                                        (reg.v2, reg.v2Max, reg.v2Min))

        reg.v3, reg.v3Max, reg.v3Min = (x * (header.vNom / calibr.cV3) * tv for x in
                                        (reg.v3Raw, reg.v3MaxRaw, reg.v3MinRaw))
        if reg.v3 > reg.v3Max: reg.v3Max = reg.v3
        if reg.v3Min > reg.v3: reg.v3 = reg.v3Min
        reg.v3, reg.v3Max, reg.v3Min = (self.limitar(self, v, self.vCap * tv) for v in
                                        (reg.v3, reg.v3Max, reg.v3Min))

        e1p = ((((reg.e1b1 << 7) + reg.e1b2) << 7) + reg.e1b3) * self.eCoef / 1000 * tv * ti
        e2p = ((((reg.e2b1 << 7) + reg.e2b2) << 7) + reg.e2b3) * self.eCoef / 1000 * tv * ti
        e3p = ((((reg.e3b1 << 7) + reg.e3b2) << 7) + reg.e3b3) * self.eCoef / 1000 * tv * ti

        reg.e1 = e1p * header.iNom / 35
        reg.e2 = e2p * header.iNom / 35
        reg.e3 = e3p * header.iNom / 35

        # reg.i1 = reg.i1Raw * (header.iNom/self.iCoef)
        c1 = (((((reg.i1b1 << 7) + reg.i1b2) << 7) + reg.i1b3) * 60 / 15) / 1000 * self.eCoef
        d1 = (((((reg.e1b1 << 7) + reg.e1b2) << 7) + reg.e1b3) * 60 / 15) / 1000 * self.eCoef
        try:
            reg.i1p = ((d1 * d1) + (c1 * c1)) ** 0.5 * 1000 / reg.v1
        except ZeroDivisionError:
            reg.i1p = 0
        # if reg.i1 == 0:
        #     reg.i1 = reg.i1p

        # reg.i2 = reg.i2Raw * (header.iNom/self.iCoef)
        c2 = (((((reg.i2b1 << 7) + reg.i2b2) << 7) + reg.i2b3) * 60 / 15) / 1000 * self.eCoef
        d2 = (((((reg.e2b1 << 7) + reg.e2b2) << 7) + reg.e2b3) * 60 / 15) / 1000 * self.eCoef
        try:
            reg.i2p = ((d2 * d2) + (c2 * c2)) ** 0.5 * 1000 / reg.v2
        except ZeroDivisionError:
            reg.i2p = 0
        # if reg.i2 == 0:
        #     reg.i2 = reg.i2p

        # reg.i3 = reg.i3Raw * (header.iNom/self.iCoef)
        c3 = (((((reg.i3b1 << 7) + reg.i3b2) << 7) + reg.i3b3) * 60 / 15) / 1000 * self.eCoef
        d3 = (((((reg.e3b1 << 7) + reg.e3b2) << 7) + reg.e3b3) * 60 / 15) / 1000 * self.eCoef
        try:
            reg.i3p = ((d3 * d3) + (c3 * c3)) ** 0.5 * 1000 / reg.v3
        except ZeroDivisionError:
            reg.i3p = 0
        # if reg.i3 == 0:
        #     reg.i3 = reg.i3p

        try:
            reg.phi1 = e1p / (reg.i1p * reg.v1 / 1000 * header.periodo / 60) / tv / ti
        except ZeroDivisionError:
            reg.phi1 = 0.0
        try:
            reg.phi2 = e2p / (reg.i2p * reg.v2 / 1000 * header.periodo / 60) / tv / ti
        except ZeroDivisionError:
            reg.phi2 = 0.0
        try:
            reg.phi3 = e3p / (reg.i3p * reg.v3 / 1000 * header.periodo / 60) / tv / ti
        except ZeroDivisionError:
            reg.phi3 = 0.0

        reg.i1 = reg.e1 / reg.phi1 / reg.v1 * 1000 / 15 * 60
        reg.i2 = reg.e2 / reg.phi2 / reg.v2 * 1000 / 15 * 60
        reg.i3 = reg.e3 / reg.phi3 / reg.v3 * 1000 / 15 * 60

        thd = abs((100 / (reg.v1Raw * (header.vNom / calibr.cV1))) * (
                (18 / calibr.cThd) * (reg.thdRaw - ((calibr.cRes / calibr.cV1) * reg.v1Raw))))
        fkr = ((reg.fkrRaw * header.vNom * .02) / calibr.cFkr) * (100 / reg.v1 * tv)
        reg.thd = self.limitar(self, thd, self.thdCap)
        reg.fkr = self.limitar(self, fkr, self.fkrCap)

        reg.pTotal = (reg.v1 * reg.i1 * reg.phi1 + reg.v2 * reg.i2 * reg.phi2 + reg.v3 * reg.i3 * reg.phi3) / 1000
        reg.eTotal = sum((reg.e1, reg.e2, reg.e3))

        return reg
