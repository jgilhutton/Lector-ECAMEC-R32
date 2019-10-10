from time import mktime, localtime
from re import finditer
from os.path import isfile


def genTimeStamp(startTime, periodo):
    stampSeconds = mktime(startTime) - mktime(startTime) % (periodo * 60)
    while True:
        stampSeconds += (periodo * 60)
        yield localtime(stampSeconds)


def feeder(regex, data, reverse=False):
    if reverse: data = data[::-1]
    for match in finditer(regex, data):
        yield match.groupdict()


def inRange(value,boundaries):
    return boundaries[0] < value < boundaries[1]


def checkFileName(fileName, ext):
    return fileName + ext  # Temp
    if not isfile(''.join((self.path, '/', fileName, ext))): return fileName + ext
    ext = ext[:-1] + '%d'
    c = 0
    while True:
        if isfile(''.join((self.path, '/', fileName, ext % c))):
            c += 1
            continue
        break
    return fileName + ext % c
