T-Recs: un servicio de recomendación basado en ontologías.
=========================================================

Nótese que, para poder utilizar este software, deberá contar con suficiente espacio como para almacenar los 100,000 documentos y 14,000 categorías de la colección documental de prueba, así como conocimientos básicos de django y configuración de servidores web.

Este servicio está basado en python2.6, por lo que habrá de tenerlo instalado.

PASOS DE INSTALACIÓN
--------------------
0. Se recomienda utilizarlo en un sistema *nix (linux u OSX). Se deberá contar con los siguientes paquetes de sistema instalados:
gettext
xapian-tools
python-xapian (refiérase a <http://code.google.com/p/djapian/wiki/Installation>)

1. Instalar pip: <http://pypi.python.org/pypi/pip/0.7.2>
    (deberá descargarlo, extraerlo y ejecutar `sudo python setup.py install`)
2. Instalar las dependencias
    `pip install -r requirements.txt`
3. Configurar la base de datos y el servidor de trabajos asíncronos:
    *Se recomienda usar postgresql y crear la base de datos, usuario y contraseña especificados en el archivo `lebrixen/settings.py`
    * Si no se desea utilizar postgres, cambie el motor de base de datos al deseado en el archivo `lebrixen/settings.py` note
      que en este caso no podrá utilizar la colección de datos de prueba y deberá seguir lo detallado en el paso 6.
    * Si se utiliza postgres, se habrá de cargar la colección de datos de prueba como sigue:
        `pg_restore data/TestData.sql`
     * Para la cola de trabajos asíncrona, se deberá instalar rabbitmq (siguiendo estos pasos <http://ask.github.com/celery/getting-started/broker-installation.html> o <http://www.rabbitmq.com/install.html>) y establecer el nombre de usuario y contraseña incluidos en `lebrixen/settings.py`

4. Cargar los datos de los índices.
    + **[OPCIONAL, sólo si no se utiliza la base de datos de prueba]** Deberá ejecutarse el web crawler de la siguiente manera (se utilizarán las urls del archivo data/topics_urls como urls iniciales):
    `scrapy-ctl.py crawl dmoz.org` 
      Esto actualizará las carpetas HTML y PDF. Luego, habrá de actualizar la ontología, llenar la colección documentar y ponderar la ontología, para ello, ejecute los siguientes comandos en orden (dada la gran cantidad de documentos, pueden tardar varias horas):
        - `lebrixen/manage.py update_ontology`
        - `lebrixen/manage.py update_documentdb`
        - `lebrixen/manage.py ponder_categories`
    + Entrenar los índices: luego de haber creado o cargado la base de datos de prueba, utilícese el siguiente comando para entrenar al clasificador de categorías
    `lebrixen/manage.py train_category_classifier`
     y para crear el índice documental
    `lebrixen/manage.py index --rebuild`
        
4. Edite el archivo `lebrixen/settings.py` y reemplace `<YOUR_HOME_FOLDER>` con su directorio principal (usualmente, `/home/<nombre_de_usuario>`)
6. A la hora de servirlo, puede utilizar el servidor de prueba de django o apache (se incluye una configuración de ejemplo en data/apache_conf). En todo caso, asegúrese de ejecutar el proceso del servidor de trabajos asíncronos así
    `lebrixen/manage.py celeryd`
    o mediante el método detallado en <http://ask.github.com/celery/cookbook/daemonizing.html>


Téngase en mente también que este proyecto seguirá evolucionando luego de su entrega a UNITEC en Julio de 2010, por lo que podrá acceder a la versión más reciente del código fuente aquí:
    <http://gitorious.org/magritte>
    o
    <http://github.com/lfborjas/Magritte>

Cualquier consulta, puede contactar al autor en
 [Twitter](http://twitter.com/lfborjas) o
 [Sitio Personal](http://www.lfborjas.com)
o mediante correo electrónico a 
 me@lfborjas.com, 
 luis.borjas@escolarea.com, 
 lfborjas@unitec.edu


