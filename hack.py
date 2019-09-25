#!/usr/bin/env python
"""
Description goes here
"""
from os.path import dirname

__author__ = "jupp"
__license__ = "Apache 2.0"
__date__ = "23/09/2019"

import requests
import json
import urllib.parse

ZOOMA_API="https://www.ebi.ac.uk/spot/zooma/v2/api"
ZOOMA_LOOKUP = ZOOMA_API + "/services/annotate?propertyValue={}"

OXO_API="https://www.ebi.ac.uk/spot/oxo/api/search"

mapped_to_snomed = {}



def get_oxo_mappings_to_snomed(uris):

    input_data = {
        'ids' : uris,
        "mappingTarget": ["SNOMEDCT"],
        'distance' : 2
    }

    response = requests.post(OXO_API, data=input_data)

    if (response.ok):
        return json.loads(response.content)


f = open("search_terms.txt", "r")
for x in f:
    x = x.strip()
    query = urllib.parse.quote_plus(x.strip())
    response = requests.get(ZOOMA_LOOKUP.format(query))
    if (response.ok):

        jData = json.loads(response.content)

        mapped_to_snomed[x] = {
            'query' : x,
            'mappings' : []
        }

        for annotation in jData:
            propertyType = annotation["annotatedProperty"]["propertyType"]
            propertyValue = annotation["annotatedProperty"]["propertyValue"]
            semanticTag = annotation["semanticTags"]
            confidence = annotation["confidence"]

            if confidence == "HIGH":
                mapped_to_snomed[x]['mappings'].append({
                    'pt': propertyType,
                    'pv' : propertyValue,
                    'st' : semanticTag
                })
                for oxo_result in get_oxo_mappings_to_snomed(semanticTag)["_embedded"]["searchResults"]:
                    if not oxo_result['mappingResponseList']:
                        print("{} maps to {}/{} with semantic tag {} - no mapping to SNOMED".format(x, propertyType, propertyValue, semanticTag))
                    else:
                        for mappings in oxo_result['mappingResponseList']:
                            print("{} maps to {}/{} with semantic tag {} - SNOMED code {} ({})".format(x, propertyType,
                                                                                                        propertyValue,
                                                                                                        semanticTag,
                                                                                                        mappings["curie"],
                                                                                                        mappings["label"]
                            ))







    else:
        # If response code is not ok (200), print the resulting http error code with description
        response.raise_for_status()