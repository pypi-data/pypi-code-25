
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
                 
        


