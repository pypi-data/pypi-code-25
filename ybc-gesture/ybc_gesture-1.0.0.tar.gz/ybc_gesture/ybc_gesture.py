import ybc_youtuyun
appid = '10114485'
secret_id = 'AKIDYtynLcYPu98rJVP6VdV7TYNyJOCkP6wW'
secret_key = 'SeZEcniMjqgIejXUDhvwhCRRAdqnUu4x'
userid = '382771946'
end_point = ybc_youtuyun.conf.API_YOUTU_END_POINT

def gesture_recog(filename=''):
    if not filename:
        return -1
    youtu = ybc_youtuyun.YouTu(appid, secret_id, secret_key, userid, end_point)
    gRecog = youtu.gestureRecog(filename)
    if gRecog['items']:
        recog_dict = {
            'ONE':1,
            'TWO':2,
            'THREE':3,
            'FOUR':4,
            'FIVE':5,
            'SIX':6,
            'SEVEN':7,
            'EIGHT':8,
            'NINE':9,
            'TEN':10,
            'LIKE':'点赞',
            'LOVE':'我爱你',
            'HEART':'比心',
            'OK':'OK',
            'ROCK':'摇滚',
            'SCISSOR':'剪刀',
            'PAPER':'布',
            'FIST':'拳头'
        }
        return recog_dict.get(gRecog['items'][0]['label'],'手势暂时识别不出来~')
    else:
        return '手势暂时识别不出来~'
    return gRecog

def main():
    # res = gesture_recog('h1.jpg')
    # print(res)
    # res = gesture_recog('h2.jpg')
    # print(res)
    # res = gesture_recog('h3.jpg')
    # print(res)
    # res = gesture_recog('h4.jpg')
    # print(res)
    # res = gesture_recog('h5.jpg')
    # print(res)
    # res = gesture_recog('h6.jpg')
    # print(res)
    # res = gesture_recog('h7.jpg')
    # print(res)
    res = gesture_recog('h8.jpg')
    print(res)
    # res = gesture_recog('h9.jpg')
    # print(res)
    # res = gesture_recog('h10.jpg')
    # print(res)
    # res = gesture_recog('h11.png')
    # print(res)
    # res = gesture_recog('h12.png')
    # print(res)
    # res = gesture_recog('h13.jpg')
    # print(res)
    # res = gesture_recog('1.jpg')
    # print(res)

if __name__ == '__main__':
    main()
