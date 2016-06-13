<b>Using Docker with Arogi-Demos</b>  
<hr />

*Prerequisites*  

 1. These instructions allow you to use Docker to run several Arogi demos with your own input GeoJSON point data. Take note of the directory location and file name of your data, those will be necessary later. A [Quickstart guide](Quickstart.md) using sample data is also available.

 2. Install Docker. Their webpage has [instructions](https://docs.docker.com/engine/installation/).

 3. In Windows and OS X, launch the Docker Quickstart Terminal. Linux uses the standard Terminal.

*Getting Started*

 1. Type: `docker pull arogi/docker-arogi-demos`  
    to grab the latest Arogi Docker image.

 2. Type: `docker run -it -p 80:80 -d -v ~/repos/arogi-demos/:/var/www/html arogi/docker-arogi-demos /bin/bash`  
    In that statement, replace `~/repos/arogi-demos/` with the pathname to the local directory with your data.
    Lines 86 and 87 of index.html reference the data. Use a text editor to change those lines to include the name of your data file. 

 3. Type: `docker ps -a`  
    to see a list of all local docker containers. Note the name it gives as a label. For the remainder of these instructions, this label will be referred to as `container_name`. The label often is something like: `silly_tonsils`
 
 4. Type: `docker attach container_name`

 3. Within the container's shell, type: `service apache2 start`  
    Note: It is possible to return to the main Docker Terminal by pressing control-p, followed by control-q.

 3. Open a web browser and enter the following into the address bar:  
     On OS X and Windows, enter `192.168.99.100`. On Linux, enter `localhost`  

*Shutting Down*  

 1. Return to the Docker terminal.

 2. Type: `docker ps -a`  
    to see a list of all local docker containers. Note the name it gives as a label. It often is something like: `silly_tonsils`

 3. To stop Docker, type: `docker stop container_name`

 4. To remove the container, type: `docker rm container_name`

 5. To remove the image, type: `docker rmi image_name` (e.g., `docker rmi arogi/circuit-web`)
