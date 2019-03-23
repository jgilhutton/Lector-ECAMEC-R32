from Medicion import Medicion

# file = 'Serie vieja T/ori.R32'
# file = 'Serie vieja M/Originales/010388O1.R32'
# file = 'Serie 1104 M/010288O1.R32'
# file = 'Serie 1605 M/100388O1.R32'
file = 'Serie 1104 T/030688O1.R32'

medicion = Medicion(file,1,1)
medicion.analizarR32()
