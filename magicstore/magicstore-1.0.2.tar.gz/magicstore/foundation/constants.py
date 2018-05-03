# coding:utf-8


class _const:
    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError("can't change const %s" % name)
        if not name.isupper():
            raise self.ConstCaseError('const name "%s" is not all uppercase' % name)
        self.__dict__[name] = value


constant = _const()

constant.USER_PROFILE_DOES_NOT_EXIST = '用户概要信息不存在'
constant.USER_DOES_NOT_EXIST = '用户不存在'

constant.USER_OR_PASSWORD_DOES_NOT_CORRECT = '手机号或密码错误'
constant.IDENTIFICATION_IS_REQUIRED = '手机号不能为空。'
constant.PASSWORD_IS_REQUIRED = '密码不能为空'

constant.NO_ASSET_SUMMARY_WAS_FOUND = '资产概要信息不存在。'
constant.NO_ASSETS_WAS_FOUND = '资产信息不存在。'
constant.NO_CURRENCIES_WERE_FOUND = '货币不存在。'
constant.NO_EARNINGS_WAS_FOUND = '收益不存在。'
