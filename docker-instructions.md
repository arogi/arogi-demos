<b>Using Docker with Arogi-Demos</b>  
<hr />

*Prerequisite*  

- Install docker. Their webpage has [instructions](https://docs.docker.com/engine/installation/).

- Go to your computer's Terminal shell prompt.

*Getting Started*

1. Type: `docker pull tniblett/arogi-apache-cgi`  
to grab the latest Arogi docker image. 

2. Type: `docker run -it -p 80:80 -d -v ~/repos/arogi-demos/:/var/www/html tniblett/arogi-apache-cgi /bin/bash`  
In that statement, replace `~/repos/arogi-demos/` with the pathname to your local repository. This associates the image to your working local repo.

3. Type: `docker ps -a`  
to see a list of local docker containers. Note the name it gives as a label. It often is something like: `silly_tonsils`.

4. Type: `docker attach container_name`  
to connect to the container. From there, you might need to press carriage return to get the terminal prompt.

5. Type: `service apache2 start`  
From within docker's terminal, this will start the container's local apache webserver.

6. Type `localhost`  
in your browser address bar to play with the demos. 

*Shutting Down*  

1. You can return to your local machine's command prompt by pressing `ctrl-p` followed by `ctrl-q`.

2. Type: `docker stop container_name` to stop docker. Note: You can restart again if you like with `docker start docker_name`.

3. If you want to remove the container, type: `docker rm container_name`.

4. To remove the image, type: `docker rmi image_name` (e.g., `docker rmi tniblett/arogi-apache-cgi`)
