import v_vk_api

api = v_vk_api.create(proxies={'http': '18.218.172.146:8118', 'https': '18.218.172.146:8118'})
print(api.request_method('users.get', user_ids=1))