## Compile
Run `ant` in the app directory.

## Logfiles
Logfiles will automatically be stored in the home folder of the host machine.

## Launch build
Use the following to launch the middleware (from within the build directory):
```sh
java -cp . asl_project.RunMW -l external_IP -p 8000 -t 3 -s false -m localhost:11211
```
- `-l`: external IP address of the middleware host.
- `-p`: port the middleware listens to.
- `-t`: number of threads in the worker thread pool.
- `-s`: sharded reads.
- `-m`: list of memcached servers with ports.
