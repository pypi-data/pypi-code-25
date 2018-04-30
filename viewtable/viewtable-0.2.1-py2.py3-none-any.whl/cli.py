import json
import pathlib

import pandas as pd
import click

try:
    from viewtable import h5pytools
except:
    import h5pytools


def df_from_json_files(files):
    print(files)
    data = []
    for fname in files:
        with open(fname, 'r') as fp:
            data.append(json.load(fp))
    
    return pd.DataFrame(data)


def df_from_hdf_files(files):
    return h5pytools.DataFrame_from_hdf5(files)



@click.command()
@click.argument('Files', type=click.File('r'), nargs=-1, required=True)
@click.option('--columns', type=str, help="String containing whitespace-separated column names to show.  example: 'col1 col2'")
@click.option('--show-columns', is_flag=True, help="Print only the names of columns")
@click.option('--width', default=80, type=int, help="Width of columns to print")
def main(files, columns, show_columns, width):
    fnames = [f.name for f in files]
    extensions = [pathlib.Path(name).suffix for name in fnames]
    unique_extentions = set(extensions)
    assert len(unique_extentions) == 1, "Files must all have same extension."
    ext = next(iter(unique_extentions))
    if ext == '.json':
        df = df_from_json_files(fnames)
    elif ext == '.hdf5':
        df = df_from_hdf_files(fnames)
    else:
        raise NotImplementedError('File type not supported: {}'.format(ext))
	
    if columns is not None:
        cols = columns.split()
        df = df[cols]

    pd.set_option('display.width', width) 

    if show_columns:
        click.echo('\n'.join(sorted(df.columns, key=lambda x: x.lower())))
    else:
        click.echo(df)

    

if __name__ == '__main__':
    main()
