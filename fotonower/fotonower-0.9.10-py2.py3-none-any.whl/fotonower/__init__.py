# -*- coding: utf-8 -*-
import requests
import json
import sys

# le token provient de la page www.fotonower.com/me/developer

class FotonowerConnect:
    def __init__(self, token, host = "www.fotonower.com", protocol = "http", log_level = 1):
        self.protocol = protocol
        self.host = host
        self.api_version = "/api/v1"
        self.upload_endpoint = "/secured/photo/upload"
        self.face_bucket = "/secured/velours/faceBucket"
        self.features = "/secured/velours/features"
        self.portfolioSavePost = "/portfolio/savePost"
        self.getNewPortfolio = "/secured/portfolio/new"
        self.token_arg = "token"
        self.token = str(token)
        self.lf_arg = "list_photo_ids"
        self.bibn_arg = "bibnumber"
        self.nb_bucket_arg = "nb_bucket"
        self.photo_hashtag_type_arg = "photo_hashtag_type"
        self.photo_desc_type_arg = "photo_desc_type"
        self.log = log_level


    def get_new_portfolio(self, portfolio_name = "", list_photo_ids = [], verbose = False):

        url = "http://" + self.host + self.api_version + self.getNewPortfolio

        list_photo_ids_csv = ",".join(map(str, list_photo_ids))

        args_get = {}
        if portfolio_name != "":
            args_get["name"] = portfolio_name

        args_get["access_token"] = self.token

        if args_get != {} :
            url += "?" + "&".join(map(lambda x : str(x) + "=" + str(args_get[x]),args_get))

# does-this works ?
# MG 26/04/18 for a post request maybie
#        r = requests.get(url, data={'portfolio_name':portfolio_name, "access_token" : self.token})
        r = requests.get(url)

        portfolio_id = 0

        if r.status_code == 200 :
            res_json = json.loads(r.content.decode("utf8"))
            if self.log > 1 :
                print (res_json)
            elif self.log == 1:
                print("request status OK")
            #portfolio_id = res_json['portfolio_id']
            if type(res_json) == type(0) :
                portfolio_id = res_json
            elif type(res_json) == type({}) :
                if 'portfolio_id' in res_json :
                    portfolio_id = res_json['portfolio_id']
            #print portfolio_id
        else :
            if self.log > 0:
                print (" Status : " + str(r.status_code))
                print (" Content : " + str(r.content))
                print (" All Response : " + str(r))
            else:
                print("Error : " + str(r.status_code))
        return portfolio_id


    def create_portfolio(self, portfolio_name, list_photo_ids = [], verbose = False, arg_aux = {}):

        url = "http://" + self.host + self.api_version + self.portfolioSavePost

        import json, requests

        list_photo_ids_csv = ",".join(map(str, list_photo_ids))

        data_to_send = {'portfolio_name':portfolio_name, "access_token" : self.token, "list_photos_ids" : list_photo_ids_csv}

        data_to_send.update(arg_aux)

        r = requests.post(url, data=data_to_send)

        portfolio_id = 0

        if r.status_code == 200 :
            res_json = json.loads(r.content)
            if verbose :
                print (res_json)
            portfolio_id = res_json['portfolio_id']
            #print portfolio_id
        else :
            print (" Status : " + str(r.status_code))
            print (" Content : " + str(r.content))
            print (" All Response : " + str(r))

        return portfolio_id



    # "compute_classification" : False forced to false (for svm computation)
    def upload_medias(self, list_filenames, portfolio_id = 0, upload_small = False, hashtags = [], verbose = False, arg_aux = {}, compute_classification=False) :
      try :
        if verbose:
            print("in upload media")
            sys.stdout.flush()
        url = self.protocol+ "://" + self.host + self.api_version + self.upload_endpoint + "?" + self.token_arg + "=" + self.token

        if verbose :
            print (" Upload medias :  " + str(list_filenames) + " : url : " + url)
            sys.stdout.flush()

        files = {}
        map_file_id_filename= {}
        for i in range(len(list_filenames)) :
            if verbose :
                print(list_filenames[i])
                sys.stdout.flush()
            key = "file" + str(i)
            map_file_id_filename[key] = list_filenames[i]#.replace('\xc2\xa', ' ')
            try:
                files[key] = open(list_filenames[i], 'rb')
            except Exception as e:
                print(e)
                print(list_filenames[i])
                print("error while trying to upload this file need to reupload it manually in portfolio " + str(portfolio_id))

        # we could pass others arguments if needed
        data_to_send = {'portfolio_id':portfolio_id, "upload_small" : upload_small, "compute_classification" : compute_classification}
        data_to_send.update(arg_aux)
        if verbose:
            print("after data_to_send, before sending request")
        r = requests.post(url, files=files, data=data_to_send)
        if verbose:
            print("after request")
        sys.stdout.flush()
        if verbose :
            print (r)
            #print (r.response)
            print (r.content)

        if r.status_code == 200 :
            print ("Result OK !")
            sys.stdout.flush()
            res_json = json.loads(r.content.decode("utf8"))
            #martigan 250418 : @moilerat je ne suis pas trop sur de ce comportement mais il faut que l on récupere
            # les résultats quand il y a eu un traitement, l association filename/photo_id me parait moins importante
            if "result" in res_json and "map_files_photo_id" in res_json:
                map_filename_photo_id = {}
                map_files_photo_id = res_json["map_files_photo_id"]
                for f in map_files_photo_id:
                    photo_id = map_files_photo_id[f]
                    if f in map_file_id_filename:
                        filename = map_file_id_filename[f]
                        map_filename_photo_id[filename] = photo_id
                    else:
                        print("Missing filename !")

                return map_filename_photo_id,res_json['result']


            if "map_files_photo_id" in res_json:
                map_filename_photo_id = {}
                map_files_photo_id = res_json["map_files_photo_id"]
                for f in map_files_photo_id :
                    photo_id = map_files_photo_id[f]
                    if f in map_file_id_filename :
                        filename = map_file_id_filename[f]
                        map_filename_photo_id[filename] = photo_id
                    else :
                        print("Missing filename !")

                return map_filename_photo_id

