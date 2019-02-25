from Medicion import Medicion

# file = 'Serie vieja T/ori.R32'
# fileDat = 'Serie vieja T/ori.dat'
# file = 'Serie vieja M/Originales/010388O1.R32'
# fileDat = 'Serie vieja M/Originales/010388O1.dat'
file = 'Serie 1104 M/010288O1.R32'
fileDat = 'Serie 1104 M/010288O1.dat'
# file = 'Serie 1605 M/100388O1.R32'
# fileDat = 'Serie 1605 M/100388O1.dat'

medicion = Medicion(file,1,1)
medicion.analizarR32()
