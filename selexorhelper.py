"""
<Program Name>
  selexorruleparserhelper.py

<Started>
  July 24, 2012

<Author>
  leon.wlaw@gmail.com
  Leonard Law

<Purpose>
  Contains helper functions that are needed by selexor.

"""
import math
import selexorexceptions
import os
import seattleclearinghouse_xmlrpc

helpercontext = {}

def initialize():
  helpercontext['COUNTRY_TO_ID'] = load_ids('country')
  # This takes up too much memory...
  # helpercontext['CITY_TO_ID'] = load_ids('city')



def get_city_id(cityname):
  # City table takes up several hundred MB of space... We treat all city names
  # as valid for now
  return cityname


def get_country_id(countryname):
  countryname = countryname.lower()
  try:
    return helpercontext['COUNTRY_TO_ID'][countryname]
  except KeyError, e:
    raise selexorexceptions.UnknownLocation(countryname)


def load_ids(idtype):
  id_file = open('./lookup/' + idtype + '.txt', 'r')
  id_map = {}

  line = id_file.readline().lower()
  while line:
    ids = line.split('\t')
    good_id = ids[0].strip()
    for id in ids:
      id_map[id.strip()] = good_id

    line = id_file.readline().lower()
  id_file.close()
  return id_map


def connect_to_clearinghouse(authdata, allow_ssl_insecure = False, xmlrpc_url = None, debug=False):
  '''
  <Purpose>
    Wrapper for a SeattleClearinghouseClient constructor.
  <Arguments>
    authdata:
      An authdict. See module documentation for more information.
  <Exceptions>
    SelexorAuthenticationFailed
  <Side Effects>
    Opens an outgoing connection to the specified clearinghouse.
  <Returns>
    A client object that can be used to communicate with the Clearinghouse as the
    specified user.

  '''
  username = authdata.keys()[0]
  apikey = None
  private_key_string = None

  if 'apikey' in authdata[username]:
    apikey = authdata[username]['apikey']
  if 'privatekey' in authdata[username]:
      private_key_string = rsa_repy.rsa_privatekey_to_string(authdata[username]['privatekey'])

  if not (apikey or private_key_string):
    raise selexorexceptions.SelexorAuthenticationFailed("Either apikey or privatekey must be given!")

  client = seattleclearinghouse_xmlrpc.SeattleClearinghouseClient(
      username = username,
      api_key = apikey,
      xmlrpc_url = xmlrpc_url,
      private_key_string = private_key_string,
      allow_ssl_insecure = allow_ssl_insecure)

  return client


def haversine_distance(long1, lat1, long2, lat2):
  '''
  Given two coordinates, calculate the great circle distance between them.
  These coordinates are specified in decimal degrees.

  '''
  # convert decimal degrees to radians
  long1 = math.radians(long1)
  long2 = math.radians(long2)
  lat1 = math.radians(lat1)
  lat2 = math.radians(lat2)
  # haversine formula
  dlong = long2 - long1
  dlat = lat2 - lat1
  a = math.sin(dlat / 2) ** 2
  b = math.cos(lat1) * math.cos(lat2) * math.sin(dlong / 2) ** 2
  c = 2 * math.asin(math.sqrt(a + b))
  dist = 6367 * c
  return dist


def haversine_distance_between_handles(handledict1, handledict2):
  return haversine_distance(handledict1['geographic']['longitude'], handledict1['geographic']['latitude'],
                            handledict2['geographic']['longitude'], handledict2['geographic']['latitude'])


def get_handle_location(handle, loctype, database):
  if loctype == 'cities':
    return (database.handle_table[handle]['geographic']['city'], database.handle_table[handle]['geographic']['country_code'])
  if loctype == 'countries':
    return (database.handle_table[handle]['geographic']['country_code'],)
  raise UnknownLocationType(loctype)
