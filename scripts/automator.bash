#!/bin/bash

# Do not forget to remove the hosts from the known_hosts file before launching
# the experiments
#
# The following is a failsafe if the .shh/config is not set up properly with:
#   Host *      # (or individual hostnames)
#       StrictHostKeyChecking no

alias ssh='ssh StrictHostKeyChecking=no'
alias scp='scp StrictHostKeyChecking=no'

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


function upload {
    # Compile the middleware
    rm ../middleware/dist/*;
    (cd ../middleware; ant);
    echo "Middleware compiled";

    # Copy middleware into home of cloud machines
    scp ../middleware/dist/middleware-bjakob.jar ${mw1_pub}:;
    scp ../middleware/dist/middleware-bjakob.jar ${mw2_pub}:;
    echo "Middleware copied to cloud hosts";
}

function populate {
    # Launch memcached instances on the server machines
    ssh ${mw2_pub} "sudo service memcached stop" &
    ssh ${server1_pub} "sudo service memcached stop; memcached -p ${server1_port} -t 1 &" &
    ssh ${server2_pub} "sudo service memcached stop; memcached -p ${server2_port} -t 1 &" &
    ssh ${server3_pub} "sudo service memcached stop; memcached -p ${server3_port} -t 1 &" &
    echo "Memcached instances launched on all servers";

    echo "Populating memcached instances ...";
    #parameters for memtier
    CT=1;
    VC=1;
    runtime=30;
    ratio=1:0;

    ssh ${client1_pub} "./memtier_benchmark-master/memtier_benchmark -s ${server1} -p ${server1_port} -c ${VC} -t ${CT} --ratio=${ratio} --test-time=${runtime} --protocol=memcache_text --expiry-range=9999-10000 --key-maximum=10000 --hide-histogram -d 1024 &> empty.log &" &
    ssh ${client2_pub} "./memtier_benchmark-master/memtier_benchmark -s ${server2} -p ${server2_port} -c ${VC} -t ${CT} --ratio=${ratio} --test-time=${runtime} --protocol=memcache_text --expiry-range=9999-10000 --key-maximum=10000 --hide-histogram -d 1024 &> empty.log &" &
    ssh ${client3_pub} "./memtier_benchmark-master/memtier_benchmark -s ${server3} -p ${server3_port} -c ${VC} -t ${CT} --ratio=${ratio} --test-time=${runtime} --protocol=memcache_text --expiry-range=9999-10000 --key-maximum=10000 --hide-histogram -d 1024 &> empty.log &" &

    sleeptime=$(( $runtime + 20 ))
    sleep ${sleeptime};

    ssh ${client1_pub} "rm *.log";
    ssh ${client2_pub} "rm *.log";
    ssh ${client3_pub} "rm *.log";

    echo "Memcached instances populated";
}

function cleanup {
    ssh ${mw2_pub} "sudo service memcached stop";
    ssh ${server1_pub} "sudo pkill -f memcached; sudo service memcached stop";
    ssh ${server2_pub} "sudo pkill -f memcached; sudo service memcached stop";
    ssh ${server3_pub} "sudo pkill -f memcached; sudo service memcached stop";
}

function pinger {
    echo "Launching ping script ...";

    ssh ${mw1_pub} "echo 'PING MIDDLEWARE 1' > mw1_ping.log";
    ssh ${mw2_pub} "echo 'PING MIDDLEWARE 2' > mw2_ping.log";

    echo "Pinging clients.";
    for machine in client{1..3}; do
        ssh ${mw1_pub} "echo 'mw1 > ${machine}' >> mw1_ping.log; ping -t 5 -i 0.2 ${!machine} >> mw1_ping.log &" &
        ssh ${mw2_pub} "echo 'mw2 > ${machine}' >> mw2_ping.log; ping -t 5 -i 0.2 ${!machine} >> mw2_ping.log &" &
        sleep 6;
        ssh ${mw1_pub} "sudo pkill -f ping";
        ssh ${mw2_pub} "sudo pkill -f ping";
    done

    echo "Pinging servers.";
    for machine in server{1..3}; do
        ssh ${mw1_pub} "echo 'mw1 > ${machine}' >> mw1_ping.log; ping -t 5 -i 0.2 ${!machine} >> mw1_ping.log &" &
        ssh ${mw2_pub} "echo 'mw2 > ${machine}' >> mw2_ping.log; ping -t 5 -i 0.2 ${!machine} >> mw2_ping.log &" &
        sleep 6;
        ssh ${mw1_pub} "sudo pkill -f ping";
        ssh ${mw2_pub} "sudo pkill -f ping";
    done

    echo "Ping finished, retrieving data ...";

    scp ${mw1_pub}:mw* ~/Desktop/logs/
    scp ${mw2_pub}:mw* ~/Desktop/logs/

    ssh ${mw1_pub} "rm *.log";
    ssh ${mw2_pub} "rm *.log";

    dir=/Users/jakob_beckmann/Documents/_uni/eth/_courses/2017/autumn/advanced_sys_lab/gitlab/asl-fall17-project/logs;
    mv ~/Desktop/logs/mw1_ping.log ${dir};
    mv ~/Desktop/logs/mw2_ping.log ${dir};

    echo "Ping finished.";
}

function tester {
    echo "Launching tester ...";
    runtime=120;
    memtier_options="--protocol=memcache_text --expiry-range=9999-10000 --key-maximum=10000 --hide-histogram --test-time=${runtime} --data-size=1024 --multi-key-get=10";

    ssh ${mw1_pub} "java -jar middleware-bjakob.jar -l ${mw1} -p ${mw1_port} -t 4 -s true -m ${server1}:${server1_port} ${server2}:${server2_port} &> test.log" &
    sleep 3;

    ssh ${client1_pub} "./memtier_benchmark-master/memtier_benchmark -s ${mw1} -p ${mw1_port} -c ${vc} --threads=2 --clients=3 --ratio=1:10 ${memtier_options} &> memtier.log" &

    echo "Test experiment launched. Please be patient for ${runtime} seconds ...";
    sleep $(( ${runtime} + 5 ));

    ssh ${mw1_pub} "sudo pkill -f middleware"

    echo "Experiment finised, recovering log files ...";
    scp ${client1_pub}:memtier.log ~/Desktop/logs;
    scp ${mw1_pub}:*.log ~/Desktop/logs;
    ssh ${client1_pub} "rm memtier.log";
    ssh ${mw1_pub} "rm analysis.log system_report.log test.log";

    date=$(date +%Y-%m-%d_%Hh%M);
    dir=/Users/jakob_beckmann/Documents/_uni/eth/_courses/2017/autumn/advanced_sys_lab/gitlab/asl-fall17-project/logs;
    mv ~/Desktop/logs/** ${dir}/${date};

    echo "Test finished";
}


function benchmark_memcached {
    echo "Setting up benchmark_memcached ...";
    mkdir ~/Desktop/logs/benchmark_memcached;
    logs_dir=~/Desktop/logs/benchmark_memcached;

    runtime=90;
    memtier_options="--protocol=memcache_text --expiry-range=9999-10000 --key-maximum=10000 --hide-histogram --test-time=${runtime} --data-size=1024";

    repetitions=(1 2 3);

    threads=2;
    clients=(1 2 4 8 16 24 32);

    operations=(read write);

    echo "Starting benchmark_memcached ...";
    for operation in "${operations[@]}"; do
        if [ "${operation}" == "read" ]; then ratio=0:1; fi
        if [ "${operation}" == "write" ]; then ratio=1:0; fi

        for nclient in "${clients[@]}"; do
            config="${threads}threads_${nclient}clients_${operation}";
            mkdir ${logs_dir}/${config}
            client_logs=${logs_dir}/${config}/clients; mkdir ${client_logs};
            server_logs=${logs_dir}/${config}/servers; mkdir ${server_logs};

            echo "Preparing to run with ${threads} threads on ${nclient} clients and ratio ${ratio}";

            for rep in "${repetitions[@]}"; do
                ssh ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${server1} --port=${server1_port} --clients=${nclient} --threads=${threads} --ratio=${ratio} ${memtier_options} &> client1_${rep}.log &" &
                ssh ${client1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client1_${rep}.log &" &

                ssh ${client2_pub} "./memtier_benchmark-master/memtier_benchmark --server=${server1} --port=${server1_port} --clients=${nclient} --threads=${threads} --ratio=${ratio} ${memtier_options} &> client2_${rep}.log &" &
                ssh ${client2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client2_${rep}.log &" &

                ssh ${client3_pub} "./memtier_benchmark-master/memtier_benchmark --server=${server1} --port=${server1_port} --clients=${nclient} --threads=${threads} --ratio=${ratio} ${memtier_options} &> client3_${rep}.log &" &
                ssh ${client3_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client3_${rep}.log &" &

                ssh ${server1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server1_${rep}.log &" &

                sleep $(( ${runtime} + 5 ))
                echo "Repetition ${rep} finished";
            done

            echo "All repetitions finished, gathering data ...";
            scp ${client1_pub}:client* ${client_logs};
            scp ${client1_pub}:dstat* ${client_logs};
            ssh ${client1_pub} "rm client* dstat*";

            scp ${client2_pub}:client* ${client_logs};
            scp ${client2_pub}:dstat* ${client_logs};
            ssh ${client2_pub} "rm client* dstat*";

            scp ${client3_pub}:client* ${client_logs};
            scp ${client3_pub}:dstat* ${client_logs};
            ssh ${client3_pub} "rm client* dstat*";

            scp ${server1_pub}:dstat* ${server_logs};
            ssh ${server1_pub} "rm dstat*";
        done
    done

    echo "Experiment finished, reordering data ...";

    date=$(date +%Y-%m-%d_%Hh%M);
    dir=/Users/jakob_beckmann/Documents/_uni/eth/_courses/2017/autumn/advanced_sys_lab/gitlab/asl-fall17-project/logs;
    mv ~/Desktop/logs/** "${dir}/${date}(bench_memcached)";

    echo "benchmark_memcached finished";
}

function benchmark_clients {
    echo "Setting up benchmark_clients ...";
    mkdir ~/Desktop/logs/benchmark_clients;
    logs_dir=~/Desktop/logs/benchmark_clients;

    runtime=90;
    memtier_options="--protocol=memcache_text --expiry-range=9999-10000 --key-maximum=10000 --hide-histogram --test-time=${runtime} --data-size=1024";

    repetitions=(1 2 3);

    threads=1;
    clients=(1 2 4 8 16 24 32);

    operations=(read write);

    echo "Starting benchmark_clients ...";
    for operation in "${operations[@]}"; do
        if [ "${operation}" == "read" ]; then ratio=0:1; fi
        if [ "${operation}" == "write" ]; then ratio=1:0; fi

        for nclient in "${clients[@]}"; do
            config="${threads}threads_${nclient}clients_${operation}";
            mkdir ${logs_dir}/${config}
            client_logs=${logs_dir}/${config}/clients; mkdir ${client_logs};
            server_logs=${logs_dir}/${config}/servers; mkdir ${server_logs};

            echo "Preparing to run with ${threads} threads on ${nclient} clients and ratio ${ratio}";

            for rep in "${repetitions[@]}"; do
                ssh ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${server1} --port=${server1_port} --clients=${nclient} --threads=${threads} --ratio=${ratio} ${memtier_options} &> client1-1_${rep}.log" &
                ssh ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${server2} --port=${server2_port} --clients=${nclient} --threads=${threads} --ratio=${ratio} ${memtier_options} &> client1-2_${rep}.log" &

                ssh ${client1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client1_${rep}.log" &

                ssh ${server1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server1_${rep}.log" &
                ssh ${server2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server2_${rep}.log" &

                sleep $(( ${runtime} + 5 ))

                echo "Repetition ${rep} finished";
            done

            echo "All repetitions finished, gathering data ...";
            scp ${client1_pub}:client* ${client_logs};
            scp ${client1_pub}:dstat* ${client_logs};
            ssh ${client1_pub} "rm client* dstat*";

            scp ${server1_pub}:dstat* ${server_logs};
            ssh ${server1_pub} "rm dstat*";

            scp ${server2_pub}:dstat* ${server_logs};
            ssh ${server2_pub} "rm dstat*";
        done
    done

    echo "Experiment finished, reordering data ...";

    date=$(date +%Y-%m-%d_%Hh%M);
    dir=/Users/jakob_beckmann/Documents/_uni/eth/_courses/2017/autumn/advanced_sys_lab/gitlab/asl-fall17-project/logs;
    mv ~/Desktop/logs/** "${dir}/${date}(bench_clients)";

    echo "benchmark_clients finished";
}

function benchmark_1mw {
    echo "Setting up benchmark_1mw ...";
    mkdir ~/Desktop/logs/benchmark_1mw;
    logs_dir=~/Desktop/logs/benchmark_1mw;

    # Make sure the middleware is not already running ...
    ssh ${mw1_pub} "sudo pkill -f middleware";

    runtime=90;
    memtier_options="--protocol=memcache_text --expiry-range=9999-10000 --key-maximum=10000 --hide-histogram --test-time=${runtime} --data-size=1024";

    repetitions=(1 2 3);

    threads=2;
    clients=(2 4 8 14 20 26 32);
    workers=(8 16 32 64)

    operations=(read write);

    echo "Starting benchmark_1mw ...";
    for operation in "${operations[@]}"; do
        if [ "${operation}" == "read" ]; then ratio=0:1; fi
        if [ "${operation}" == "write" ]; then ratio=1:0; fi

        for nworker in "${workers[@]}"; do
            echo
            echo "Preparing to run with ${nworker} workers ...";

            worker_dir="${nworker}_workers";
            mkdir ${logs_dir}/${worker_dir};

            for nclient in "${clients[@]}"; do
                config="${threads}threads_${nclient}clients_${operation}";
                mkdir ${logs_dir}/${worker_dir}/${config}
                mw_logs=${logs_dir}/${worker_dir}/${config}/mw; mkdir ${mw_logs};
                client_logs=${logs_dir}/${worker_dir}/${config}/clients; mkdir ${client_logs};
                server_logs=${logs_dir}/${worker_dir}/${config}/servers; mkdir ${server_logs};

                echo "Preparing to run with ${threads} threads on ${nclient} clients and ratio ${ratio} (${nworker} workers)";

                for rep in "${repetitions[@]}"; do
                    ssh ${mw1_pub} "java -jar middleware-bjakob.jar -l ${mw1} -p ${mw1_port} -s false -t ${nworker} -m ${server1}:${server1_port} &> mw1_${rep}.log &" &
                    sleep 2;            # Make sure the middleware runs ...
                    ssh ${mw1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_mw1_${rep}.log &" &

                    ssh ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=${nclient} --threads=${threads} --ratio=${ratio} ${memtier_options} &> client1_${rep}.log" &
                    ssh ${client1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client1_${rep}.log &" &

                    ssh ${server1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server1_${rep}.log &" &

                    sleep $(( ${runtime} + 5 ))

                    # Kill the middleware to get data
                    ssh ${mw1_pub} "sudo pkill -f middleware";

                    echo "Repetition ${rep} finished";
                done

                echo "All repetitions finished, gathering data ...";
                scp ${mw1_pub}:mw* ${mw_logs};
                scp ${mw1_pub}:dstat* ${mw_logs};
                ssh ${mw1_pub} "rm mw* dstat*";

                scp ${client1_pub}:client* ${client_logs};
                scp ${client1_pub}:dstat* ${client_logs};
                ssh ${client1_pub} "rm client* dstat*";

                scp ${server1_pub}:dstat* ${server_logs};
                ssh ${server1_pub} "rm dstat*";
            done
        done
    done

    echo "Experiment finished, retrieving middleware system data ...";
    scp ${mw1_pub}:analysis.log ${logs_dir};
    scp ${mw1_pub}:system_report.log ${logs_dir};
    ssh ${mw1_pub} "rm *.log ana* sys*";

    echo "Data retrieved, reordering ...";
    date=$(date +%Y-%m-%d_%Hh%M);
    dir=/Users/jakob_beckmann/Documents/_uni/eth/_courses/2017/autumn/advanced_sys_lab/gitlab/asl-fall17-project/logs;
    mv ~/Desktop/logs/** "${dir}/${date}(bench_1mw)";

    echo "benchmark_1mw finished";
}

function benchmark_2mw {
    echo "Setting up benchmark_2mw ...";
    mkdir ~/Desktop/logs/benchmark_2mw;
    logs_dir=~/Desktop/logs/benchmark_2mw;

    # Make sure the middlewares are not already running.
    ssh ${mw1_pub} "sudo pkill -f middleware";
    ssh ${mw2_pub} "sudo pkill -f middleware";

    runtime=90;
    memtier_options="--protocol=memcache_text --expiry-range=9999-10000 --key-maximum=10000 --hide-histogram --test-time=${runtime} --data-size=1024";

    repetitions=(1 2 3);

    threads=1;
    clients=(2 4 8 14 20 26 32);
    workers=(8 16 32 64)

    operations=(read write);

    echo "Starting benchmark_2mw ...";
    for operation in "${operations[@]}"; do
        if [ "${operation}" == "read" ]; then ratio=0:1; fi
        if [ "${operation}" == "write" ]; then ratio=1:0; fi

        for nworker in "${workers[@]}"; do
            echo
            echo "Preparing to run with ${nworker} workers ...";

            worker_dir="${nworker}_workers";
            mkdir ${logs_dir}/${worker_dir};

            for nclient in "${clients[@]}"; do
                config="${threads}threads_${nclient}clients_${operation}";
                mkdir ${logs_dir}/${worker_dir}/${config}
                mw_logs=${logs_dir}/${worker_dir}/${config}/mw; mkdir ${mw_logs};
                client_logs=${logs_dir}/${worker_dir}/${config}/clients; mkdir ${client_logs};
                server_logs=${logs_dir}/${worker_dir}/${config}/servers; mkdir ${server_logs};

                echo "Preparing to run with ${threads} threads on ${nclient} clients and ratio ${ratio} (${nworker} workers)";

                for rep in "${repetitions[@]}"; do
                    ssh ${mw1_pub} "java -jar middleware-bjakob.jar -l ${mw1} -p ${mw1_port} -s false -t ${nworker} -m ${server1}:${server1_port} &> mw1_${rep}.log &" &
                    ssh ${mw2_pub} "java -jar middleware-bjakob.jar -l ${mw2} -p ${mw2_port} -s false -t ${nworker} -m ${server1}:${server1_port} &> mw2_${rep}.log &" &
                    sleep 2;            # Make sure the middleware runs ...
                    ssh ${mw1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_mw1_${rep}.log &" &
                    ssh ${mw2_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_mw2_${rep}.log &" &

                    ssh ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw1} --port=${mw1_port} --clients=${nclient} --threads=${threads} --ratio=${ratio} ${memtier_options} &> client1-1_${rep}.log" &
                    ssh ${client1_pub} "./memtier_benchmark-master/memtier_benchmark --server=${mw2} --port=${mw2_port} --clients=${nclient} --threads=${threads} --ratio=${ratio} ${memtier_options} &> client1-2_${rep}.log" &
                    ssh ${client1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_client1_${rep}.log &" &

                    ssh ${server1_pub} "dstat -c -n -d -T 1 ${runtime} > dstat_server1_${rep}.log &" &

                    sleep $(( ${runtime} + 5 ))

                    # Kill the middlewares to get data
                    ssh ${mw1_pub} "sudo pkill -f middleware";
                    ssh ${mw2_pub} "sudo pkill -f middleware";

                    echo "Repetition ${rep} finished";
                done

                echo "All repetitions finished, gathering data ...";
                scp ${mw1_pub}:mw* ${mw_logs};
                scp ${mw1_pub}:dstat* ${mw_logs};
                ssh ${mw1_pub} "rm mw* dstat*";

                scp ${mw2_pub}:mw* ${mw_logs};
                scp ${mw2_pub}:dstat* ${mw_logs};
                ssh ${mw2_pub} "rm mw* dstat*";

                scp ${client1_pub}:client* ${client_logs};
                scp ${client1_pub}:dstat* ${client_logs};
                ssh ${client1_pub} "rm client* dstat*";

                scp ${server1_pub}:dstat* ${server_logs};
                ssh ${server1_pub} "rm dstat*";
            done
        done
    done

    echo "Experiment finished, retrieving middleware system data ...";
    scp ${mw1_pub}:analysis.log ${logs_dir}/analysis1.log;
    scp ${mw1_pub}:system_report.log ${logs_dir}/system_report1.log;
    ssh ${mw1_pub} "rm *.log ana* sys*";

    scp ${mw2_pub}:analysis.log ${logs_dir}/analysis2.log;
    scp ${mw2_pub}:system_report.log ${logs_dir}/system_report2.log;
    ssh ${mw2_pub} "rm *.log ana* sys*";

    echo "Data retrieved, reordering ...";
    date=$(date +%Y-%m-%d_%Hh%M);
    dir=/Users/jakob_beckmann/Documents/_uni/eth/_courses/2017/autumn/advanced_sys_lab/gitlab/asl-fall17-project/logs;
    mv ~/Desktop/logs/** "${dir}/${date}(bench_2mw)";

    echo "benchmark_2mw finished";
}


if [ "${1}" == "run" ]; then
    upload;
    pinger;
    populate;
    populate;

    # List the experiments to run
    # benchmark_memcached;
    # benchmark_clients;
    # benchmark_1mw;
    # benchmark_2mw;

    cleanup;
fi
