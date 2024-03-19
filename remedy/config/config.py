import os
import os.path as op
import yaml

def generate_config():
    cwd = os.getcwd()
    prj = op.join(cwd, 'remedy')
    conf = op.join(prj, 'config')
    conf_fname = op.join(conf, 'config.yml')
    
    paths = {'paths': {'parent': cwd,
                       'project': prj,
                       'config': conf}
        }
    
    with open(conf_fname, 'w') as cf:
        yaml.dump(paths, cf)
    
    return

def read_config():
    cwd = os.getcwd()
    prj = op.join(cwd, 'remedy')
    conf = op.join(prj, 'config')
    conf_fname = op.join(conf, 'config.yml')
    
    with open(conf_fname, 'r') as cf:
        configs =  yaml.load(cf, Loader=yaml.FullLoader)
        
    return configs


def add_config(position, arg):
    cwd = os.getcwd()
    prj = op.join(cwd, 'remedy')
    conf = op.join(prj, 'config')
    conf_fname = op.join(conf, 'config.yml')
    
    pos = position.split('/')
    
    with open(conf_fname, 'r') as cf:
        configs =  yaml.load(cf, Loader=yaml.FullLoader)
    
    configs[position] = arg
    
    with open(conf_fname, 'w') as cf:
        yaml.dump(configs, cf)
    
    return


def write_config(config):
    conf_fname = op.join(config['paths']['config'], 'config.yml')
    
    with open(conf_fname, 'w') as cf:
        yaml.dump(config, cf)
    
    return
    
    
if __name__ == '__main__':
    generate_config()
    print(read_config())