from urllib import request as req
import getopt
import sys
import re


def get_k_song(url):
    try:
        response = req.urlopen(url)
        html = response.read().decode()
        content = re.search('{"activity_id.+(?=,"lyric)', html).group()
        song_info = eval(content)
    except:
        pass
    return song_info


def log(site, title, stream_type, stream_format, stream_size, filename):
    print('——————————————————————————————')
    print('- Site: \t', site)
    print('- Title: \t', title)
    print('- Stream: \t')
    print('    - type: \t', stream_type)
    print('    - format: \t', stream_format)
    print('    - size: \t', stream_size+' B')
    print('')
    print('downloading...'+filename)
    print('███████████(进度条未实现)')


def main():
    _DEBUG = True
    try:
        opts, args = getopt.getopt(sys.argv[1:], ":ho:v:", ['--debug', "output="])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    if len(arg)<0:
        raise Exception
    song = get_k_song(url)
    title = song['song_name']+' - '+song['nick']
    file_info = req.urlopen(song['playurl']).info()
    log('全民K歌', title, file_info['Content-Type'], '.m4a', file_info['True-Size'], title+'.m4a')
    req.urlretrieve(song['playurl'], title+'.m4a')
    print('Finish! ')

if __name__ == "__main__":
    main()
