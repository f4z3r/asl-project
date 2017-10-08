# Set up clients with memtier_benchmark
for i in {1..3}
do
    ssh -o StrictHostKeyChecking=no bjakob@bjakobforaslvms${i}.westeurope.cloudapp.azure.com "
    sudo apt-get update >> ~/setup_client-${i}.log
    sudo apt-get --yes --force-yes install git unzip ant >> ~/setup_client-${i}.log
    sudo apt-get --yes --force-yes install build-essential autoconf automake libpcre3-dev libevent-dev pkg-config zlib1g-dev >> ~/setup_client-${i}.log
    wget https://github.com/RedisLabs/memtier_benchmark/archive/master.zip
    unzip master.zip
    cd memtier_benchmark-master
    autoreconf -ivf >> ~/setup_client-${i}.log
    ./configure >> ~/setup_client-${i}.log
    make >> ~/setup_client-${i}.log
    exit
    "
    scp bjakob@bjakobforaslvms${i}.westeurope.cloudapp.azure.com:~/setup_client-${i}.log /Users/jakob_beckmann/Documents/_uni/eth/_courses/2017/autumn/advanced_sys_lab/project/logs/setup_client-${i}.log
done

# Set up middleware
ssh -o StrictHostKeyChecking=no bjakob@bjakobforaslvms4.westeurope.cloudapp.azure.com "
sudo apt-get update >> ~/setup_middleware.log
sudo apt-get --yes --force-yes install git unzip ant >> setup_middleware.log
echo 'JAVA_HOME=' >> ~/setup_middleware.log
echo $JAVA_HOME >> ~/setup_middleware.log
echo 'ANT_HOME=' >> ~/setup_middleware.log
echo $ANT_HOME >> ~/setup_middleware.log
echo 'PATH=' >> ~/setup_middleware.log
echo $PATH >> ~/setup_middleware.log
exit
"
scp bjakob@bjakobforaslvms4.westeurope.cloudapp.azure.com:~/setup_middleware.log /Users/jakob_beckmann/Documents/_uni/eth/_courses/2017/autumn/advanced_sys_lab/project/logs/setup_middleware.log

# Set up memcached servers
for i in {5..8}
do
    ssh -o StrictHostKeyChecking=no bjakob@bjakobforaslvms${i}.westeurope.cloudapp.azure.com "
    sudo apt-get update >> ~/setup_server-${i}.log
    sudo apt-get install --yes --force-yes git unzip ant memcached >> ~/setup_server-${i}.log
    sudo service memcached stop
    exit
    "
    scp bjakob@bjakobforaslvms${i}.westeurope.cloudapp.azure.com:~/setup_server-${i}.log /Users/jakob_beckmann/Documents/_uni/eth/_courses/2017/autumn/advanced_sys_lab/project/logs/setup_server-${i}.log
done
