#!/usr/bin/env python3

def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)


# Config
worker_list = [8, 16, 32, 64]
arrival_rate_list = [3714.358333, 5998.8125, 6218.020833, 6207.666667, 6212.945833,
                     6198.5375, 6217.820833, 6202.591667, 6155.1375, 3621.566667,
                     6814.504167, 9249.220833, 10412.30417, 10259.30417, 10320.58333,
                     10164.5, 10287.29167, 10623.75833, 3725.716667, 7082.291667,
                     10030.78333, 12332.61667, 12871.17917, 12993.27083, 13032.92917,
                     13175.4, 12834.41667, 3712.545833, 7000.029167, 9851.5, 12849.02083,
                     13445.125, 13990.43333, 14844.51667, 15243.5125, 15421.1375]
service_time_list = [2.551340292, 2.992740208, 4.819790083, 8.210024958]


client_list = [2, 4, 8, 16, 24, 32, 40, 48, 56]




for idx in range(0, len(arrival_rate_list)):
    service_time = service_time_list[idx//9] / 1000
    workers = worker_list[idx//9] * 2
    service_rate = 1 / service_time
    rho = arrival_rate_list[idx] / (service_rate * workers)
    p0 = pow(
        1 + \
        pow(workers * rho, workers) / (factorial(workers) * (1 - rho)) + \
        sum([pow(workers * rho, n) / factorial(n) for n in range(1, workers)]),
        -1
    )
    varrho = pow(workers * rho, workers) / (factorial(workers) * (1 - rho)) * p0
    En_q = rho * varrho / (1 - rho)
    Varn_q = rho * varrho * (1 + rho - varrho * rho) / pow(1 - rho, 2)
    Er = (1 / service_rate) * (1 + varrho / (workers * (1 - rho)))

    # Little's law
    Ew_q = En_q / arrival_rate_list[idx]

    if idx % 9 == 0:
        print("\n\nWORKERS {}".format(worker_list[idx//9]))

    print(r"\hline {} & {:10.7} & {:10.7} & {:10.5} & {:10.5} & {:10.5} & {:10.5} & {:10.5} \\".format(
        client_list[idx%9],
        arrival_rate_list[idx],
        service_rate,
        service_time * 1000,
        rho * 100,
        En_q,
        Ew_q * 1000,
        Er * 1000
    ))
