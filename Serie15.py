from Tools import limitar
from re import search
from struct import unpack


class Serie15:
    largoHeaderData = 36
    largoHeaderCalibracion = 54
    largoRegistroErr = 7
    bogusBytes = 90
    qBytesMolestos = 0
    deltaMax = 1.3
    fkrCap = 2.0
    thdCap = 10.0
    phiCap = 1.0
    reverse = True
    # FORMAT STRINGS
    regex = '(?P<bogus>^\xff.{%s}(?=\xff))|(?P<calibr>[^\xff]{%s}(?=\xff)|[^\xff]{26}\xff[^\xff]{27})?\xff(?P<header>(?<=\xff)[^\xff]{%s}(?=\xff))|(?P<err>(?<=\xff)[^\xff]{%s}(?=\xff))|(?P<reg>[^\xff]{%s})'
    headerFormatString = 'Equipo Nro:\t{}\t\tCódigo de Cliente: \tID. Subestación:\t{}\nNumero de Serie:\t{}\tPeriodo:\t{} {}.\nTensión:     \t{} V\t\tFactor de Corrección: {}\nCorriente:\t{} Amp\t\tFactor de Corrección: {}\nDia inicio:\t{}\tDia fin:\t{}\nHora inicio:\t{}\tHora fin:\t{}\n\nFecha	Hora\tV\tV Max\tV Min\tTHD1\tFlicker\tAnormalidad\n\t\tV\tV\tV\t%\t%\t\n'
    regFormatString = '%s\t%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%s\n'
    errFormatString = '{}\t{}\t{}\n'
    # MAPAS
    regDatMap = ['v1', 'v1Max', 'v1Min', 'thd', 'fkr']
    calibrMap = ['fileName']
    headerMap = ['serie', 'equipo', 'periodo', 'dStrt', 'mStrt', 'yStrt', 'hStrt', 'minStrt', 'vNomRaw', 'iNomRaw',
                 'dEnd', 'mEnd', 'yEnd', 'hEnd', 'minEnd']
    errMap = ['codigo', 'S', 'M', 'H', 'd', 'm', 'y']
    # UNPACK STRINGS
    unpackHeaderCalibracion = '>17s 37x'  # fileName
    unpackHeaderData = '>8s B 2s 2s2s2s2s2s x B B 2s2s2s2s2s 2x'
    unpackErr = '>BBBBBBB'

    def setRegex(self):
        formatTuple = (self.bogusBytes, self.largoHeaderCalibracion, self.largoHeaderData, self.largoRegistroErr,
                       self.largoRegistro)
        self.regex = self.regex % formatTuple

    def setVariante(self, rawData):
        regSizes = {8240: 6, 9008: 12}
        initRe = '(?P<header>(?<=\xff)[^\xff]{%s}(?=\xff))\xff(?P<calibr>[^\xff]{%s}(?=\xff)|[^\xff]{27}\xff[^\xff]{26}(?=\xff))' % (
        self.largoHeaderData, self.largoHeaderCalibracion)
        testRe = search(bytes(initRe, encoding='latin1'), rawData)
        if testRe:
            calibr = testRe.group('calibr')
            regSize = unpack('>H', calibr[-4:-2])[0]
            self.largoRegistro = regSizes[regSize]

        if self.largoRegistro == 6:
            self.unpackReg = 'HHH'
            self.regMap = ['v1Raw', 'thdRaw', 'fkrRaw', ]
        elif self.largoRegistro == 12:
            self.unpackReg = '2xHHHHH'
            self.regMap = ['fkrRaw', 'thdRaw', 'v1MinRaw', 'v1MaxRaw', 'v1Raw']
        self.setRegex()

    def analizarRegistroDat(self, reg, calibr, tv, ti, header):
        reg.v1 = ((300 * reg.v1Raw) / 65278) * tv
        if self.largoRegistro == 12:
            reg.v1Max = ((300 * reg.v1MaxRaw) / 65278) * tv
            reg.v1Min = ((300 * reg.v1MinRaw) / 65278) * tv
            if reg.v1 > reg.v1Max: reg.v1Max = reg.v1
            if reg.v1Min > reg.v1: reg.v1 = reg.v1Min
            reg.v1, reg.v1Max, reg.v1Min = (limitar(v, 0, header.vNom * self.deltaMax * tv) for v in
                                            (reg.v1, reg.v1Max, reg.v1Min))
        elif self.largoRegistro == 6:
            reg.v1Max, reg.v1Min = reg.v1, reg.v1

        thd = reg.thdRaw * 50 / 65278
        fkr = reg.fkrRaw * 20 / 65278
        reg.thd = limitar(thd, 0, self.thdCap)
        reg.fkr = limitar(fkr, 0, self.fkrCap)
        return reg
