"""
Irods Python Module, wraps calls
"""


import os
from irods.session import iRODSSession

import re, json
import mimetypes
import base64
import traceback




class Irods:
    """
    Parent class for helper IROD commands
    """

    session = None

    def set_connection(self, json_body):
        self.session = iRODSSession(host=json_body['host'], port=json_body['port'], user=json_body['user'], password=json_body['password'], zone=json_body['zone'])

    def delete (self, current_path):
        """ deletes file """
        try:
            obj = self.session.data_objects.get(current_path)
            obj.unlink(force=True)
        except:
            print("there was an error deleting that file")


    def patch(self, current_path, json_body):
        """ rename file """

        json_body = "/" + json_body
        
        try:
            self.session.data_objects.move(current_path,json_body)
        except:
            # maybe its a folder.
            try:
               self.session.collections.move(current_path,json_body)
            except:
                print("Could not rename, tried folder and file")


    def post(self, current_path, json_body):
        """ create file """

        print ("post")
        print (current_path)
        print (json_body)

        if (json_body == "notebook" or json_body == "file"):

            try:
                obj = self.session.data_objects.create(current_path)
                my_content = "edit me"

                if (json_body == "notebook"):
                    my_content = '{ "cells": [ { "cell_type": "code", "execution_count": null, "metadata": { }, "outputs": [], "source": [] } ], "metadata": { "kernelspec": { "display_name": "Python 3", "language": "python", "name": "python3" }, "language_info": { "codemirror_mode": { "name": "ipython", "version": 3 }, "file_extension": ".py", "mimetype": "text/x-python", "name": "python", "nbconvert_exporter": "python", "pygments_lexer": "ipython3", "version": "3.6.4" } }, "nbformat": 4, "nbformat_minor": 2 }'

                with obj.open('w') as f:
                    f.seek(0,0);
                    f.write(my_content.encode())

                return {

                    "name": obj.name,
                    "path": obj.name,
                    "last_modified": "2018-03-05T17:02:11.246961Z",
                    "created":"2018-03-05T17:02:11.246961Z",
                    "content": my_content,
                    "format": "text",
                    "mimetype":"text/*",
                    "writable":False,
                    "type":"file"
                }

            except:
                print("error creating the file ")
        
        if (json_body == "directory"):
            print(current_path)
            coll = self.session.collections.create(current_path)

            result = {

                "name": coll.name,
                "path": coll.name,
                "last_modified": "2018-03-05T17:02:11.246961Z",
                "created":"2018-03-05T17:02:11.246961Z",
                "content":[],
                "format": "json",
                "mimetype":None,
                "writable":True,
                "type":"directory"
            }

            return result


    def put(self, current_path, json_body):
        """ save file """

        print(current_path)
        print(json_body)

        data = json_body
        print(data)
        print (data['content'])

        if (type(data['content'] is dict )):
            data['content'] = json.dumps(data['content'])

        obj = self.session.data_objects.get(current_path)

        with obj.open('w') as f:
            f.seek(0,0);
            f.write(data['content'].encode())

        return "done"


    def get(self, current_path):
        """
        Used to get contents of current directory
        """

        if ( self.session == None) :
            return {

                "name": "folder_name",
                "path": "folder_path",
                "last_modified": "2018-03-05T17:02:11.246961Z",
                "created":"2018-03-05T17:02:11.246961Z",
                "content": [],
                "format": "json",
                "mimetype":None,
                "writable":False,
                "type":"directory"
            }

        try:
            coll = self.session.collections.get(current_path)

            folders = coll.subcollections
            files = coll.data_objects
            result = {

                "name": "folder_name",
                "path": "folder_path",
                "last_modified": "2018-03-05T17:02:11.246961Z",
                "created":"2018-03-05T17:02:11.246961Z",
                "content":[],
                "format": "json",
                "mimetype":None,
                "writable":True,
                "type":"directory"
            }

            for folder in folders:
                result['content'].append({
                    "name":folder.name,
                    "path":current_path+"/"+folder.name,
                    "last_modified": "2018-03-05T17:02:11.246961Z",
                    "created":"2018-03-05T17:02:11.246961Z",
                    "content":None,
                    "format": "json",
                    "mimetype":None,
                    "writable":True,
                    "type":"directory"
                })

            for f in files:
                result['content'].append({
                    "name":f.name,
                    "path":current_path+"/"+f.name,
                    "last_modified": "2018-03-05T17:02:11.246961Z",
                    "created":"2018-03-05T17:02:11.246961Z",
                    "content": None,
                    "format": "text",
                    "mimetype":"text/*",
                    "writable":False,
                    "type":"file"
                })
          
            return result
        except:            
            try:
                obj = self.session.data_objects.get(current_path)

                if (obj.size > 1048576):
                    return {
                        "name": "error",
                        "path": "error",
                        "last_modified": "2018-03-05T17:02:11.246961Z",
                        "created":"2018-03-05T17:02:11.246961Z",
                        "content": "This file is too large to view in Jupyter Lab\nMax file size 100mb",
                        "format": "text",
                        "mimetype":"error",
                        "writable":False,
                        "type":"file"
                    }

                mtype = mimetypes.guess_type(obj.name)
                ftype = "text"
                file_string = ""

                with obj.open('r+') as f:
                    f.seek(0,0)
                    file_string = f.read()

                print (mtype)
                 
                mtype = mtype[0]
                
                if ("image" in mtype):
                    print("yes")
                    file_string = str(base64.b64encode(file_string).decode('ascii'))
                    ftype = "base64"
                else:
                    print("no")
                    file_string = str(file_string.decode('UTF-8'))

                

                return {

                    "name": obj.name,
                    "path": obj.name,
                    "last_modified": "2018-03-05T17:02:11.246961Z",
                    "created":"2018-03-05T17:02:11.246961Z",
                    "content": file_string,
                    "format": str(ftype),
                    "mimetype":str(mtype),
                    "writable":False,
                    "type":"file"
                }

            except Exception as e:
                print (e)
                print (traceback.format_exc())
                return {
                    "name": "folder_name",
                    "path": "folder_path",
                    "last_modified": "2018-03-05T17:02:11.246961Z",
                    "created":"2018-03-05T17:02:11.246961Z",
                    "content": [{
                        "name": "INVALID IRODS CONFIG",
                        "path": "INVALID IRODS CONFIG",
                        "last_modified": "2018-03-05T17:02:11.246961Z",
                        "created":"2018-03-05T17:02:11.246961Z",
                        "content": [],
                        "format": "json",
                        "mimetype":None,
                        "writable":False,
                        "type":"directory"
                    }],
                    "format": "json",
                    "mimetype":None,
                    "writable":False,
                    "type":"directory"
                }