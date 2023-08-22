##############################################################################################################
# ERT4IO is a python script to plot the I/O Roofline graph for an application.
# It is based on the parsed text file from darshan outputs.
# Through the integration of pydarshan .darshan files can be used directly.
# Currently, it supports only POSIX and MPIIO APIs and the metrics are read from the darshan output files.
#   Usage: python3 ERT4IO.py -p <darshan_outputs_dir> -d <is_darshan_output>
#   Example: python3 ERT4IO.py or python3 ERT4IO.py -p demo_darshan_outputs -d 1
#   Output: roofline.png
#   Note: The darshan output files should be in the following format:
#         <"system_name"_"app_name"_n"num_process">.<api>
#         For example: fuchs_ior_n1.posix
#         Peak outputs should be renamed to the following format:
#         peak_<"system_name"_"app_name"_n"num_process">.<api>
#         For example: peak_fuchs_ior_n900.posix
#         The darshan output files should be in the same directory.
################################################################################################################
import argparse
import numpy as np
import matplotlib.pyplot as plt
import os


# naive_darshan_reader function is used to get the metrics from the specified output
# parameters: f - darshan output file
# return: metrics - dictionary of metrics
def naive_darshan_reader(f):
    metrics = {}
    runtime = 0
    md_file = open(f, 'r')
    lines = md_file.read().splitlines()
    if f.endswith('posix'):
        metrics['api'] = "POSIX"
        for idx, line in enumerate(lines):
            if line.startswith('# nprocs:'):
                metrics['nprocs'] = float(line.split(':')[1].lstrip())
            if line.startswith('# run time:'):
                runtime = float(line.split(':')[1].lstrip())
            if line.startswith('total_POSIX_OPENS:'):
                metrics['op'] = 0
                for i in range(13):
                    metrics['op'] += float(lines[idx + i].split(':')[1].lstrip())
                metrics['ops'] = float(metrics['op'] / runtime)
            if line.startswith('total_POSIX_BYTES_READ:'):
                metrics['size'] = 0.0
                metrics['size'] = float(line.split(':')[1].lstrip()) + float(
                    lines[idx + 1].split(':')[1].lstrip())
                metrics['bw'] = float(metrics['size'] / runtime)
        metrics['op_ins'] = metrics['op'] / metrics['size']
    elif f.endswith('mpiio'):
        metrics['api'] = "MPIIO"
        for idx, line in enumerate(lines):
            if line.startswith('# nprocs:'):
                metrics['nprocs'] = float(line.split(':')[1].lstrip())
            if line.startswith('# run time:'):
                runtime = float(line.split(':')[1].lstrip())
            if line.startswith('total_MPIIO_INDEP_OPENS:'):
                metrics['op'] = 0
                for i in range(13):
                    metrics['op'] += float(lines[idx + i].split(':')[1].lstrip())
                metrics['ops'] = float(metrics['op'] / runtime)
            if line.startswith('total_MPIIO_BYTES_READ:'):
                metrics['size'] = 0.0
                metrics['size'] = float(line.split(':')[1].lstrip()) + float(
                    lines[idx + 1].split(':')[1].lstrip())
                metrics['bw'] = float(metrics['size'] / runtime)
        metrics['op_ins'] = metrics['op'] / metrics['size']
    return metrics


# get_metrics function is used to get the metrics from the specified output files.
# currently it supports parsed darshan outputs only.
# parameters:
# app_path: path of the output files
# is_darshan_output: boolean value to check if the output files are darshan output
# returns:
# apps: list of application metrics
# app_names: list of application names
# peaks: list of peak metrics

def get_metrics(app_path='demo_darshan_output', is_darshan_output=True):
    apps = []
    app_names = []
    peaks = []
    directory = os.fsencode(app_path)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith('.posix') or filename.endswith('.mpiio'):
            path = app_path + "/" + filename
            if is_darshan_output:
                app = naive_darshan_reader(path)
                if filename.startswith('peak_'):
                    peaks.append({"peak_ops": app['ops'], "peak_bw": app['bw'], "peak_sys": filename.split("_")[1],
                                  "peak_api": app['api'], "peak_nprocs": app['nprocs'], "peak_ins": app['op_ins'],
                                  "peak_rp": 'RP'})
                else:
                    apps.append(app)
                    first = filename.split('.')[0]
                    app_name = first.split('_')[1] + "-" + first.split('_')[2] + "(" + first.split('_')[0] + ")"
                    app_names.append(app_name)
    return apps, app_names, peaks


# plot_rooflines function is used to plot the roofline graph
# parameters:
# peaks: list of peak metrics
# apps: list of application metrics
# app_names: list of application names
# view_min: minimum value of x-axis
# view_max: maximum value of x-axis
def plot_rooflines(peaks, apps, app_names, view_min=0, view_max=1):
    for peak in peaks:
        x = []
        y = []
        for i in np.linspace(view_min, view_max, num=10000000):
            if peak['peak_ops'] > (i * peak['peak_bw']):
                x.append(i)
                y.append(i * peak['peak_bw'])
            else:
                x.append(i)
                y.append(peak['peak_ops'])
        plt.plot(x, y, label="System: %s\n"
                             "Interface: %s\n"
                             "NProcs: %s \n"
                             "IOPS: %s \n"
                             "BW: %s MiB/s" % (peak['peak_sys'], peak['peak_api'].lower(), peak['peak_nprocs'],
                                               format(peak['peak_ops'], '.2f'),
                                               format(peak['peak_bw'] / (1024 * 1024), '.2f')))
        x_peak = [peak['peak_ins']]
        y_peak = [peak['peak_ops']]
        plt.plot(x_peak, y_peak, marker="x", markersize=5, color='red')
        plt.text(peak['peak_ins'], peak['peak_ops'], "%s" % peak['peak_rp'])

    for idx, app in enumerate(apps):
        x_app = [app['op_ins']]
        y_app = [app['ops']]
        plt.plot(x_app, y_app, marker="o", markersize=5, color=np.random.rand(3, ))
        plt.text(app['op_ins'], app['ops'], "%s" % app_names[idx])
    plt.title("Empirical Roofline Graph")
    plt.legend(loc='lower right')
    plt.ylabel("Operational Performance [IOP/s]")
    plt.xlabel("I/O Operational Intensity [IOP/Byte]")
    plt.xscale("log")
    plt.yscale("log")
    plt.grid(True, which="both", ls="-")
    plt.show()


if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser(description='Plot Roofline Graph')
    parser.add_argument('-p', '--path', help='path of the darshan output files', required=False)
    parser.add_argument('-d', '--darshan', help='boolean value to check if the output files are darshan output',
                        required=False)
    args = vars(parser.parse_args())
    if args['path'] is not None:
        app_path = args['path']
    else:
        app_path = 'demo_darshan_outputs'
    if args['darshan'] is not None:
        is_darshan_output = args['darshan']
    else:
        is_darshan_output = True
    apps, app_names, peaks = get_metrics(app_path, is_darshan_output)
    plot_rooflines(peaks, apps, app_names, 0, 1)

