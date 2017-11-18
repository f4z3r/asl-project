#!/bin/bash

# Note that the following folder structure will be respected for all experiments:
# experiment_name(date)/
#   /ping_mw_NN.log
#   /ratio
#       /sharded vs non-sharded
#           /n_workers
#               /m_clients
#                   /client_NN_TT_RR.log (TT subclient)
#                   /mw_NN_RR.log
#                   /dstat
#                       /dstat_client_NN_RR.log
#                       /dstat_mw_NN_RR.log
#                       /dstat_server_NN_RR.log


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


function upload {
    # Compile the middleware
    rm ../middleware/dist/*;
    (cd ../middleware; ant);
    echo "Middleware compiled";

    # Copy middleware into home of cloud machines
    ${scp} ../middleware/dist/middleware-bjakob.jar ${mw1_pub}:;
    ${scp} ../middleware/dist/middleware-bjakob.jar ${mw2_pub}:;
    echo "Middleware copied to cloud hosts";
}

function populate {
    echo "Launching memcached ..."
    # Launch memcached instances on the server machines
    ${ssh} ${mw2_pub} "sudo service memcached stop" &
    ${ssh} ${server1_pub} "sudo service memcached stop; memcached -p ${server1_port} -t 1 &" &
    ${ssh} ${server2_pub} "sudo service memcached stop; memcached -p ${server2_port} -t 1 &" &
    ${ssh} ${server3_pub} "sudo service memcached stop; memcached -p ${server3_port} -t 1 &" &

    sleep 3;

    echo "Memcached instances launched on all servers";

    echo "Populating memcached instances ...";
    #parameters for memtier
    CT=1;
    VC=1;
    runtime=30;
    ratio=1:0;

    ${ssh} ${client1_pub} "./memtier_benchmark-master/memtier_benchmark -s ${server1} -p ${server1_port} -c ${VC} -t ${CT} --ratio=${ratio} --test-time=${runtime} --protocol=memcache_text --key-pattern=P:P --expiry-range=9999-10000 --key-maximum=10000 --hide-histogram -d 1024 &> empty.log &" &
    ${ssh} ${client2_pub} "./memtier_benchmark-master/memtier_benchmark -s ${server2} -p ${server2_port} -c ${VC} -t ${CT} --ratio=${ratio} --test-time=${runtime} --protocol=memcache_text --key-pattern=P:P --expiry-range=9999-10000 --key-maximum=10000 --hide-histogram -d 1024 &> empty.log &" &
    ${ssh} ${client3_pub} "./memtier_benchmark-master/memtier_benchmark -s ${server3} -p ${server3_port} -c ${VC} -t ${CT} --ratio=${ratio} --test-time=${runtime} --protocol=memcache_text --key-pattern=P:P --expiry-range=9999-10000 --key-maximum=10000 --hide-histogram -d 1024 &> empty.log &" &

    sleeptime=$(( $runtime + 20 ))
    sleep ${sleeptime};

    ${ssh} ${client1_pub} "rm *.log";
    ${ssh} ${client2_pub} "rm *.log";
    ${ssh} ${client3_pub} "rm *.log";

    echo "Memcached instances populated";
}

function cleanup {
    echo "Cleaning up ...";
    ${ssh} ${mw1_pub} "sudo pkill -f middleware";
    ${ssh} ${mw2_pub} "sudo pkill -f middleware";
    ${ssh} ${mw2_pub} "sudo service memcached stop";
    ${ssh} ${server1_pub} "sudo pkill -f memcached; sudo service memcached stop";
    ${ssh} ${server2_pub} "sudo pkill -f memcached; sudo service memcached stop";
    ${ssh} ${server3_pub} "sudo pkill -f memcached; sudo service memcached stop";
    echo "Finished cleaning up.";
}

function pinger {
    echo "    Launching ping script ...";

    ${ssh} ${mw1_pub} "echo 'PING MIDDLEWARE 1' > mw_1_ping.log";
    ${ssh} ${mw2_pub} "echo 'PING MIDDLEWARE 2' > mw_2_ping.log";

    echo "        Pinging clients.";
    for machine in client{1..3}; do
        ${ssh} ${mw1_pub} "echo 'mw1 > ${machine}' >> mw_1_ping.log; ping -t 5 -i 0.2 ${!machine} >> mw_1_ping.log &" &
        ${ssh} ${mw2_pub} "echo 'mw2 > ${machine}' >> mw_2_ping.log; ping -t 5 -i 0.2 ${!machine} >> mw_2_ping.log &" &
        sleep 6;
        ${ssh} ${mw1_pub} "sudo pkill -f ping";
        ${ssh} ${mw2_pub} "sudo pkill -f ping";
    done

    echo "        Pinging servers.";
    for machine in server{1..3}; do
        ${ssh} ${mw1_pub} "echo 'mw1 > ${machine}' >> mw_1_ping.log; ping -t 5 -i 0.2 ${!machine} >> mw_1_ping.log &" &
        ${ssh} ${mw2_pub} "echo 'mw2 > ${machine}' >> mw_2_ping.log; ping -t 5 -i 0.2 ${!machine} >> mw_2_ping.log &" &
        sleep 6;
        ${ssh} ${mw1_pub} "sudo pkill -f ping";
        ${ssh} ${mw2_pub} "sudo pkill -f ping";
    done

    echo "    Ping finished.";
}


# =================================================================================
# =================================================================================
# Benchmark memcached
# =================================================================================
# =================================================================================
function benchmark_memcached {
    echo "Setting up benchmark_memcached ...";
    mydate=$(date +%Y-%m-%d_%Hh%M);
    log_dir="/Users/jakob_beckmann/Desktop/logs/benchmark_memcached(${mydate})"
    mkdir -p ${log_dir};


    pinger;

    echo "    Retreiving ping data.";
    ${scp} ${mw1_pub}:mw* ${log_dir};
    ${ssh} ${mw1_pub} "rm *.log";

    ${scp} ${mw2_pub}:mw* ${log_dir};
    ${ssh} ${mw2_pub} "rm *.log";

    runtime=90;
    memtier_options="--protocol=memcache_text --expiry-range=9999-10000 --key-maximum=10000 --test-time=${runtime} --data-size=1024";

    # Config:
    threads=2;
    operations=(0:1 1:0);
    is_sharded=false;
    worker_list=no;
    client_list=(2 4 8 16 24 32 40 48 56);
    repetitions=(1 2 3);

    echo "Starting benchmark_memcached ...";
    for op in "${operations[@]}"; do
        mkdir ${log_dir}/ratio_${op};
        for sharded in "${is_sharded[@]}"; do
            mkdir ${log_dir}/ratio_${op}/sharded_${sharded};
            for workers in "${worker_list[@]}"; do
                mkdir ${log_dir}/ratio_${op}/sharded_${sharded}/workers_${workers};
                for clients in "${client_list[@]}"; do
                    cwd=${log_dir}/ratio_${op}/sharded_${sharded}/workers_${workers}/clients_${clients};
                    mkdir ${cwd};
                    mkdir ${cwd}/dstat;
                    echo "    Launching with op: ${op}, sharded: ${sharded}, workers: ${workers}, clients: ${clients}";
                    for rep in "${repetitions[@]}"; do
                        echo "        Launching repetition ${rep} ...";

                        ${ssh} ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${server1} --port=${server1_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} &> client_1_1_${rep}.log &" &
                        ${ssh} ${client1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_1_${rep}.log &" &

                        ${ssh} ${client2_pub} "./memtier_benchmark-master/memtier_benchmark --server=${server1} --port=${server1_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} &> client_2_1_${rep}.log &" &
                        ${ssh} ${client2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_2_${rep}.log &" &

                        ${ssh} ${client3_pub} "./memtier_benchmark-master/memtier_benchmark --server=${server1} --port=${server1_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} &> client_3_1_${rep}.log &" &
                        ${ssh} ${client3_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_3_${rep}.log &" &

                        ${ssh} ${server1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_1_${rep}.log &" &

                        sleep $(( ${runtime} + 5 ))

                    done

                    echo "        All repetitions finished, gathering data ...";
                    ${scp} ${client1_pub}:client* ${cwd};
                    ${scp} ${client1_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${client1_pub} "rm client* dstat*";

                    ${scp} ${client2_pub}:client* ${cwd};
                    ${scp} ${client2_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${client2_pub} "rm client* dstat*";

                    ${scp} ${client3_pub}:client* ${cwd};
                    ${scp} ${client3_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${client3_pub} "rm client* dstat*";

                    ${scp} ${server1_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${server1_pub} "rm dstat*";

                    echo "        Finished gathering data.";
                done
            done
        done
    done

    echo "    Experiment finished, reordering data ...";
    mv /Users/jakob_beckmann/Desktop/logs/** ${final_dir};

    echo "benchmark_memcached finished";
}



# =================================================================================
# =================================================================================
# Benchmark clients
# =================================================================================
# =================================================================================
function benchmark_clients {
    echo "Setting up benchmark_clients ...";
    mydate=$(date +%Y-%m-%d_%Hh%M);
    log_dir="/Users/jakob_beckmann/Desktop/logs/benchmark_clients(${mydate})"
    mkdir -p ${log_dir};

    pinger;

    echo "    Retreiving ping data.";
    ${scp} ${mw1_pub}:mw* ${log_dir};
    ${ssh} ${mw1_pub} "rm *.log";

    ${scp} ${mw2_pub}:mw* ${log_dir};
    ${ssh} ${mw2_pub} "rm *.log";

    runtime=90;
    memtier_options="--protocol=memcache_text --expiry-range=9999-10000 --key-maximum=10000 --test-time=${runtime} --data-size=1024";

    # Config:
    threads=1;
    operations=(0:1 1:0);
    is_sharded=false;
    worker_list=no;
    client_list=(2 4 8 16 24 32 40 48 56);
    repetitions=(1 2 3);

    echo "Starting benchmark_clients ...";
    for op in "${operations[@]}"; do
        mkdir ${log_dir}/ratio_${op};
        for sharded in "${is_sharded[@]}"; do
            mkdir ${log_dir}/ratio_${op}/sharded_${sharded};
            for workers in "${worker_list[@]}"; do
                mkdir ${log_dir}/ratio_${op}/sharded_${sharded}/workers_${workers};
                for clients in "${client_list[@]}"; do
                    cwd=${log_dir}/ratio_${op}/sharded_${sharded}/workers_${workers}/clients_${clients};
                    mkdir ${cwd};
                    mkdir ${cwd}/dstat;
                    echo "    Launching with op: ${op}, sharded: ${sharded}, workers: ${workers}, clients: ${clients}";
                    for rep in "${repetitions[@]}"; do
                        echo "        Launching repetition ${rep} ...";

                        ${ssh} ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${server1} --port=${server1_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} &> client_1_1_${rep}.log" &
                        ${ssh} ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${server2} --port=${server2_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} &> client_1_2_${rep}.log" &

                        ${ssh} ${client1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_1_${rep}.log" &

                        ${ssh} ${server1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_1_${rep}.log" &
                        ${ssh} ${server2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_2_${rep}.log" &

                        sleep $(( ${runtime} + 5 ))

                    done

                    echo "        All repetitions finished, gathering data ...";
                    ${scp} ${client1_pub}:client* ${cwd};
                    ${scp} ${client1_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${client1_pub} "rm client* dstat*";

                    ${scp} ${server1_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${server1_pub} "rm dstat*";

                    ${scp} ${server2_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${server2_pub} "rm dstat*";

                    echo "        Finished gathering data.";
                done
            done
        done
    done

    echo "    Experiment finished, reordering data ...";
    mv /Users/jakob_beckmann/Desktop/logs/** ${final_dir};

    echo "benchmark_clients finished";
}



# =================================================================================
# =================================================================================
# Benchmark with one middleware
# =================================================================================
# =================================================================================
function benchmark_1mw {
    echo "Setting up benchmark_1mw ...";
    mydate=$(date +%Y-%m-%d_%Hh%M);
    log_dir="/Users/jakob_beckmann/Desktop/logs/benchmark_1mw(${mydate})"
    mkdir -p ${log_dir};

    pinger;

    echo "    Retreiving ping data.";
    ${scp} ${mw1_pub}:mw* ${log_dir};
    ${ssh} ${mw1_pub} "rm *.log";

    ${scp} ${mw2_pub}:mw* ${log_dir};
    ${ssh} ${mw2_pub} "rm *.log";

    runtime=90;
    memtier_options="--protocol=memcache_text --expiry-range=9999-10000 --key-maximum=10000 --test-time=${runtime} --data-size=1024";

    # Config:
    threads=2;
    operations=(0:1 1:0);
    is_sharded=false;
    worker_list=(8 16 32 64);
    client_list=(2 4 8 16 24 32 40 48 56);
    repetitions=(1 2 3);

    echo "Starting benchmark_1mw ...";
    for op in "${operations[@]}"; do
        mkdir ${log_dir}/ratio_${op};
        for sharded in "${is_sharded[@]}"; do
            mkdir ${log_dir}/ratio_${op}/sharded_${sharded};
            for workers in "${worker_list[@]}"; do
                mkdir ${log_dir}/ratio_${op}/sharded_${sharded}/workers_${workers};
                for clients in "${client_list[@]}"; do
                    cwd=${log_dir}/ratio_${op}/sharded_${sharded}/workers_${workers}/clients_${clients};
                    mkdir ${cwd};
                    mkdir ${cwd}/dstat;
                    echo "    Launching with op: ${op}, sharded: ${sharded}, workers: ${workers}, clients: ${clients}";
                    for rep in "${repetitions[@]}"; do
                        echo "        Launching repetition ${rep} ...";

                        ${ssh} ${mw1_pub} "java -jar middleware-bjakob.jar -l ${mw1} -p ${mw1_port} -s ${sharded} -t ${workers} -m ${server1}:${server1_port} &> mw_1_${rep}.log &" &
                        ${ssh} ${mw1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_mw_1_${rep}.log &" &

                        # Make sure the middleware runs ...
                        sleep 2;

                        ${ssh} ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} &> client_1_1_${rep}.log" &
                        ${ssh} ${client1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_1_${rep}.log &" &

                        ${ssh} ${server1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_1_${rep}.log &" &

                        sleep $(( ${runtime} + 5 ))

                        # Kill the middleware to get data
                        ${ssh} ${mw1_pub} "sudo pkill -f middleware";

                    done

                    echo "        All repetitions finished, gathering data ...";
                    ${scp} ${mw1_pub}:mw* ${cwd};
                    ${scp} ${mw1_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${mw1_pub} "rm mw* dstat*";

                    ${scp} ${client1_pub}:client* ${cwd};
                    ${scp} ${client1_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${client1_pub} "rm client* dstat*";

                    ${scp} ${server1_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${server1_pub} "rm dstat*";

                    echo "        Finished gathering data.";
                done
            done
        done
    done

    echo "    Experiment finished, gathering middleware system data";
    ${scp} ${mw1_pub}:analysis.log ${log_dir};
    ${scp} ${mw1_pub}:system_report.log ${log_dir};
    ${ssh} ${mw1_pub} "rm ana* sys*";

    echo "    Reordering data ...";
    mv /Users/jakob_beckmann/Desktop/logs/** ${final_dir};

    echo "benchmark_1mw finished";
}



# =================================================================================
# =================================================================================
# Benchmark with two middlewares
# =================================================================================
# =================================================================================
function benchmark_2mw {
    echo "Setting up benchmark_2mw ...";
    mydate=$(date +%Y-%m-%d_%Hh%M);
    log_dir="/Users/jakob_beckmann/Desktop/logs/benchmark_2mw(${mydate})"
    mkdir -p ${log_dir};

    pinger;

    echo "    Retreiving ping data.";
    ${scp} ${mw1_pub}:mw* ${log_dir};
    ${ssh} ${mw1_pub} "rm *.log";

    ${scp} ${mw2_pub}:mw* ${log_dir};
    ${ssh} ${mw2_pub} "rm *.log";

    runtime=90;
    memtier_options="--protocol=memcache_text --expiry-range=9999-10000 --key-maximum=10000 --test-time=${runtime} --data-size=1024";

    # Config:
    threads=1;
    operations=(0:1 1:0);
    is_sharded=false;
    worker_list=(8 16 32 64);
    client_list=(2 4 8 16 24 32 40 48 56);
    repetitions=(1 2 3);

    echo "Starting benchmark_2mw ...";
    for op in "${operations[@]}"; do
        mkdir ${log_dir}/ratio_${op};
        for sharded in "${is_sharded[@]}"; do
            mkdir ${log_dir}/ratio_${op}/sharded_${sharded};
            for workers in "${worker_list[@]}"; do
                mkdir ${log_dir}/ratio_${op}/sharded_${sharded}/workers_${workers};
                for clients in "${client_list[@]}"; do
                    cwd=${log_dir}/ratio_${op}/sharded_${sharded}/workers_${workers}/clients_${clients};
                    mkdir ${cwd};
                    mkdir ${cwd}/dstat;
                    echo "    Launching with op: ${op}, sharded: ${sharded}, workers: ${workers}, clients: ${clients}";
                    for rep in "${repetitions[@]}"; do
                        echo "        Launching repetition ${rep} ...";

                        ${ssh} ${mw1_pub} "java -jar middleware-bjakob.jar -l ${mw1} -p ${mw1_port} -s ${sharded} -t ${workers} -m ${server1}:${server1_port} &> mw_1_${rep}.log &" &
                        ${ssh} ${mw2_pub} "java -jar middleware-bjakob.jar -l ${mw2} -p ${mw2_port} -s ${sharded} -t ${workers} -m ${server1}:${server1_port} &> mw_2_${rep}.log &" &
                        ${ssh} ${mw1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_mw_1_${rep}.log &" &
                        ${ssh} ${mw2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_mw_2_${rep}.log &" &

                        # Make sure the middlewares run ...
                        sleep 2;

                        ${ssh} ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} &> client_1_1_${rep}.log" &
                        ${ssh} ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw2} --port=${mw2_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} &> client_1_2_${rep}.log" &
                        ${ssh} ${client1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_1_${rep}.log &" &

                        ${ssh} ${server1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_1_${rep}.log &" &

                        sleep $(( ${runtime} + 5 ))

                        # Kill the middlewares to get data
                        ${ssh} ${mw1_pub} "sudo pkill -f middleware";
                        ${ssh} ${mw2_pub} "sudo pkill -f middleware";
                    done

                    echo "        All repetitions finished, gathering data ...";
                    ${scp} ${mw1_pub}:mw* ${cwd};
                    ${scp} ${mw1_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${mw1_pub} "rm mw* dstat*";

                    ${scp} ${mw2_pub}:mw* ${cwd};
                    ${scp} ${mw2_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${mw2_pub} "rm mw* dstat*";

                    ${scp} ${client1_pub}:client* ${cwd};
                    ${scp} ${client1_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${client1_pub} "rm client* dstat*";

                    ${scp} ${server1_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${server1_pub} "rm dstat*";

                    echo "        Finished gathering data.";
                done
            done
        done
    done

    echo "    Experiment finished, gathering middleware system data";
    ${scp} ${mw1_pub}:analysis.log ${log_dir}/analysis1.log;
    ${scp} ${mw1_pub}:system_report.log ${log_dir}/system_report1.log;
    ${ssh} ${mw1_pub} "rm ana* sys*";

    ${scp} ${mw2_pub}:analysis.log ${log_dir}/analysis2.log;
    ${scp} ${mw2_pub}:system_report.log ${log_dir}/system_report2.log;
    ${ssh} ${mw2_pub} "rm ana* sys*";

    echo "    Reordering data ...";
    mv /Users/jakob_beckmann/Desktop/logs/** ${final_dir};

    echo "benchmark_2mw finished";
}



# =================================================================================
# =================================================================================
# Throughput of writes
# =================================================================================
# =================================================================================
function throughput_writes {
    echo "Setting up throughput_writes ...";
    mydate=$(date +%Y-%m-%d_%Hh%M);
    log_dir="/Users/jakob_beckmann/Desktop/logs/throughput_writes(${mydate})"
    mkdir -p ${log_dir};

    pinger;

    echo "    Retreiving ping data.";
    ${scp} ${mw1_pub}:mw* ${log_dir};
    ${ssh} ${mw1_pub} "rm *.log";

    ${scp} ${mw2_pub}:mw* ${log_dir};
    ${ssh} ${mw2_pub} "rm *.log";

    runtime=90;
    memtier_options="--protocol=memcache_text --expiry-range=9999-10000 --key-maximum=10000 --test-time=${runtime} --data-size=1024";

    # Config:
    threads=1;
    operations=1:0;
    is_sharded=false;
    worker_list=(8 16 32 64);
    client_list=(2 4 8 16 24 32 40 48 56);
    repetitions=(1 2 3);

    echo "Starting throughput_writes ...";
    for op in "${operations[@]}"; do
        mkdir ${log_dir}/ratio_${op};
        for sharded in "${is_sharded[@]}"; do
            mkdir ${log_dir}/ratio_${op}/sharded_${sharded};
            for workers in "${worker_list[@]}"; do
                mkdir ${log_dir}/ratio_${op}/sharded_${sharded}/workers_${workers};
                for clients in "${client_list[@]}"; do
                    cwd=${log_dir}/ratio_${op}/sharded_${sharded}/workers_${workers}/clients_${clients};
                    mkdir ${cwd};
                    mkdir ${cwd}/dstat;
                    echo "    Launching with op: ${op}, sharded: ${sharded}, workers: ${workers}, clients: ${clients}";
                    for rep in "${repetitions[@]}"; do
                        echo "        Launching repetition ${rep} ...";

                        ${ssh} ${mw1_pub} "java -jar middleware-bjakob.jar -l ${mw1} -p ${mw1_port} -s ${sharded} -t ${workers} -m ${server1}:${server1_port} ${server2}:${server2_port} ${server3}:${server3_port} &> mw_1_${rep}.log &" &
                        ${ssh} ${mw2_pub} "java -jar middleware-bjakob.jar -l ${mw2} -p ${mw2_port} -s ${sharded} -t ${workers} -m ${server1}:${server1_port} ${server2}:${server2_port} ${server3}:${server3_port} &> mw_2_${rep}.log &" &
                        ${ssh} ${mw1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_mw_1_${rep}.log &" &
                        ${ssh} ${mw2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_mw_2_${rep}.log &" &

                        # Make sure the middlewares run ...
                        sleep 2;

                        ${ssh} ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} &> client_1_1_${rep}.log" &
                        ${ssh} ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw2} --port=${mw2_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} &> client_1_2_${rep}.log" &
                        ${ssh} ${client1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_1_${rep}.log &" &

                        ${ssh} ${client2_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} &> client_2_1_${rep}.log" &
                        ${ssh} ${client2_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw2} --port=${mw2_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} &> client_2_2_${rep}.log" &
                        ${ssh} ${client2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_2_${rep}.log &" &

                        ${ssh} ${client3_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} &> client_3_1_${rep}.log" &
                        ${ssh} ${client3_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw2} --port=${mw2_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} &> client_3_2_${rep}.log" &
                        ${ssh} ${client3_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_3_${rep}.log &" &

                        ${ssh} ${server1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_1_${rep}.log &" &
                        ${ssh} ${server2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_2_${rep}.log &" &
                        ${ssh} ${server3_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_3_${rep}.log &" &

                        sleep $(( ${runtime} + 5 ))

                        # Kill the middlewares to get data
                        ${ssh} ${mw1_pub} "sudo pkill -f middleware";
                        ${ssh} ${mw2_pub} "sudo pkill -f middleware";
                    done

                    echo "        All repetitions finished, gathering data ...";
                    ${scp} ${mw1_pub}:mw* ${cwd};
                    ${scp} ${mw1_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${mw1_pub} "rm mw* dstat*";

                    ${scp} ${mw2_pub}:mw* ${cwd};
                    ${scp} ${mw2_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${mw2_pub} "rm mw* dstat*";

                    ${scp} ${client1_pub}:client* ${cwd};
                    ${scp} ${client1_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${client1_pub} "rm client* dstat*";

                    ${scp} ${client2_pub}:client* ${cwd};
                    ${scp} ${client2_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${client2_pub} "rm client* dstat*";

                    ${scp} ${client3_pub}:client* ${cwd};
                    ${scp} ${client3_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${client3_pub} "rm client* dstat*";

                    ${scp} ${server1_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${server1_pub} "rm dstat*";

                    ${scp} ${server2_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${server2_pub} "rm dstat*";

                    ${scp} ${server3_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${server3_pub} "rm dstat*";

                    echo "        Finished gathering data.";
                done
            done
        done
    done

    echo "    Experiment finished, gathering middleware system data";
    ${scp} ${mw1_pub}:analysis.log ${log_dir}/analysis1.log;
    ${scp} ${mw1_pub}:system_report.log ${log_dir}/system_report1.log;
    ${ssh} ${mw1_pub} "rm ana* sys*";

    ${scp} ${mw2_pub}:analysis.log ${log_dir}/analysis2.log;
    ${scp} ${mw2_pub}:system_report.log ${log_dir}/system_report2.log;
    ${ssh} ${mw2_pub} "rm ana* sys*";

    echo "    Reordering data ...";
    mv /Users/jakob_beckmann/Desktop/logs/** ${final_dir};

    echo "throughput_writes finished";
}


function get_and_multigets {
    echo "Setting up get_and_multigets ...";
    mydate=$(date +%Y-%m-%d_%Hh%M);
    log_dir="/Users/jakob_beckmann/Desktop/logs/get_and_multigets(${mydate})"
    mkdir -p ${log_dir};

    pinger;

    echo "    Retreiving ping data.";
    ${scp} ${mw1_pub}:mw* ${log_dir};
    ${ssh} ${mw1_pub} "rm *.log";

    ${scp} ${mw2_pub}:mw* ${log_dir};
    ${ssh} ${mw2_pub} "rm *.log";

    runtime=90;
    memtier_options="--protocol=memcache_text --expiry-range=9999-10000 --key-maximum=10000 --test-time=${runtime} --data-size=1024";

    # Config:
    threads=1;
    operations=(0:9 0:6 0:3 0:1);
    is_sharded=(true false);
    worker_list=64;
    client_list=2;
    repetitions=(1 2 3);

    echo "Starting get_and_multigets ...";
    for op in "${operations[@]}"; do
        if [ "${op}" == "0:9" ]; then multiget=9; fi
        if [ "${op}" == "0:6" ]; then multiget=6; fi
        if [ "${op}" == "0:3" ]; then multiget=3; fi
        if [ "${op}" == "0:1" ]; then multiget=1; fi
        mkdir ${log_dir}/ratio_${op};
        for sharded in "${is_sharded[@]}"; do
            mkdir ${log_dir}/ratio_${op}/sharded_${sharded};
            for workers in "${worker_list[@]}"; do
                mkdir ${log_dir}/ratio_${op}/sharded_${sharded}/workers_${workers};
                for clients in "${client_list[@]}"; do
                    cwd=${log_dir}/ratio_${op}/sharded_${sharded}/workers_${workers}/clients_${clients};
                    mkdir ${cwd};
                    mkdir ${cwd}/dstat;
                    echo "    Launching with op: ${op}, sharded: ${sharded}, workers: ${workers}, clients: ${clients}";
                    for rep in "${repetitions[@]}"; do
                        echo "        Launching repetition ${rep} ...";

                        ${ssh} ${mw1_pub} "java -jar middleware-bjakob.jar -l ${mw1} -p ${mw1_port} -s ${sharded} -t ${workers} -m ${server1}:${server1_port} ${server2}:${server2_port} ${server3}:${server3_port} &> mw_1_${rep}.log &" &
                        ${ssh} ${mw2_pub} "java -jar middleware-bjakob.jar -l ${mw2} -p ${mw2_port} -s ${sharded} -t ${workers} -m ${server1}:${server1_port} ${server2}:${server2_port} ${server3}:${server3_port} &> mw_2_${rep}.log &" &
                        ${ssh} ${mw1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_mw_1_${rep}.log &" &
                        ${ssh} ${mw2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_mw_2_${rep}.log &" &

                        # Make sure the middleware runs ...
                        sleep 2;

                        ${ssh} ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} --multi-key-get=${multiget} &> client_1_1_${rep}.log" &
                        ${ssh} ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw2} --port=${mw2_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} --multi-key-get=${multiget} &> client_1_2_${rep}.log" &
                        ${ssh} ${client1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_1_${rep}.log &" &

                        ${ssh} ${client2_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} --multi-key-get=${multiget} &> client_2_1_${rep}.log" &
                        ${ssh} ${client2_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw2} --port=${mw2_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} --multi-key-get=${multiget} &> client_2_2_${rep}.log" &
                        ${ssh} ${client2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_2_${rep}.log &" &

                        ${ssh} ${client3_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} --multi-key-get=${multiget} &> client_3_1_${rep}.log" &
                        ${ssh} ${client3_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw2} --port=${mw2_port} --clients=${clients} --threads=${threads} --ratio=${op} ${memtier_options} --multi-key-get=${multiget} &> client_3_2_${rep}.log" &
                        ${ssh} ${client3_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_3_${rep}.log &" &

                        ${ssh} ${server1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_1_${rep}.log &" &
                        ${ssh} ${server2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_2_${rep}.log &" &
                        ${ssh} ${server3_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_3_${rep}.log &" &

                        sleep $(( ${runtime} + 5 ))

                        # Kill the middlewares to get data
                        ${ssh} ${mw1_pub} "sudo pkill -f middleware";
                        ${ssh} ${mw2_pub} "sudo pkill -f middleware";
                    done

                    echo "        All repetitions finished, gathering data ...";
                    ${scp} ${mw1_pub}:mw* ${cwd};
                    ${scp} ${mw1_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${mw1_pub} "rm mw* dstat*";

                    ${scp} ${mw2_pub}:mw* ${cwd};
                    ${scp} ${mw2_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${mw2_pub} "rm mw* dstat*";

                    ${scp} ${client1_pub}:client* ${cwd};
                    ${scp} ${client1_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${client1_pub} "rm client* dstat*";

                    ${scp} ${client2_pub}:client* ${cwd};
                    ${scp} ${client2_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${client2_pub} "rm client* dstat*";

                    ${scp} ${client3_pub}:client* ${cwd};
                    ${scp} ${client3_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${client3_pub} "rm client* dstat*";

                    ${scp} ${server1_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${server1_pub} "rm dstat*";

                    ${scp} ${server2_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${server2_pub} "rm dstat*";

                    ${scp} ${server3_pub}:dstat* ${cwd}/dstat;
                    ${ssh} ${server3_pub} "rm dstat*";

                    echo "        Finished gathering data.";
                done
            done
        done
    done

    echo "    Experiment finished, gathering middleware system data";
    ${scp} ${mw1_pub}:analysis.log ${log_dir}/analysis1.log;
    ${scp} ${mw1_pub}:system_report.log ${log_dir}/system_report1.log;
    ${ssh} ${mw1_pub} "rm ana* sys*";

    ${scp} ${mw2_pub}:analysis.log ${log_dir}/analysis2.log;
    ${scp} ${mw2_pub}:system_report.log ${log_dir}/system_report2.log;
    ${ssh} ${mw2_pub} "rm ana* sys*";

    echo "    Reordering data ...";
    mv /Users/jakob_beckmann/Desktop/logs/** ${final_dir};

    echo "get_and_multigets finished";
}


function 2kanalysis {
    echo "Setting up 2kanalysis ...";
    mydate=$(date +%Y-%m-%d_%Hh%M);
    log_dir="/Users/jakob_beckmann/Desktop/logs/2kanalysis(${mydate})"
    mkdir -p ${log_dir};

    pinger;

    echo "    Retreiving ping data.";
    ${scp} ${mw1_pub}:mw* ${log_dir};
    ${ssh} ${mw1_pub} "rm *.log";

    ${scp} ${mw2_pub}:mw* ${log_dir};
    ${ssh} ${mw2_pub} "rm *.log";

    runtime=90;
    memtier_options="--protocol=memcache_text --expiry-range=9999-10000 --key-maximum=10000 --test-time=${runtime} --data-size=1024";

    # Config:
    operations=(1:1 1:0 0:1);
    sharded="false";
    worker_list=(8 32);
    repetitions=(1 2 3);

    echo "Starting 2kanalysis ...";
    for op in "${operations[@]}"; do
        for workers in "${worker_list[@]}"; do
            # ==================================================================
            # One middleware two servers
            # ==================================================================
            echo "    Launching with op: ${op}, servers: 2, middlewares: 1, workers: ${workers}";
            cwd=${log_dir}/mws_1/servers_2/workers_${workers}/ratio_${op}
            mkdir -p ${cwd};
            mkdir ${cwd}/dstat;
            for rep in "${repetitions[@]}"; do
                echo "        Launching repetition ${rep} ...";

                ${ssh} ${mw1_pub} "java -jar middleware-bjakob.jar -l ${mw1} -p ${mw1_port} -s ${sharded} -t ${workers} -m ${server1}:${server1_port} ${server2}:${server2_port} &> mw_1_${rep}.log &" &
                ${ssh} ${mw1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_mw_1_${rep}.log &" &

                # Make sure the middleware runs ...
                sleep 2;

                ${ssh} ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=32 --threads=2 --ratio=${op} ${memtier_options} &> client_1_1_${rep}.log" &
                ${ssh} ${client1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_1_${rep}.log &" &

                ${ssh} ${client2_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=32 --threads=2 --ratio=${op} ${memtier_options} &> client_2_1_${rep}.log" &
                ${ssh} ${client2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_2_${rep}.log &" &

                ${ssh} ${client3_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=32 --threads=2 --ratio=${op} ${memtier_options} &> client_3_1_${rep}.log" &
                ${ssh} ${client3_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_3_${rep}.log &" &

                ${ssh} ${server1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_1_${rep}.log &" &
                ${ssh} ${server2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_2_${rep}.log &" &

                sleep $(( ${runtime} + 5 ))

                # Kill the middlewares to get data
                ${ssh} ${mw1_pub} "sudo pkill -f middleware";
            done
            echo "        All repetitions finished, gathering data ...";
            ${scp} ${mw1_pub}:mw* ${cwd};
            ${scp} ${mw1_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${mw1_pub} "rm mw* dstat*";

            ${scp} ${client1_pub}:client* ${cwd};
            ${scp} ${client1_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${client1_pub} "rm client* dstat*";

            ${scp} ${client2_pub}:client* ${cwd};
            ${scp} ${client2_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${client2_pub} "rm client* dstat*";

            ${scp} ${client3_pub}:client* ${cwd};
            ${scp} ${client3_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${client3_pub} "rm client* dstat*";

            ${scp} ${server1_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${server1_pub} "rm dstat*";

            ${scp} ${server2_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${server2_pub} "rm dstat*";

            echo "        Finished gathering data.";

            # ==================================================================
            # Two middleware two servers
            # ==================================================================
            echo "    Launching with op: ${op}, servers: 2, middlewares: 2, workers: ${workers}";
            cwd=${log_dir}/mws_2/servers_2/workers_${workers}/ratio_${op}
            mkdir -p ${cwd};
            mkdir ${cwd}/dstat;
            for rep in "${repetitions[@]}"; do
                echo "        Launching repetition ${rep} ...";

                ${ssh} ${mw1_pub} "java -jar middleware-bjakob.jar -l ${mw1} -p ${mw1_port} -s ${sharded} -t ${workers} -m ${server1}:${server1_port} ${server2}:${server2_port} &> mw_1_${rep}.log &" &
                ${ssh} ${mw2_pub} "java -jar middleware-bjakob.jar -l ${mw2} -p ${mw2_port} -s ${sharded} -t ${workers} -m ${server1}:${server1_port} ${server2}:${server2_port} &> mw_2_${rep}.log &" &
                ${ssh} ${mw1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_mw_1_${rep}.log &" &
                ${ssh} ${mw2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_mw_2_${rep}.log &" &

                # Make sure the middlewares run ...
                sleep 2;

                ${ssh} ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=32 --threads=1 --ratio=${op} ${memtier_options} &> client_1_1_${rep}.log" &
                ${ssh} ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw2} --port=${mw2_port} --clients=32 --threads=1 --ratio=${op} ${memtier_options} &> client_1_2_${rep}.log" &
                ${ssh} ${client1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_1_${rep}.log &" &

                ${ssh} ${client2_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=32 --threads=1 --ratio=${op} ${memtier_options} &> client_2_1_${rep}.log" &
                ${ssh} ${client2_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw2} --port=${mw2_port} --clients=32 --threads=1 --ratio=${op} ${memtier_options} &> client_2_2_${rep}.log" &
                ${ssh} ${client2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_2_${rep}.log &" &

                ${ssh} ${client3_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=32 --threads=1 --ratio=${op} ${memtier_options} &> client_3_1_${rep}.log" &
                ${ssh} ${client3_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw2} --port=${mw2_port} --clients=32 --threads=1 --ratio=${op} ${memtier_options} &> client_3_2_${rep}.log" &
                ${ssh} ${client3_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_3_${rep}.log &" &

                ${ssh} ${server1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_1_${rep}.log &" &
                ${ssh} ${server2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_2_${rep}.log &" &

                sleep $(( ${runtime} + 5 ))

                # Kill the middlewares to get data
                ${ssh} ${mw1_pub} "sudo pkill -f middleware";
                ${ssh} ${mw2_pub} "sudo pkill -f middleware";
            done
            echo "        All repetitions finished, gathering data ...";
            ${scp} ${mw1_pub}:mw* ${cwd};
            ${scp} ${mw1_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${mw1_pub} "rm mw* dstat*";

            ${scp} ${mw2_pub}:mw* ${cwd};
            ${scp} ${mw2_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${mw2_pub} "rm mw* dstat*";

            ${scp} ${client1_pub}:client* ${cwd};
            ${scp} ${client1_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${client1_pub} "rm client* dstat*";

            ${scp} ${client2_pub}:client* ${cwd};
            ${scp} ${client2_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${client2_pub} "rm client* dstat*";

            ${scp} ${client3_pub}:client* ${cwd};
            ${scp} ${client3_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${client3_pub} "rm client* dstat*";

            ${scp} ${server1_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${server1_pub} "rm dstat*";

            ${scp} ${server2_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${server2_pub} "rm dstat*";

            echo "        Finished gathering data.";

            # ==================================================================
            # One middleware three servers
            # ==================================================================
            echo "    Launching with op: ${op}, servers: 3, middlewares: 1, workers: ${workers}";
            cwd=${log_dir}/mws_1/servers_3/workers_${workers}/ratio_${op}
            mkdir -p ${cwd};
            mkdir ${cwd}/dstat;
            for rep in "${repetitions[@]}"; do
                echo "        Launching repetition ${rep} ...";

                ${ssh} ${mw1_pub} "java -jar middleware-bjakob.jar -l ${mw1} -p ${mw1_port} -s ${sharded} -t ${workers} -m ${server1}:${server1_port} ${server2}:${server2_port} ${server3}:${server3_port} &> mw_1_${rep}.log &" &
                ${ssh} ${mw1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_mw_1_${rep}.log &" &

                # Make sure the middleware runs ...
                sleep 2;

                ${ssh} ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=32 --threads=2 --ratio=${op} ${memtier_options} &> client_1_1_${rep}.log" &
                ${ssh} ${client1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_1_${rep}.log &" &

                ${ssh} ${client2_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=32 --threads=2 --ratio=${op} ${memtier_options} &> client_2_1_${rep}.log" &
                ${ssh} ${client2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_2_${rep}.log &" &

                ${ssh} ${client3_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=32 --threads=2 --ratio=${op} ${memtier_options} &> client_3_1_${rep}.log" &
                ${ssh} ${client3_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_3_${rep}.log &" &

                ${ssh} ${server1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_1_${rep}.log &" &
                ${ssh} ${server2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_2_${rep}.log &" &
                ${ssh} ${server3_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_3_${rep}.log &" &

                sleep $(( ${runtime} + 5 ))

                # Kill the middlewares to get data
                ${ssh} ${mw1_pub} "sudo pkill -f middleware";
            done
            echo "        All repetitions finished, gathering data ...";
            ${scp} ${mw1_pub}:mw* ${cwd};
            ${scp} ${mw1_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${mw1_pub} "rm mw* dstat*";

            ${scp} ${client1_pub}:client* ${cwd};
            ${scp} ${client1_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${client1_pub} "rm client* dstat*";

            ${scp} ${client2_pub}:client* ${cwd};
            ${scp} ${client2_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${client2_pub} "rm client* dstat*";

            ${scp} ${client3_pub}:client* ${cwd};
            ${scp} ${client3_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${client3_pub} "rm client* dstat*";

            ${scp} ${server1_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${server1_pub} "rm dstat*";

            ${scp} ${server2_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${server2_pub} "rm dstat*";

            ${scp} ${server3_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${server3_pub} "rm dstat*";

            echo "        Finished gathering data.";

            # ==================================================================
            # Two middleware three servers
            # ==================================================================
            echo "    Launching with op: ${op}, servers: 3, middlewares: 2, workers: ${workers}";
            cwd=${log_dir}/mws_2/servers_3/workers_${workers}/ratio_${op}
            mkdir -p ${cwd};
            mkdir ${cwd}/dstat;
            for rep in "${repetitions[@]}"; do
                echo "        Launching repetition ${rep} ...";

                ${ssh} ${mw1_pub} "java -jar middleware-bjakob.jar -l ${mw1} -p ${mw1_port} -s ${sharded} -t ${workers} -m ${server1}:${server1_port} ${server2}:${server2_port} ${server3}:${server3_port} &> mw_1_${rep}.log &" &
                ${ssh} ${mw2_pub} "java -jar middleware-bjakob.jar -l ${mw2} -p ${mw2_port} -s ${sharded} -t ${workers} -m ${server1}:${server1_port} ${server2}:${server2_port} ${server3}:${server3_port} &> mw_2_${rep}.log &" &
                ${ssh} ${mw1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_mw_1_${rep}.log &" &
                ${ssh} ${mw2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_mw_2_${rep}.log &" &

                # Make sure the middlewares run ...
                sleep 2;

                ${ssh} ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=32 --threads=1 --ratio=${op} ${memtier_options} &> client_1_1_${rep}.log" &
                ${ssh} ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw2} --port=${mw2_port} --clients=32 --threads=1 --ratio=${op} ${memtier_options} &> client_1_2_${rep}.log" &
                ${ssh} ${client1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_1_${rep}.log &" &

                ${ssh} ${client2_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=32 --threads=1 --ratio=${op} ${memtier_options} &> client_2_1_${rep}.log" &
                ${ssh} ${client2_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw2} --port=${mw2_port} --clients=32 --threads=1 --ratio=${op} ${memtier_options} &> client_2_2_${rep}.log" &
                ${ssh} ${client2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_2_${rep}.log &" &

                ${ssh} ${client3_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=32 --threads=1 --ratio=${op} ${memtier_options} &> client_3_1_${rep}.log" &
                ${ssh} ${client3_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw2} --port=${mw2_port} --clients=32 --threads=1 --ratio=${op} ${memtier_options} &> client_3_2_${rep}.log" &
                ${ssh} ${client3_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client_3_${rep}.log &" &

                ${ssh} ${server1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_1_${rep}.log &" &
                ${ssh} ${server2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_2_${rep}.log &" &
                ${ssh} ${server3_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server_3_${rep}.log &" &

                sleep $(( ${runtime} + 5 ))

                # Kill the middlewares to get data
                ${ssh} ${mw1_pub} "sudo pkill -f middleware";
                ${ssh} ${mw2_pub} "sudo pkill -f middleware";
            done
            echo "        All repetitions finished, gathering data ...";
            ${scp} ${mw1_pub}:mw* ${cwd};
            ${scp} ${mw1_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${mw1_pub} "rm mw* dstat*";

            ${scp} ${mw2_pub}:mw* ${cwd};
            ${scp} ${mw2_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${mw2_pub} "rm mw* dstat*";

            ${scp} ${client1_pub}:client* ${cwd};
            ${scp} ${client1_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${client1_pub} "rm client* dstat*";

            ${scp} ${client2_pub}:client* ${cwd};
            ${scp} ${client2_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${client2_pub} "rm client* dstat*";

            ${scp} ${client3_pub}:client* ${cwd};
            ${scp} ${client3_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${client3_pub} "rm client* dstat*";

            ${scp} ${server1_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${server1_pub} "rm dstat*";

            ${scp} ${server2_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${server2_pub} "rm dstat*";

            ${scp} ${server3_pub}:dstat* ${cwd}/dstat;
            ${ssh} ${server3_pub} "rm dstat*";

            echo "        Finished gathering data.";
        done
    done

    echo "    Experiment finished, gathering middleware system data";
    ${scp} ${mw1_pub}:analysis.log ${log_dir}/analysis1.log;
    ${scp} ${mw1_pub}:system_report.log ${log_dir}/system_report1.log;
    ${ssh} ${mw1_pub} "rm ana* sys*";

    ${scp} ${mw2_pub}:analysis.log ${log_dir}/analysis2.log;
    ${scp} ${mw2_pub}:system_report.log ${log_dir}/system_report2.log;
    ${ssh} ${mw2_pub} "rm ana* sys*";

    echo "    Reordering data ...";
    mv /Users/jakob_beckmann/Desktop/logs/** ${final_dir};

    echo "2kanalysis finished";
}

function test51 {
    
}

if [ "${1}" == "run" ]; then
    upload;
    populate;

    # List the experiments to run
    # benchmark_memcached;
    # benchmark_clients;
    # benchmark_1mw;
    # benchmark_2mw;
    # throughput_writes;
    # get_and_multigets;
    2kanalysis;

    cleanup;
fi
