dataSeries = {
            'Vieja':{
                        1:{
                            'headerDat':'Equipo Nro:\t{filename}\t\tCódigo de Cliente: \tID. Subestación:\t        \nNumero de Serie:\tND\tPeriodo:\
                             {periodo} {Utiempo}.\nTensión:     \t{tension} V\t\tFactor de Corrección: {TV}\nCorriente:\t{corriente} Amp\t\t\
                             Factor de Corrección: {TI}\nDia inicio:\t{inicio}\tDia fin:\t{final}\nHora inicio:\t{horaInicio}\tHora fin:\t{horaFinal}\
                             \n\nFecha	Hora\tU\tU Max\tU Min\tTHD1\tFlicker\tAnormalidad\n\t\tV\tV\tV\t%\t%\t\n',
                            'largoRegistro':10,
                            'largoErr':7,
                            'byteSeparador':255,
                            'variables':['V','Vmax','Vmin','thd','flicker'],
                            'maxValues':{'V':286,'Vmax':286,'Vmin':286,'thd':10,'flicker':2},
                            'formatoReg':'%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%s\n',
                            'formatoErr':'%s\t%s\n',
                            'getTension':lambda x: x*0.07087628543376923,
                            'getFlicker':lambda x,y,z: ((x*220*.02)/y)*(100/z),
                            'getThd':lambda u,v,w,x,y,z: (100/u)*(abs(v-((w/x)*y)))*18/z,
                            'unpackString':'>HHHHH',
                            'unpackErr':'>BBBBBBB',
                            'unpackHeaderCalibracion':{'string':'HHHHH','indices':[0,1,2,3,4]},
                            'unpackHeader':'>8sx2s2s2s2s2s2s3x2s2s2s2s2sxx',
                            'unpackHeaderSecundario':'>8sx2s2s2s2s2s2s3x2s2s2s2s2sxx',
                            'headerMap':dict([reversed(x) for x in enumerate(['filename','periodo','diaInicio','mesInicio','añoInicio','horaInicio','minInicio','diaFin','mesFin','añoFin','horaFin','minFin'])]),
                            'regIndexes':{'flicker':0,'thd':1,'Vmin':2,'Vmax':3,'V':4},},
                        3:{
                            'largoRegistro':42,
                            'largoErr':7,
                            'byteSeparador':255,
                            'factorTension':lambda x: x*0.008392460165229354,
                            'factorCorriente':lambda x: x*0.005086235518683759,
                            'factorPotencia':lambda x,y: y*x,
                            # 'packString':'>HHHHHHHH HxHHHHH HxHHHHH',
                            'packString':'>HB HBH H HHH HBH H HHH HBH H HHH',
                            
                            # I1 v1min v1max v1 },
                            },
                    },
            '1104':{
                        1:{
                            'headerDat':'Equipo Nro:\t{filename}\t\tCódigo de Cliente: \tID. Subestación:\t        \nNumero de Serie:\tND\tPeriodo:\
                             {periodo} {Utiempo}.\nTensión:     \t{tension} V\t\tFactor de Corrección: {TV}\nCorriente:\t{corriente} Amp\t\t\
                             Factor de Corrección: {TI}\nDia inicio:\t{inicio}\tDia fin:\t{final}\nHora inicio:\t{horaInicio}\tHora fin:\t{horaFinal}\
                             \n\nFecha	Hora\tU\tU Max\tU Min\tTHD1\tFlicker\tAnormalidad\n\t\tV\tV\tV\t%\t%\t\n',
                            'largoRegistro':19,
                            'largoErr':7,
                            'byteSeparador':255,
                            'variables':['V','Vmax','Vmin','thd','flicker'],
                            'maxValues':{'V':286,'Vmax':286,'Vmin':286,'thd':10,'flicker':2},
                            'formatoReg':'%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%s\n',
                            'formatoErr':'%s\t%s\n',
                            'getTension':lambda x: x*0.1342281848192215,
                            'getFlicker':lambda x,y,z: ((x*220*.02)/y)*(100/z),
                            'getThd':lambda u,v,w,x,y,z: (100/u)*(abs(v-((w/x)*y)))*18/z,
                            'unpackString':'>HH 9x HHH',
                            'unpackErr':'>BBBBBBB',
                            'unpackHeaderCalibracion':{'string':'HxxxxxxxxxxHxxHHxxxxHxx','indices':[3,0,1,4,2]},
                            'unpackHeader':'>8sx2s2s2s2s2s2s3x2s2s2s2s2sxx',
                            'unpackHeaderSecundario':'>8sx2s2s2s2s2s2s3x2s2s2s2s2sxx',
                            'headerMap':dict([reversed(x) for x in enumerate(['filename','periodo','diaInicio','mesInicio','añoInicio','horaInicio','minInicio','diaFin','mesFin','añoFin','horaFin','minFin'])]),
                            'regIndexes':{'flicker':0,'thd':1,'Vmin':2,'Vmax':3,'V':4},},
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
                            'headerDat':'Equipo Nro:\t{filename}\t\tCódigo de Cliente: \tID. Subestación:\t        \nNumero de Serie:\tND\tPeriodo:\
                             {periodo} {Utiempo}.\nTensión:     \t{tension} V\t\tFactor de Corrección: {TV}\nCorriente:\t{corriente} Amp\t\t\
                             Factor de Corrección: {TI}\nDia inicio:\t{inicio}\tDia fin:\t{final}\nHora inicio:\t{horaInicio}\tHora fin:\t{horaFinal}\
                             \n\nFecha	Hora\tU\tU Max\tU Min\tTHD U\tFlicker\tAnormalidad\n\t\tV\tV\tV\t%\t%\t\n',
                            'largoRegistro':12,
                            'largoErr':7,
                            'byteSeparador':255,
                            'variables':['V','Vmax','Vmin','thd','flicker'],
                            'maxValues':{'V':286,'Vmax':286,'Vmin':286,'thd':10,'flicker':2},
                            'formatoReg':'%s\t%0.2f\t%0.2f\t%0.2f\t%0.2f\t%0.3f\t%s\n',
                            'formatoErr':'%s\t%s\n',
                            'getTension':lambda x: x*0.00459564208984375,
                            'getFlicker':lambda x:x*4.664380212779652e-09,
                            'getThd':lambda x: x*0.0007659912109375,
                            'unpackString':'IHHHH',
                            'unpackErr':'>BBBBBBB',
                            'unpackHeader':'9x 2s 2s2s2s 2s2s 3x 2s2s2s 2s2s 2x 8s 46x',
                            'unpackHeaderSecundario':'9x 2s 2s2s2s 2s2s 3x 2s2s2s 2s2s 3x 8s 46x',
                            'unpackHeaderCalibracion':{'string':'','indices':None},
                            'headerMap':dict([reversed(x) for x in enumerate(['periodo','diaInicio','mesInicio','añoInicio','horaInicio','minInicio',
                            'diaFin','mesFin','añoFin','horaFin','minFin','filename'])]),
                            'regIndexes':{'flicker':0,'thd':1,'Vmin':2,'Vmax':3,'V':4},},
                        3:{
                            'largoRegistro':54,
                            'largoErr':7,
                            'byteSeparador':255,
                            'factorTension':0.00839227754373019,
                            'factorCorriente':0.005088869461694482,
                            'factorFlicker':0.0,
                            'factorThd':0.0,
                            'packString':'>HHHHHHHHHHxHHHHHHHHxBBBBBBBBHHHH'},},
            '1612':{},}