<b>Using Docker with Arogi-Demos</b>  
<hr />

*Prerequisite*  

- Install docker. Their webpage has [instructions](https://docs.docker.com/engine/installation/).

- Go to your computer's Terminal shell prompt.
    *Linux Users*
    - You don't need to do anything further.
    *OS X users*
    - You need to make sure that the docker virtual machine is attached to your terminal. Run the following commands:
      `docker-machine start` #This will ensure the vm is running. If you are sure it is you can skip this step.
      `docker-machine env && eval $(docker-machine env)`
    *Windows Users*
    - You need to make sure that the docker virtual machine is attached to your terminal. Run the following commands:
      `TBD` #I need to test this on Windows and list the proper syntax.

- <i>If running Mac OS X, initiate the docker virtual machine by entering the following three commands in the prompt</i>
  - `docker-machine start`
  - `docker-machine env`
  - `eval $(docker-machine env)`

*Getting Started*

 1. Type: `docker pull arogi/circuit-web`  
    to grab the latest Arogi docker image.

 2. Type: `docker run -it -p 80:80 -d -v ~/repos/arogi-demos/:/var/www/html arogi/circuit-web`  
    In that statement, replace `~/repos/arogi-demos/` with the pathname to your local repository. This assumes a Unix based home directory - for Windows based machines you may need something like `-v /c/Users/My\ User\ Name/repos:`. This tells the container we are creating to map your working local repo location to be within the docker container.

 3. Type `localhost`  
    in your browser address bar to play with the demos. Note that on Mac OS X and Windows this address is likely to be `192.168.99.100`

  *Shutting Down*  

 1. You can return to your local machine's command prompt by pressing `ctrl-p` followed by `ctrl-q`.

 2. Type: `docker ps -a`  
    to see a list of all local docker containers. Note the name it gives as a label. It often is something like: `silly_tonsils`.

 3. Type: `docker stop container_name` to stop docker. Note: You can restart again if you like with `docker start docker_name`.

 4. If you want to remove the container, type: `docker rm container_name`.

 5. To remove the image, type: `docker rmi image_name` (e.g., `docker rmi arogi/circuit-web`)

  *Extra Options*

  The steps above are sufficient to start your own arogi local web host.  However, if you wish to play around with the image you can do so as follows:

 1. Type: `docker ps -a`
    and note the name of the container. If you have followed the directions above you probably still have a running container.

 2. Type: `docker stop container_name`
    to stop the container

 3. Type: `docker run -it -p 80:80 -d -v ~/repos/arogi-demos/:/var/www/html arogi/circuit-web /bin/bash`
    to launch a container and start the shell. If you have pressed `ctrl-p, ctrl-q` and left the container we can re-attach to the container by typing: `docker attach container_name` to connect to the container. From there, you might need to press carriage return to get the terminal prompt.

 4. Type: `service apache2 start`  
    From within docker's terminal, this will start the container's local apache webserver.
