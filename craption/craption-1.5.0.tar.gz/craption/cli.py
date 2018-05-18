#coding: utf-8

from craption import settings, upload, utils
import opster
import os
import shutil

@opster.command()
def main(clear_conf=('c', False, 'Rewrite example config'),
         dropbox_login=('d', False, 'Login to dropbox')):
    if dropbox_login:
        settings.dropbox_login()
        return
    if clear_conf:
        utils.install()
        return

    local_image = utils.screenshot()
    assert os.path.exists(local_image)
    filename = utils.get_filename()
    url = upload.upload(local_image, filename)
    print(url)
    utils.set_clipboard(url)
    conf = settings.get_conf()
    if conf.get('file').as_bool('keep'):
        dest_dir = os.path.expanduser(conf['file']['dir'])
        if not os.path.exists(dest_dir):
            os.mkdir(dest_dir)
        dest = os.path.join(dest_dir, filename)
        shutil.move(local_image, dest)
    else:
        os.unlink(local_image)

def dispatch():
    main.command()

if __name__ == '__main__':
    dispatch()
