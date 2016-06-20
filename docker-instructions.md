<b>Using Docker with Arogi-Demos</b>  
<hr />

*Prerequisites*  

 1. These instructions allow you to use Docker to run several Arogi demos with your own input GeoJSON point data.

 2. Install Docker. Their webpage has [instructions](https://docs.docker.com/engine/installation/).

 3. In Windows and OS X, launch the Docker Quickstart Terminal. Linux uses the standard Terminal.
 
 4. Type: `git clone https://github.com/arogi/arogi-demos.git`  
    to make a local copy of the arogi-demos. Note the location of the created directory.

*Getting Started*

 1. Type: `docker pull arogi/temp-arogi-demos`  
    to grab the latest Arogi Docker image.

 2. Type: `docker run -it -p 80:80 -d -v ~/repos/arogi-demos/:/var/www/html arogi/temp-arogi-demos /bin/bash`  
    In that statement, replace `~/repos/arogi-demos/` with the pathname to the local directory of the cloned repository.
    Data used are in the /data directory. To change data files, modify the path in index.html, lines 86/87.

 3. Type: `docker ps -a`  
    to see a list of all local docker containers. Note the name it gives as a label. For the remainder of these instructions, this label will be referred to as `container_name`. The label often is something like: `silly_tonsils`
 
 4. Type: `docker attach container_name`

 3. Within the container's shell, type: `service apache2 start`  
    Note: It is possible to return to the main Docker Terminal by pressing control-p, followed by control-q.

 3. Open a web browser and enter the following into the address bar:  
     On OS X and Windows, enter `192.168.99.100`. On Linux, enter `localhost`  

*Shutting Down*  

 1. Return to the Docker terminal.

 2. To stop Docker, type: `docker stop container_name`

 3. To remove the container, type: `docker rm container_name`

 4. To remove the image, type: `docker rmi image_name` (e.g., `docker rmi arogi/temp-arogi-demos`)
