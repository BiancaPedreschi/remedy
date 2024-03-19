import os
import os.path as op
import tarfile
import zipfile
import gdown
from config import read_config, write_config


def extract(tar_url, extract_path='.'):
    tar = tarfile.open(tar_url, 'r')
    for item in tar:
        tar.extract(item, extract_path)
        if item.name.find(".tgz") != -1 or item.name.find(".tar") != -1:
            extract(item.name, "./" + item.name[:item.name.rfind('/')])
            
            
def fetch_data():
    config = read_config()
    parent_dir = config['paths']['parent']
    url = ('https://drive.google.com/file/d/12tFrfTJTmUxXCHIEhgfRjXLcad9pylVt/view?usp=sharing')

    print('Creating data path...')
    output_dir = op.join(parent_dir, 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    print('Downloading data...')
    output = op.join(output_dir, 'remedy_data.zip')
    gdown.download(url, output, quiet=False, fuzzy=True)
    
    print('Extracting data...')
    with zipfile.ZipFile(output, 'r') as zip_fname:
        zip_fname.extractall(output_dir)
    # extract(output)
    os.remove(output)
    
    config['paths']['data'] = op.join(output_dir, 'remedy_data')
    write_config(config)
    
    return


if __name__ == '__main__':
    fetch_data()
