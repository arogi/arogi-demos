<b>Using Docker with Arogi-Demos</b>  
<hr />

*Prerequisites*  

 1. Install Docker. Their webpage has [instructions](https://docs.docker.com/engine/installation/).

 2. Access Docker via a Terminal shell:
    - *Linux Users*, proceed to Step 1 of Getting Started.
    - *Windows and OS X*, use the Docker Quickstart Terminal.

 3. To make a local copy of arogi-demos, in a Terminal shell, type:  
    `git clone https://github.com/arogi/arogi-demos.git`


*Getting Started*

 1. Type: `docker pull arogi/circuit-web`  
    to grab the latest Arogi docker image.

 2. Type: `docker run -it -p 80:80 -d -v ~/repos/arogi-demos/:/var/www/html arogi/circuit-web`  
    In that statement, replace `~/repos/arogi-demos/` with the pathname to your local repository. If using Windows, follow this pattern instead: `-v /c/Users/My\ User\ Name/repos:`

 3. Type `localhost`  
    in your browser address bar. On OS X and Windows, use this address: `192.168.99.100`


*Shutting Down*  

 1. Return to your local machine's command prompt by pressing `ctrl-p` followed by `ctrl-q`

 2. Type: `docker ps -a`  
    to see a list of all local docker containers. Note the name it gives as a label. It often is something like: `silly_tonsils`

 3. To stop Docker, type: `docker stop container_name`

 4. To remove the container, type: `docker rm container_name`

 5. To remove the image, type: `docker rmi image_name` (e.g., `docker rmi arogi/circuit-web`)
