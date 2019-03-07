def feeder(data,largoRegistro,largoErr,largoHeader,largoHeaderCalibracion,byteSeparador):
    returnData = data[:]
    limite = (largoHeader+largoHeaderCalibracion)-1
    puntero = len(data)-1 # jajaj Perdón C, por ponerle este nombre a la variable.
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
        if puntero == limite:
            yield ('header',returnData[1:largoHeader+1])
            break

def inRange(valor,*arg):
    if not valor or not all([all(x) for x in arg]): return False
    return all([rango[0] <= valor <= rango[1] for rango in arg])

def debugPrint(*args,**kwargs):
    print(' DEBUG '.center(100,'#'))
    if args:
        print(','.join(map(str,args)))
    if kwargs:
        print(','.join([str(x) for x in zip(kwargs.keys(),kwargs.values())]))
    print(' DEBUG '.center(100,'#'))