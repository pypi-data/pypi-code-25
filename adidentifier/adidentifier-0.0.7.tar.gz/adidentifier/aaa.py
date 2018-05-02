
# -*- coding: UTF-8 -*-

from adidentifier import AdIdentifier
if __name__ == "__main__":

    ad = AdIdentifier()
    adtexts1 = [
         "速贷之家-借钱不担心_2小时到账","https://www.aiqianzhan.com/html/register3_bd4.html?utm_source=bd4-pc-ss&utm_medium=bd4SEM&utm_campaign=D1-%BE%BA%C6%B7%B4%CA-YD&utm_content=%BE%BA%C6%B7%B4%CA-%C3%FB%B4%CA&utm_term=p2p%CD%F8%B4%FB"]
    for text in adtexts1:
        resu = ad.is_finance(text)
        print text,"------->>", resu
    
    adtexts2 = ["https://ss3.baidu.com/-rVXeDTa2gU2pMbgoY3K/it/u=3778907493,3669893773&fm=202&mola=new&crop=v1",
                "https://ss2.bdstatic.com/8_V1bjqh_Q23odCf/pacific/upload_25289207_1521622472509.png?x=0&y=0&h=150&w=242&vh=92.98&vw=150.00&oh=150.00&ow=242.00",
                "http://pagead2.googlesyndication.com/pagead/show_ads.js",
                "http://www.googletagservices.com/tag/js/gpt_mobile.js"]
    for text in adtexts2:
        resu = ad.is_ad(text)
        print(text, "------>>", resu)

    print("============")
    print ad.get_target_from_href("https://www.baidu.com/baidu.php?url=0f0000jsnOdydCYpIY2xQXFCV1h5YmZnZh_pWjXI1sMrqQiM8Y55S59-6yXvznN6gm_5K2BIwOl4qzVcr2qRUIZdYnyTM2gOTAL-ed0xhaXP7ZI4XoxPJtWsnc4vPT3Qgcpo8dLTicCsAu_tZqqn5DH0sVytFArXV5kfFxBwLN5Kyia2R0.DD_NR2Ar5Od663rj6t8ae9zC63p_jnNKtAlEuw9zsISgZsIoDgQvTVxQgzdtEZ-LTEuzk3x5I9qxo9vU_5Mvmxgv3IhOj4en5VS8ZutEOOS1j4SrZdSyZxg9tqhZden5o3OOOqhZ1tT5ot_rSEj4en5ovmxgkl32AM-WI6h9ikX1BsIT7jHzlRL5spycTT5y9G4mgwRDkRAcY_1fdIT7jHzs_lTUQqRHAZ1tT5ot_rSEj4en5ovmxgkl32AM-CFhY_mx5ksSEzselt5M_sSEu9qx7i_nYQZu_LSr4f.U1Yk0ZDq1xBYSsKspynqn0KY5TL3V5_0pyYqnWcd0ATqmhRLn0KdpHdBmy-bIfKspyfqnWR0mv-b5Hckr0KVIjYknjDLg1DsnH-xnW0vn-t1PW0k0AVG5H00TMfqP1cz0ANGujYkPjmvg1cvnWR4g1cknH0Yg1cznHR40AFG5HcsP0KVm1YLPjDknjnknjIxP1fkPWckP1f1g1DkP1bkrHD1nHIxn0KkTA-b5H00TyPGujYs0ZFMIA7M5H00mycqn7ts0ANzu1Ys0ZKs5H00UMus5H08nj0snj0snj00Ugws5H00uAwETjYs0ZFJ5H00uANv5gKW0AuY5H00TA6qn0KET1Ys0AFL5HDs0A4Y5H00TLCq0ZwdT1YLPHTvnHnLPWTLrjmkPWmvnHfk0ZF-TgfqnHRzPHcYrH0knj0dPsK1pyfqrHNhmW-9m10snj0suARvrfKWTvYqPWD4PRuAPHc3Pbw7wj9arfK9m1Yk0ZK85H00TydY5H00Tyd15H00XMfqn0KVmdqhThqV5HKxn7tsg100uA78IyF-gLK_my4GuZnqn7tsg1Kxn0Ksmgwxuhk9u1Ys0AwWpyfqn0K-IA-b5iYk0A71TAPW5H00IgKGUhPW5H00Tydh5H00uhPdIjYs0AulpjYs0Au9IjYs0ZGsUZN15H00mywhUA7M5HD0UAuW5H00mLFW5HfsPHmv&us=0.0.0.0.0.0.0.101&ck=0.0.0.0.0.0.0.0&shh=www.baidu.com&sht=baidu")

    print ad.get_domain_from_url("https://www.asdasd.com/asdasd")

    # a = {
    #     "target": this.href
    #     "img": this.img.src
    #     "text": extract_text_from(this.content.html)  
    # }

    # a_lists = execute(html)

    # for a in a_lists:
    #     if is_external_link(target):
    #         if (a.img and is_ad(a.img)) or  is_finance(target) or (text and is_finance(text)) :
    #             result.append(a)
                 
        


