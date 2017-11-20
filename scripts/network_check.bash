#!/bin/bash

# Do not forget to remove the hosts from the known_hosts file before launching
# the experiments
#
# The following is a failsafe if the .shh/config is not set up properly with:
#   Host *      # (or individual hostnames)
#       StrictHostKeyChecking no

ssh='ssh -o StrictHostKeyChecking=no'
scp='scp -q -o StrictHostKeyChecking=no'

# Addresses of cloud machines
export client1_pub="bjakob@bjakobforaslvms1.westeurope.cloudapp.azure.com";
export client2_pub="bjakob@bjakobforaslvms2.westeurope.cloudapp.azure.com";
export client3_pub="bjakob@bjakobforaslvms3.westeurope.cloudapp.azure.com";
export mw1_pub="bjakob@bjakobforaslvms4.westeurope.cloudapp.azure.com";
export mw2_pub="bjakob@bjakobforaslvms5.westeurope.cloudapp.azure.com";
export server1_pub="bjakob@bjakobforaslvms6.westeurope.cloudapp.azure.com";
export server2_pub="bjakob@bjakobforaslvms7.westeurope.cloudapp.azure.com";
export server3_pub="bjakob@bjakobforaslvms8.westeurope.cloudapp.azure.com";

export client1="10.0.0.9";
export client2="10.0.0.6";
export client3="10.0.0.8";
export mw1="10.0.0.5";      export mw1_port="8000";
export mw2="10.0.0.10";     export mw2_port="8000";
export server1="10.0.0.7";  export server1_port="11211";
export server2="10.0.0.4";  export server2_port="11211";
export server3="10.0.0.11"; export server3_port="11211";

final_dir=/Users/jakob_beckmann/Documents/_uni/eth/_courses/2017/autumn/advanced_sys_lab/gitlab/asl-fall17-project/logs;


function network_check {
    echo "Starting network check ...";

    ${ssh} ${mw1_pub} "iperf -s &" &
    ${ssh} ${mw2_pub} "iperf -s &" &
    ${ssh} ${server1_pub} "iperf -s &" &
    ${ssh} ${server2_pub} "iperf -s &" &
    ${ssh} ${server3_pub} "iperf -s &" &

    ${ssh} ${client1_pub} "echo 'SERVER 1' >> client1_network.log";
    ${ssh} ${client2_pub} "echo 'SERVER 1' >> client2_network.log";
    ${ssh} ${client3_pub} "echo 'SERVER 1' >> client3_network.log";
    ${ssh} ${mw1_pub} "echo 'SERVER 1' >> mw1_network.log"
    ${ssh} ${mw2_pub} "echo 'SERVER 1' >> mw2_network.log"

    ${ssh} ${client1_pub} "iperf -c ${server1} >> client1_network.log";
    ${ssh} ${client2_pub} "iperf -c ${server1} >> client2_network.log";
    ${ssh} ${client3_pub} "iperf -c ${server1} >> client3_network.log";
    ${ssh} ${mw1_pub} "iperf -c ${server1} >> mw1_network.log";
    ${ssh} ${mw2_pub} "iperf -c ${server1} >> mw2_network.log";

    ${ssh} ${client1_pub} "echo 'SERVER 2' >> client1_network.log";
    ${ssh} ${client2_pub} "echo 'SERVER 2' >> client2_network.log";
    ${ssh} ${client3_pub} "echo 'SERVER 2' >> client3_network.log";
    ${ssh} ${mw1_pub} "echo 'SERVER 2' >> mw1_network.log"
    ${ssh} ${mw2_pub} "echo 'SERVER 2' >> mw2_network.log"

    ${ssh} ${client1_pub} "iperf -c ${server2} >> client1_network.log";
    ${ssh} ${client2_pub} "iperf -c ${server2} >> client2_network.log";
    ${ssh} ${client3_pub} "iperf -c ${server2} >> client3_network.log";
    ${ssh} ${mw1_pub} "iperf -c ${server2} >> mw1_network.log";
    ${ssh} ${mw2_pub} "iperf -c ${server2} >> mw2_network.log";

    ${ssh} ${client1_pub} "echo 'SERVER 3' >> client1_network.log";
    ${ssh} ${client2_pub} "echo 'SERVER 3' >> client2_network.log";
    ${ssh} ${client3_pub} "echo 'SERVER 3' >> client3_network.log";
    ${ssh} ${mw1_pub} "echo 'SERVER 3' >> mw1_network.log"
    ${ssh} ${mw2_pub} "echo 'SERVER 3' >> mw2_network.log"

    ${ssh} ${client1_pub} "iperf -c ${server3} >> client1_network.log";
    ${ssh} ${client2_pub} "iperf -c ${server3} >> client2_network.log";
    ${ssh} ${client3_pub} "iperf -c ${server3} >> client3_network.log";
    ${ssh} ${mw1_pub} "iperf -c ${server3} >> mw1_network.log";
    ${ssh} ${mw2_pub} "iperf -c ${server3} >> mw2_network.log";

    ${ssh} ${client1_pub} "echo 'MW 1' >> client1_network.log";
    ${ssh} ${client2_pub} "echo 'MW 1' >> client2_network.log";
    ${ssh} ${client3_pub} "echo 'MW 1' >> client3_network.log";

    ${ssh} ${client1_pub} "iperf -c ${mw1} >> client1_network.log";
    ${ssh} ${client2_pub} "iperf -c ${mw1} >> client2_network.log";
    ${ssh} ${client3_pub} "iperf -c ${mw1} >> client3_network.log";

    ${ssh} ${client1_pub} "echo 'MW 2' >> client1_network.log";
    ${ssh} ${client2_pub} "echo 'MW 2' >> client2_network.log";
    ${ssh} ${client3_pub} "echo 'MW 2' >> client3_network.log";

    ${ssh} ${client1_pub} "iperf -c ${mw2} >> client1_network.log";
    ${ssh} ${client2_pub} "iperf -c ${mw2} >> client2_network.log";
    ${ssh} ${client3_pub} "iperf -c ${mw2} >> client3_network.log";


    ${ssh} ${mw1_pub} "sudo pkill -f iperf";
    ${ssh} ${mw2_pub} "sudo pkill -f iperf";
    ${ssh} ${server1_pub} "sudo pkill -f iperf";
    ${ssh} ${server2_pub} "sudo pkill -f iperf";
    ${ssh} ${server3_pub} "sudo pkill -f iperf";


    echo "Gathering data ...";
    ${scp} ${client1_pub}:client* ${final_dir}
    ${scp} ${client2_pub}:client* ${final_dir}
    ${scp} ${client3_pub}:client* ${final_dir}
    ${scp} ${mw1}:mw* ${final_dir}
    ${scp} ${mw2}:mw* ${final_dir}
}



if [ "${1}" == "run" ]; then
    network_check;
fi
