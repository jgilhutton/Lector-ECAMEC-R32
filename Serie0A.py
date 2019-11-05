from Tools import limitar


class Serie0A:
    largoRegistro = 15
    largoHeaderData = 36
    largoHeaderCalibracion = 28
    largoRegistroErr = 7
    qBytesMolestos = 0
    deltaMax = 1.3
    fkrCap = 2.0
    thdCap = 10.0
    phiCap = 1.0
    reverse = True
    # FORMAT STRINGS
    regex = '(?P<calibr>[^\xff]{%s}(?=\xff))?\xff(?P<header>(?<=\xff)[^\xff]{%s}(?=\xff))|(?P<err>(?<=\xff)[^\xff]{%s}(?=\xff))|(?P<reg>[^\xff]{%s})'
    headerFormatString = 'Equipo Nro:\t{}\t\tCódigo de Cliente: \tID. Subestación:\t{}\nNumero de Serie:\t{}\tPeriodo:\t{} {}.\nTensión:     \t{} V\t\tFactor de Corrección: {}\nCorriente:\t{} Amp\t\tFactor de Corrección: {}\nDia inicio:\t{}\tDia fin:\t{}\nHora inicio:\t{}\tHora fin:\t{}\n\nFecha	Hora\tV\tV Max\tV Min\tTHD1\tFlicker\tAnormalidad\n\t\tV\tV\tV\t%\t%\t\n'
    regFormatString = '%s\t%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%s\n'
    errFormatString = '{}\t{}\t{}\n'
    # MAPAS
    regMap = ['fkrRaw', 'thdRaw', 'v1MinRaw', 'v1MaxRaw', 'v1Raw']
    regDatMap = ['v1', 'v1Max', 'v1Min', 'thd', 'fkr']
    calibrMap = ['cThd', 'cRes', 'cFkr', 'cV']
    headerMap = ['fileName', 'equipo', 'periodo', 'dStrt', 'mStrt', 'yStrt', 'hStrt', 'minStrt', 'vNomRaw', 'iNomRaw',
                 'dEnd', 'mEnd', 'yEnd', 'hEnd', 'minEnd']
    errMap = ['codigo', 'S', 'M', 'H', 'd', 'm', 'y']
    # UNPACK STRINGS
    unpackReg = '>HH 5x HHH'
    unpackHeaderCalibracion = '12xHHHH8x'
    unpackHeaderData = '>8s B 2s 2s2s2s2s2s x B B 2s2s2s2s2s 2x'
    unpackErr = '>BBBBBBB'

    def setRegex(self):
        formatTuple = (self.largoHeaderCalibracion, self.largoHeaderData, self.largoRegistroErr, self.largoRegistro)
        self.regex = self.regex % formatTuple

    def setVariante(self, rawData):
        self.setRegex()

    def analizarRegistroDat(self, reg, calibr, tv, ti, header):
        reg.v1 = reg.v1Raw * (header.vNom / calibr.cV) * tv
        reg.v1Max = reg.v1MaxRaw * (header.vNom / calibr.cV) * tv
        reg.v1Min = reg.v1MinRaw * (header.vNom / calibr.cV) * tv
        if reg.v1 > reg.v1Max: reg.v1Max = reg.v1
        if reg.v1Min > reg.v1: reg.v1 = reg.v1Min
        reg.v1, reg.v1Max, reg.v1Min = (limitar(v, 0, header.vNom * self.deltaMax * tv) for v in
                                        (reg.v1, reg.v1Max, reg.v1Min))
        try:
            thd = abs((100 / (reg.v1Raw * (header.vNom / calibr.cV))) * (
                (18 / calibr.cThd) * (reg.thdRaw - ((calibr.cRes / calibr.cV) * reg.v1Raw))))
        except ZeroDivisionError:
            thd = 0
        try:
            fkr = ((reg.fkrRaw * header.vNom * .02) / calibr.cFkr) * (100 / reg.v1 * tv)
        except ZeroDivisionError:
            fkr = 0
        reg.thd = limitar(thd, 0, self.thdCap)
        reg.fkr = limitar(fkr, 0, self.fkrCap)
        return reg
