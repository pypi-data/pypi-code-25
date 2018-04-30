import logging
import random
import unittest

from zebe.module.wechat import WeChatMiaoJiUser
from zebe.service.wechat import WeChatMiaoJiUserService


logging.basicConfig(level=logging.DEBUG)


class WechatServiceTest(unittest.TestCase):

    # 测试删除、添加和查询
    def __test_add(self):
        # 删除、查询全部数据
        service = WeChatMiaoJiUserService()
        service.delete_all()
        self.assertTrue(len(service.find_all()) == 0)
        # 添加
        user = WeChatMiaoJiUser()
        user.id = '3'
        user.nickname = 'Zebe'
        user.realname = '张成瑶'
        user.wxid = 'zebe1989'
        service.add(user)
        data_list = service.find_all()
        self.assertTrue(len(data_list) >= 1)
        # 查询单条数据
        data = data_list[0]
        data_find_one = service.find_one(data.id)
        self.assertIsNotNone(data_find_one)
        # 修改
        rand_str = str(random.randint(1, 100000))
        nickname = rand_str + '_rnd_nickname'
        realname = rand_str + '_rnd_realname'
        wxid = rand_str + '_rnd_wxid'
        data_find_one.nickname = nickname
        data_find_one.realname = realname
        data_find_one.wxid = wxid
        service.update(data_find_one)
        # 修改后查询校验是否修改完成
        data_find_one = service.find_one(data.id)
        self.assertTrue(data_find_one.nickname == nickname)
        self.assertTrue(data_find_one.realname == realname)
        self.assertTrue(data_find_one.wxid == wxid)
        # 删除单条数据
        #service.delete_one(data_find_one)
        service.delete_one_by_id(data.id)
        #service.delete_many_by_ids(['1', '2', '3'])
        self.assertTrue(len(service.find_all()) == 0)

    # 测试分页查询
    def test_find(self):
        # 清空数据
        service = WeChatMiaoJiUserService()
        service.delete_all()
        self.assertTrue(len(service.find_all()) == 0)
        # 添加数据1
        user1 = WeChatMiaoJiUser()
        user1.id = '1'
        user1.nickname = 'Zebe1'
        user1.realname = '张成瑶1'
        user1.wxid = 'zebe1989'
        service.add(user1)
        # 添加数据2
        user2 = WeChatMiaoJiUser()
        user2.id = '2'
        user2.nickname = 'Zebe2'
        user2.realname = '张成瑶2'
        user2.wxid = 'zebe1989'
        service.add(user2)
        # 添加数据3
        user3 = WeChatMiaoJiUser()
        user3.id = '3'
        user3.nickname = 'Zebe3'
        user3.realname = '张成瑶3'
        user3.wxid = 'zebe1989'
        service.add(user3)
        # 添加数据4
        user4 = WeChatMiaoJiUser()
        user4.id = '4'
        user4.nickname = 'Zebe4'
        user4.realname = '张成瑶4'
        user4.wxid = 'zebe1989'
        service.add(user4)
        # 查询第一页
        page_data = service.find_by_page(2, 1)
        for data in page_data:
            print(data)


if __name__ == '__main__':
    unittest.main()