#            if "photo_ids" in res_json :
#                print("This case can't be treated correctly WARNING !")
#                return res_json["photo_ids"]

            if 'photo_id' in res_json :
                if len(list_filenames) > 1 :
                    print ("Some filename were not uploaded !")
                #return res_json['photo_id']
                return {list_filenames[0]:res_json['photo_id']}
        else :
            print(str(r.status))

        for line in r.content.split("\n") :
            if "This exception" in line:
                print (line)

        return 0
      except Exception as e:
          sys.stdout.flush()
          print("ERROR IN API l 160 " + str(e))
          return 0



    def upload_media(self, filename, portfolio_id = 0, hashtags = [], verbose = False) :
      try :
        url = self.protocol+ "://" + self.host + self.api_version + self.upload_endpoint + "?" + self.token_arg + "=" + self.token

        if verbose :
            print (" Upload media :  " + filename + " : url : " + url)

        # we could pass others arguments if needed
        r = requests.post(url, files={'file': open(filename, 'rb')}, data={'portfolio_id':portfolio_id})

        if verbose :
            print (r)
            #print (r.response)
            print (r.content)

        if r.status_code == 200 :
            print ("Result OK !")
            res_json = json.loads(r.content.decode("utf8"))

            if 'photo_id' in res_json :
                return res_json['photo_id']

        return 0
      except Exception as e:
          print("ERROR IN API l189 " + str(e))
          return 0



    def faceBucket(self, list_of_face_as_photo_id, bibnumber = 0, nb_bucket = 6, photo_hashtag_type = 67, photo_desc_type = 0, verbose = False) :
      try :
        if len(list_of_face_as_photo_id) <= 3:
            if verbose :
                sys.stdout.write("3")
                #print "Less than three is useless !"
            return {}
        if len(list_of_face_as_photo_id) >= 100 :
            if verbose :
                print ("  list_of_face_as_photo_id : " + str(len(list_of_face_as_photo_id)))
            return {}

        list = ",".join(map(str, list_of_face_as_photo_id))
        url = self.protocol+ "://" + self.host + self.api_version + self.face_bucket + "?" + self.token_arg + "=" + self.token + "&" + self.lf_arg + "=" + list
        url += "&" + self.nb_bucket_arg + "=" + nb_bucket
        url += "&" + self.photo_hashtag_type_arg + "=" + str(photo_hashtag_type)
        url += "&" + self.photo_desc_type_arg + "=" + str(photo_desc_type)

        if bibnumber != 0 :
            url += "&" + self.bibn_arg + "=" + str(bibnumber)

        if verbose :
            print (" faceBucket : url : " + url)

        # we could pass others arguments if needed
        r = requests.post(url)

        #if verbose :
            #print (r)
            #print (r.content)

        if r.status_code == 200 :
            print ("Result OK !")
            res_json = json.loads(r.content)

            res_to_send = {}
            for k in res_json :
                res_to_send[int(k)] = res_json[k]

            return res_to_send

            #if 'photo_id' in res_json and len(res_json['photo_id']) :
            #    return res_json['photo_id'][0]

        return {}
      except Exception as e :
          print (str(e))
          return {}



    def veloursFeature(self, list_photo_ids, photo_desc_type = 0, verbose = False) :

        list = ",".join(map(str, list_photo_ids))
        url = self.protocol+ "://" + self.host + self.api_version + self.features + "?" + self.token_arg + "=" + self.token + "&" + self.lf_arg + "=" + list
        url += "&" + self.photo_desc_type_arg + "=" + str(photo_desc_type)

        if verbose :
            print (" faceBucket : url : " + url)

        # we could pass others arguments if needed
        r = requests.get(url)

        #if verbose :
            #print (r)
            #print (r.content)

        if r.status_code == 200 :
            print ("Result OK !")
            res_json = json.loads(r.content)

            return res_json

            #if 'photo_id' in res_json and len(res_json['photo_id']) :
            #    return res_json['photo_id'][0]

        return {}


