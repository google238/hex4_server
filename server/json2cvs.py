#!/usr/bin/env python

from sys import argv
from os  import path
from types import *

import argparse
import logging
import json
import csv

def main():

    parser = argparse.ArgumentParser(
        description='Convert json file to csv'
    )

    parser.add_argument(    
        '-i', 
        '--input_file', 
        dest='input_file', 
        default=None, 
        required=True,
        help='Source json file (mandatory)'
    )
    parser.add_argument(
        '-o', 
        '--output_file', 
        dest='output_file', 
        default=None, 
        required=True,
        help='Destination csv file (mandatory)'
    )

    parser.add_argument(
        '-t', 
        '--type_round', 
        dest='type_round', 
        default=1, 
        required=True,
        help='file type'
    )

    args        = parser.parse_args()
    input_file  = args.input_file
    output_file = args.output_file
    type_round  = args.type_round
    print (type_round)
    json_data    = []
    data         = None
    if str(type_round) == "1": 
        item_keys    = ['comSkillNum','is_luckbonus','level','maxMoves','objectiveCollect','objectiveRequired','score','stars','ts','type','uid','useMoves','version','version_type','win']
    else:
        item_keys    = ['avatarID','level','miniID','ts','type','uid','version','version_type']
        

    with open(input_file) as json_file:
        json_data = json_file.read()

    try:
        data = json.loads(json_data)
    except Exception, e:
        raise e
    
    with open(output_file, 'wb') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(item_keys)
        for item in data:
            item_values = []
            for key in item_keys:
                value = item.get(key, '')
                if type(value) is StringTypes:
                    item_values.append(value.encode('utf-8'))
                else:
                    item_values.append(value)
            writer.writerow(item_values)
                
if __name__ == "__main__":
    main()
