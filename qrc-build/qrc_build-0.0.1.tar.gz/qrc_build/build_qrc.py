"""
convert folder to qrc and python module

qrc struct
<file alias="logo.png">logo.png</file>

pyqt
import icon
QPixmap(":icon/test.png")
"""

import os
import subprocess
import py_compile


def build_qrc(folder_filename, output_filename='icon.qrc'):
    qrc_data = '''
<!DOCTYPE RCC>
<RCC version="1.0">
<qresource>
{}
</qresource>
</RCC>
    '''
    file_data = []

    for r, ds, fs in os.walk(folder_filename):
        for f in fs:
            path = '\\'.join([r.replace(folder_filename, ''), f])[1:]

            asset_path = 'icons\\' + path
            file_data.append('<file alias="{}">{}</file>'.format(asset_path, asset_path))

    qrc_fina_data = qrc_data.format('\n'.join(file_data))

    with open(output_filename, 'w') as f:
        f.write(qrc_fina_data)

    return output_filename


def build_module_for_qt5(folder_filename, qrc_filename, py_output_filename, pyc_output_filename):
    rcc_tool_filename = os.path.abspath('pyrcc5.exe')

    if not os.path.exists(rcc_tool_filename):
        print('pyrcc5.exe not exists!')
        raise IOError

    cmd = [rcc_tool_filename, '-compress', '1', '-threshold', '1', '-o', py_output_filename, qrc_filename]

    p = subprocess.Popen(cmd, cwd=os.path.dirname(folder_filename), stdout=subprocess.DEVNULL)
    p.communicate()

    # remove qrc
    os.remove(qrc_filename)

    # build pyc
    py_compile.compile(py_output_filename, pyc_output_filename)
    os.remove(py_output_filename)

    return pyc_output_filename


def asset_folder_to_pyc(main_root, asset_folder):
    folder_filename = os.path.join(main_root, asset_folder)
    qrc_filename = os.path.join(main_root, asset_folder + '.qrc')
    py_filename = os.path.join(main_root, asset_folder + '.py')
    pyc_filename = os.path.join(main_root, asset_folder + '.pyc')

    build_qrc(folder_filename, qrc_filename)

    pyc_filename = build_module_for_qt5(folder_filename, qrc_filename, py_filename, pyc_filename)

    return pyc_filename


if __name__ == '__main__':
    print(asset_folder_to_pyc(r'E:\XDL_MANAGER3', 'icons'))
