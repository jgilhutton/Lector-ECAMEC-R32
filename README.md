# Lector de archivos .R32 de ECAMEC.
Este es un trabajo de ingeniería inversa a los archivos R32 que generan los registradores de variables eléctricas de la empresa ECAMEC.

En el laburo, tenemos que analizar toneladas de archivos R32, de equipos de 4 series distintas, que generan mal los archivos, con factores de tension y corrientes diferentes.

ECAMEC no nos dio ninguna solución para esto, por lo que nos vemos obligados a procesar uno por uno. Insoportable.

Esta herramienta está destinada a terminar con nuestro sufrimiento y el de los demás.

# Este programa, al día de la fecha, puede leer las series:

- 0xB1 _(Monofásica)_
- 0x9C _(Monofásica)_
- 0x9B _(Monofásica)_
- 0x21 _(Monofásica)_
- 0xDB _(Trifásica)_
- 0x01 _(Trifásica)_
- 0x5B _(Trifásica)_
- 0x91 _(Trifasica)_

Las series corresponden al noveno (9°) byte del header de cada medición. Generalmente, los headers se encuentran al principio de cada archivo R32 precedidos por un byte \xff, en ese caso, el byte de la serie sería el décimo (10°) byte del archivo .R32

# Modo de uso:

```
    Modo de uso:    python ECAMEC.py -i [Directorio]|[Archivo] [Opcionales]
    Opcionales:
        -o  Directorio donde se guardan los archivos generados
            Valor por defecto: Directorio de los archivos R32
        -tv Factor de tensión   Valor por defecto: 1
        -ti Factor de corriente Valor por defecto: 1
        -v  Muestra más información en la pantalla durante el
            procesamiento.
        -vv Muestra aun más información
        -h  Muestra este mensaje

    Ejemplos:
    python ECAMEC.py -i "C:\Mediciones" -o "C:\Mediciones Procesadas"
    python ECAMEC.py -i MEDICION.R32 -tv 35 -ti 15.5
```

# Requerimientos:

- Python 3. Python es un lenguaje de programación interpretado, de código libre, usado para la creación de este proyecto. Si usan Windows XP, deben obtener una versión de Python menor o igual a la 3.4. Cualquier duda, en www.python.org pueden consultar.
- Alguien que sepa cómo manejar alguna de las terminales cmd, powershell o unix shell.
- Cualquier sistema operativo.

# Bug reports

Por favor, si encuentran algún error en el script, abran un issue en este repositorio o manden un mail a jgilhutton@gmail.com