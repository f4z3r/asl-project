# Lauch with command <local_ip> <external ip memcached:port> <test_time> >> mw.log &
#
# Note this has a dependency on killme.sh

sharded="false"
threads=3
port=8000

commandkill="./killme.sh $3 &"
$commandkill

cmdpart = "java -cp . asl_project.RunMW -t ${threads} -s ${sharded} -l $1 -p ${port} -m $2"
$cmdpart
