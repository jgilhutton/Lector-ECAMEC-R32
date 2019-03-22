from re import finditer

def feeder(data,regex):
    data = data[::-1]
    for match in finditer(regex,data):
        yield match.groupdict()

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