import re, os
from collections import Counter
from bl_product_amaz.database import DataBase
from bl_product_amaz.us_btgs import US_btgs
from bl_product_amaz.amz_attrs import AMZ_attrs
from bl_product_amaz.amz_sub_attrs import AMZ_sub_attrs
from bl_product_amaz.amz_title_dic import AMZ_title_dic
from bl_db_product_amz_best.products import Products


class Title_filter(DataBase):
    def __init__(self):
        super(Title_filter, self).__init__()
        self.us_btgs_api = US_btgs()
        self.amz_attrs_api = AMZ_attrs()
        self.amz_sub_attrs_api = AMZ_sub_attrs()
        self.amz_title_dic = AMZ_title_dic()
        self.titles = Products()

    def get_title_word_dic_by_node_id(self, node_ids):
        amz_attr_list = []
        filter_list = []

        # get sub_attrs text and make filter
        for node_id in node_ids:
            res = self.us_btgs_api.get_btg_by_node_id(node_id)
            for amz_attr in res['attr_ids']:
                amz_attr_list.append(amz_attr)

        for amz_attr_id in amz_attr_list:
            res1 = self.amz_attrs_api.get_title_dic_by_attr_id(amz_attr_id)
            filter_list.extend(res1)

        filter_list = sorted(filter_list, key=len)

        for i in range(len(filter_list)):
            filter_list[i] =  filter_list[i].lower()

        return filter_list




    def filtering_titles(self, node_ids, filter_list):
        filtered_titles = []
        titles = []
        offset = 0
        limit = 100


        # get titles
        for node_id in node_ids:
            try:
                r = self.titles.get_products_by_node_id(node_id, offset, limit)
                for product in r:
                    title_dic = {}
                    title_dic['ASIN'] = product['ASIN']
                    title_dic['brand'] = product['Brand']
                    title_dic['title'] = product['Title']
                    titles.append(title_dic)
            except Exception as e:
                print(e)

        # filtering by title dic
        for title_info in titles:
            title = title_info['title']
            # remove brand
            title = title.replace(title_info['brand'],"")
            title = title.lower()
            title = title.replace("(", "")
            title = title.replace(")", "")
            title = title.replace(",", " ")

            for filter in filter_list: # 길이 순서대로
                title = re.sub('\\b'+filter+' '+'\\b',"",title)

            title_info['filtered_title'] = title


        # data clouding
        for title in titles:
            tmp = title['title'].split(" ")
            filtered_titles.extend(tmp)

        result_words = Counter(filtered_titles)

        return titles, result_words

    def add_sub_attr_in_amz_sub_attrs(self, node_id, attr_id, attr_kr_name, attr_us_name,
                     sub_attr_id, sub_attr_kr_name, sub_attr_us_name):

        # check attr_id is in amz_attrs DB
        # add attr_id in amz_attrs DB and us_btg that node_id is input node_id
        self.amz_attrs_api.add_attr(attr_id, attr_kr_name, attr_us_name)
        self.us_btgs_api.update_attr_id_by_node_id(node_id, attr_id)

        # add sub_attr in amz_sub_attrs DB
        self.amz_sub_attrs_api.add_sub_attr(sub_attr_id, sub_attr_kr_name, sub_attr_us_name)
        self.amz_attrs_api.update_sub_attr_ids(attr_id, sub_attr_id)


    def add_sub_attr_word_in_amz_title_dic(self, sub_attr_id, sub_attr_word):

        self.amz_title_dic.add_title_dic_word(sub_attr_id, sub_attr_word)















