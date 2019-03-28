# Lector de archivos .R32 de ![alt text](http://www.ecamec.com.ar/images/loguito.jpg)
Este es un trabajo de ingeniería inversa a los archivos R32 que generan los registradores de variables eléctricas de la empresa ECAMEC.

En el laburo, tenemos que analizar toneladas de archivos R32, de equipos de 4 series distintas, que generan mal los archivos, con factores de tension y corrientes diferentes.

ECAMEC no nos dio ninguna solución para esto, por lo que nos vemos obligados a procesar uno por uno. Insoportable.

Esta herramienta está destinada a terminar con nuestro sufrimiento y el de los demás.

Iré modificando y ampliando el programa a medida que vaya descubriendo cosas.

# Este programa, al día de la fecha, puede leer las series:

- Vieja Monofásica
- Vieja Trifásica
- 1104 Monofásica
- 1104 Trifásica
- 1605 Monofásica
- 1605 Trifásica

# Modo de uso:

``    
     Modo de uso:    python r32.py [-d Directorio]|[-f Archivo] [Opcionales]
    -d  Directorio con archivos .R32
    -f  Archivo .R32
    Opcionales:
        -o  Directorio donde se guardan los archivos generados
            Valor por defecto: Directorio de los archivos R32
        -tv Factor de tensión   Valor por defecto: 1
        -ti Factor de corriente Valor por defecto: 1
        -v  Muestra más información en la pantalla durante el
            procesamiento. Valor por defect: Falso
        -vv Igual que -v pero con información de depuración

    Los archivos pueden tener cualquier extensión.
    Lo que importa es la información que está dentro de ellos.
    Un archivo válido puede ser MEDICION.TXT, si se desea

    Ejemplos:
    python r32.py -d "C:\Mediciones" -o "C:\Mediciones Procesadas"
    python r32.py -f MEDICION.R32 -tv 35 -ti 15.5
``

# Requerimientos:

- Python 3. Python es un lenguaje de programación interpretado, de código libre, usado para la creación de este proyecto. Si usan Windows XP, deben obtener una versión de Python menor o igual a la 3.4. Cualquier duda, en www.python.org pueden consultar.
- Alguien que sepa cómo manejar alguna de las terminales cmd, powershell o unix shell.
- Cualquier sistema operativo.
