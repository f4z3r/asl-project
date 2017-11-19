# /middleware
Contains source code and distribution of the middleware.

Note that none of the following has to be performed by hand as it is run by the `automator.bash` script.

## Compile
Run `ant` in the this directory.

## Launch build
Use the following to launch the middleware (from within the `/middleware/dist` directory):
```sh
java -jar middleware -l <mw_ip> -p 8000 -t 3 -s false -m <mc_ip>:11211
```
- `-l`: IP address of the middleware host.
- `-p`: port the middleware listens to.
- `-t`: number of threads in the worker thread pool.
- `-s`: sharded reads.
- `-m`: list of memcached server IPs with ports.
