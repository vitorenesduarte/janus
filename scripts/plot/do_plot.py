import argparse
import logging
import yaml
import copy
import subprocess
from string import Template

default_gnuplot_exe="/usr/local/bin/gnuplot5"
default_gnuplot_cmds="./cmds.gnuplot"

args = None

# filters to get the data
def bench(k,*args):
    return k[3] == args[0]

def txn(k, *args):
    return k[0] == args[0]
############################


def parse_args():
    global args
    parser = argparse.ArgumentParser(description='generate graphs.')
    parser.add_argument('-d', '--data', 
                        dest="data_files",
                        metavar='FILE', 
                        type=str, 
                        nargs='+',
                        help='the data files')
    parser.add_argument('-g', '--graph-config', 
                        metavar='FILE',
                        dest="graphs",
                        type=str, 
                        nargs='+',
                        help='the data files')
    parser.add_argument('-gexe', '--gnuplot-exe',
                        metavar='FILE',
                        dest="gnuplot_exe",
                        type=str, 
                        default=default_gnuplot_exe,
                        help='gnuplot executable')
    parser.add_argument('-gcmds', '--gnuplot-cmds',
                        metavar='FILE',
                        dest="gnuplot_cmds",
                        type=str,
                        default=default_gnuplot_cmds,
                        help='gnuplot commands')
    args = parser.parse_args()


def classify_data():
    global args
    output = {}
    for fn in args.data_files:
        lines = open(fn,'r').readlines()
        for l in lines:
            if l.strip()[0] != '#':
                key = tuple(l.split(',')[0:4]) # key is txn,cc,ab,bench
                key = tuple([k.strip() for k in key])
                if key not in output:
                    output[key] = fn
                else:
                    logging.warning("duplicate key found for {} - {}; previous {}".format(key, fn, output[key]))
                break
    return output



def get_data(data_classes, filters):
    output = []
    for key, fn in data_classes.iteritems():
        res = []
        for f in filters:
            #print(f[0], f[1:], key[3], f[0](key,*f[1:]))
            res.append( f[0](key,*f[1:]) )
        if all(res):
            output.append(fn)
    return output


def run_gnuplot(settings, data_files):
    global args
    
    if (data_files is None) or (len(data_files)==0):
        return

    cmd = [args.gnuplot_exe]
    for k,v in settings.iteritems():
        cmd.append('-e')
        cmd.append("{k}='{v}';".format(k=k, v=v))

    cmd.append('-e')
    cmd.append("input_files='{}'".format(' '.join(data_files)))

    cmd.append(args.gnuplot_cmds)
    logging.info("running: {}".format(' '.join(['"{}"'.format(c) for c in cmd])))
    res = subprocess.call(cmd)

    if res != 0:
        logging.error("Error {} running gnuplot!".format(res))


def generate_graph(config, txn_types, data_classes):
    if type(config['bench']) is not list:
        config['bench'] = [config['bench']]
    for txn_name in txn_types:
        for b in config['bench']:
            data_files = get_data(data_classes, [ [bench, b], [txn, txn_name] ])
            gnuplot_settings = copy.copy(config['graph'])
            gnuplot_settings['output_file'] = Template(gnuplot_settings['output_file']).substitute(txn=txn_name, bench=b)
            run_gnuplot(gnuplot_settings, data_files)


def main():
    logging.basicConfig(level=logging.DEBUG)
    global args
    parse_args()
    data_classes = classify_data()
    txn_types = set([k[0] for k in data_classes.keys()])
    for fn in args.graphs:
        with open(fn, 'r') as f:
            config = yaml.load(f)
            generate_graph(config, txn_types, data_classes)


if __name__ == "__main__":
    main()