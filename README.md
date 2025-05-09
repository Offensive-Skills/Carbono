> ⚠️ **Este repositorio está obsoleto**  
>  
> Esta herramienta ya no se encuentra en desarrollo ni recibe mantenimiento.  
> Ahora debes usar la nueva aplicación **Grafeno**, disponible en:  
> 👉 [https://github.com/Offensive-Skills/Grafeno](https://github.com/Offensive-Skills/Grafeno)  
>  

# Introducción

![image](./images/carbono.png)

Herramienta para la automatización de despliegue de entornos para realizar retos de **pentesting**.

Cuenta con centenares de retos de ciberseguridad, tanto de carácter individual, como otros asociados a cursos de la plataforma [offs.es](https://offs.es)

> Todas los entornos de prueba serán desplegados en el entorno local del usuario, por lo que es perfecta para llevar a cabo pruebas de pentración offline y mejorar las **skills** de un usuario en **ciberseguridad**




# Instalación

Para la intalación de esta herramienta debemos ejecutar el fichero de **setup**.

> Se recomienda ejecutar `apt upgrade` para tener todos los paquetes actualizados y no surjan problemas de incompatibilidad. Hay que tener en cuenta que si el equipo lleva mucho sin actualizarse o es una maquina virtual recien instalada este comando podría demorarse mucho tiempo (aun asi es recomendable su ejecución).

```bash
sudo ./setup.sh
```

> Si no tenías instalado docker previamente es necesario reinicar el equipo para que la configuración de permisos sea correcta.

1. Actualiza los paquetes del sistemas para asegurarnos de tener las últimas versiones de las herramientas.
2. Instala python3 y pip3.
3. Instala docker y docker-compose.
4. Configura docker.
5. Instala las librerías de pip necesarias por la herramienta (customtkinter, pillow y requests).

# Configuración de entorno

Esta herramienta permite la descarga de archivos con retos y writeups. Por defecto, se descargarán en una carpeta llamada `offensiveSkills`, que se creará en el directorio **home (./~)** del usuario. Si deseamos que se esta carpeta se cree en otro repositorio debemos de especificarlo usando una variable global llamada **OFFS_PATH**

```bash
export OFFS_PATH="~/Desktop/"
echo 'export OFFS_PATH="~/Desktop/"' >  ~/.bashrc
```

O en el caso de que usemos otro tipo de shell como zsh(kali linux):

```bash
export OFFS_PATH="~/Desktop/"
echo 'export OFFS_PATH="~/Desktop/"' >  ~/.zshrc
```

# Uso de la herramienta

Para iniciar la herramienta debemos ejecutar un comando como el siguiente:

```bash
source venv_carbono/bin/activate
python3 app.py --username username --api-token api_token
```

Donde:
- `username`: Debe ser nuestro nombre de usuario.
- `api_token`: Token asociado al usuario.

Si no tenemos un token o no estamos registrados debemos de hacerlo en [offs.es](https://offs.es).


Para salir del entorno de virtual de python **(venv)** ejectar:

```bash
deactivate
```

> El script setup.sh es compatible con distribuciones que utilicen el instalador de paquetes apt (debian), incluido dentro de WSL. En el caso de usar WSL hay que configurarlo correctamente para poder acceder a la red de docker desde el equipo anfitrión.

---
# License 
Carbono © 2024 by Offensive Skills is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International

You can read more about the License in the [`LICENSE` documentation](./LICENSE.md)
