import baostock as bs


# 每次收到实时行情后，回调此方法
def callbackFunc(ResultData):
    print(ResultData.data)


if __name__ == '__main__':
    # 登陆
    login_result = bs.login_real_time(user_id='anonymous', password='123456')
    # 订阅
    rs = bs.subscribe_by_code("sh.600000", 3, "123", "", "test")
    if rs.error_code != '0':
        print("request real time error", rs.error_msg)
    else:
        # 使主程序不再向下执行。使用time.sleep()等方法也可以
        text = input("press any key to cancel real time \r\n")
        # 取消订阅
        cancel_rs = bs.cancel_subscribe(rs.serial_id)
    # 登出
    login_result = bs.logout_real_time("anonymous")
