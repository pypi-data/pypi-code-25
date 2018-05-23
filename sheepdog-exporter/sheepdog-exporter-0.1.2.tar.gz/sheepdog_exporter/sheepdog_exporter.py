#!/usr/local/bin/python3.5
# encoding: utf-8
'''
 -- Export metadata from sheepdog

 is a description

It defines classes_and_methods

@author:     David Steinberg

@copyright:  2018 UCSC Genomics Institute. All rights reserved.

@license:    Apache 2

@contact:    davidcs@ucsc.edu
@deffield    updated: May 22, 2018
'''

import sys
import os
import csv
import json

import csv
import json
import os

import requests
from pmap.core import pmap

from io import StringIO

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2018-05-22'
__updated__ = '2018-05-22'


class Exporter:

    def __init__(self, credentials_filename, base_url):
        self.base_url = base_url
        self.access_token = self.access_token(
            credentials_filename)
        self.sheep_url = '{}/api/v0/submission'.format(base_url)
    
    def headers(self):
        '''
        Return the headers dict that includes the access token for 
        creating a request.
        '''
        return {'Authorization': 'bearer ' + self.access_token}
    
    def access_token(self, filename):
        '''
        Get a fence access token using a path to a credentials.json
        and return that token.
        '''
        auth_url = '{}/user/credentials/cdis/access_token'.format(self.base_url)
        print('Using {} to get an access token.'.format(filename))
        try:
            json_data = open(filename).read()
            keys = json.loads(json_data)
        except Exception as e:
            print('Failed to find your credentials! Check your credentials path: {} \n {}'.format(filename, str(e)))
            return None
        print('Getting access token from {} .'.format(auth_url))
        try:
            access_token = requests.post(auth_url, json=keys).json()['access_token']
        except Exception as e:
            print('Failed to authenticate! Check the URL {} \n {}'.format(auth_url, str(e)))
            return None
        return access_token
    
    def get_dictionary(self, program, project):
        '''
        Gets the schema for a program and project and returns
        it as a dict.
        '''
        dictionary_url = '{}/{}/{}/_dictionary'.format(self.sheep_url, program, project)
        response = requests.get(
            dictionary_url,
            headers=self.headers())
        return response.json()
    
    def get_schema_for_type(self, program, project, my_type):
        '''
        Return the JSON schema for a given program, project, and type.
        '''
        dictionary_url = '{}/{}/{}/_dictionary/{}'.format(self.sheep_url, program, project, my_type)
        return requests.get(
            dictionary_url,
            headers=self.headers()).json()
    
    def get_submissions_by_type(self, program, project, my_type):
        '''
        Returns all the submissions for a given program, 
        project, type triplet.
        '''
        url = '{}/{}/{}/export/?node_label={}'.format(self.sheep_url, program, project, my_type)
        # FIXME returns a TSV
        return requests.get(url, headers=self.headers()).content
    
    def get_json_submission_by_type(self, program, project, my_type):
        '''
        Returns the JSON version of a program, project, type triplet
        and returns a list of dictionaries.
        '''
        print('Getting {} submissions.'.format(my_type))
        # FIXME JSON serialization is done by the server
        buf = StringIO(self.get_submissions_by_type(program, project, my_type).decode('utf-8'))
        reader = csv.DictReader(buf, delimiter='\t')
        return list(reader)
    
    def get_programs(self):
        '''
        Returns the list of projects for a given program.
        '''
        programs_url = '{}/'.format(self.sheep_url)
        raw_programs = requests.get(programs_url, headers=self.headers()).json()['links']
        return map(os.path.basename, raw_programs)
    
    def get_projects(self, program):
        '''
        Returns the list of projects for a given program.
        '''
        projects_url = '{}/{}/'.format(self.sheep_url, program)
        raw_projects = requests.get(projects_url, headers=self.headers()).json()['links']
        return map(os.path.basename, raw_projects)
    
    def get_all_submissions(self, program, project):
        '''
        Export all of the types for a given program and project
        and return them as a dictionary with keys for each type.
        '''
        print('Getting dictionary for {}-{}'.format(program, project))
        submission_dictionary = self.get_dictionary(program, project)
        submission_list = pmap(lambda x: self.get_json_submission_by_type(program, project, os.path.basename(x)), submission_dictionary['links'])
        
        return dict(zip(submission_dictionary['links'], submission_list))




def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_license = '''
    sheepdog-exporter
    

  Created by David Steinberg on %s.
  Copyright 2018 Genomics Institute. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (str(__date__))

    try:
        print('''
            o                    o                                    o          
            |                    |                                    |          
        o-o O--o o-o o-o o-o   o-O o-o o--o     o-o \ / o-o  o-o o-o -o- o-o o-o 
         \  |  | |-' |-' |  | |  | | | |  |     |-'  o  |  | | | |    |  |-' |   
        o-o o  o o-o o-o O-o   o-o o-o o--O     o-o / \ O-o  o-o o    o  o-o o   
                         |                |             |                        
                         o             o--o             o    
                                             
                         Export DCP metadata from the CLI!!!
        ''')
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('program', nargs='?', type=str, help='The DCP Program to export. Leave blank to list programs.')
        parser.add_argument('project', nargs='?', type=str, help='The DCP Project to export. Leave blank to list projects.')
        parser.add_argument('--dcp-url', type=str, help='The URL of the DCP service (default: https://dcp.bionimbus.org', default='https://dcp.bionimbus.org')
        parser.add_argument('--credentials', type=str, help='The path to your DCP credentials.json (default: ./credentials.json', default='./credentials.json')
        parser.add_argument('--output_path', type=str, help='The path to place the resulting export (default: ./', default='./')
        
        
        # Process arguments
        args = parser.parse_args()

        exporter = Exporter(
            args.credentials,
            args.dcp_url)
        
        if not args.program:
            programs = exporter.get_programs()
            print('Programs available at {}:'.format(args.dcp_url))
            print('')
            print("     {}".format('\n     '.join(programs)))
            print('')
            print('Try entering `sheepdog-exporter {}` to list projects!'.format(args.program, programs[0]))
        
        elif args.program and not args.project:
            projects = exporter.get_projects(args.program)
            print('Projects for program {}:'.format(args.program))
            print('')
            print("     {}".format('\n     '.join(projects)))
            print('')
            print('Try entering `sheepdog-exporter {program} {project}` to output "{program}-{project}.json"!'.format(project=projects[0], program=args.program))
        elif args.program and args.project:
            print('Exporting {}-{} from {}'.format(args.program, args.project, args.dcp_url))
            try:
                exported = exporter.get_all_submissions(
                    args.program, args.project)
            except Exception as e:
                print(str(e))
                return 1
            output_path = '{}/{}-{}.json'.format(
                args.output_path, args.program, args.project)
            outfile = open(output_path, 'w')
            json.dump(exported, outfile)
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    sys.exit(main())