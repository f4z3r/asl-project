# Lauch with command <local_ip> <external ip memcached:port> <test_time> >> mw.log &

sharded = "false"
threads = 3
port = 8000

cmdpart = "java -cp . asl_project.RunMW -t ${threads} -s ${sharded} -l $1 -p ${port} -m $2"

$cmdpart
$sleep $3

$ps ax | grep RunMW | grep -v grep
