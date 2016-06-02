<b>Using Docker with Arogi-Demos</b>  
<hr />

*Prerequisites*  

 1. Install Docker. Their webpage has [instructions](https://docs.docker.com/engine/installation/).

 2. In Windows and OS X, launch the Docker Quickstart Terminal. Linux uses the standard Terminal.

 3. Make a local copy of arogi-demos. Type:  
    `git clone https://github.com/arogi/arogi-demos.git`


*Getting Started*

 1. Type: `docker pull arogi/circuit-web`  
    to grab the latest Arogi Docker image.

 2. Type: `docker run -it -p 80:80 -d -v ~/repos/arogi-demos/:/var/www/html arogi/circuit-web`  
    In that statement, replace `~/repos/arogi-demos/` with the pathname to your local repository.

 3. Open a web browser and enter the following into the address bar:  
     On OS X and Windows, enter `192.168.99.100`. On Linux, enter `localhost`  


*Shutting Down*  

 1. Return to the Docker terminal.

 2. Type: `docker ps -a`  
    to see a list of all local docker containers. Note the name it gives as a label. It often is something like: `silly_tonsils`

 3. To stop Docker, type: `docker stop container_name`

 4. To remove the container, type: `docker rm container_name`

 5. To remove the image, type: `docker rmi image_name` (e.g., `docker rmi arogi/circuit-web`)
