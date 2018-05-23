
import config
import requests
import logging 

# _logger = logging.getLogger()
# _logger.setLevel(logging.INFO)


class TxMap(object):

    def __get_data_from_tx_server(self, url, param):
        param['key'] = config.APIKEY
        res = requests.get(url, params=param)
        return res.json()

    def get_gps_via_address(self, address):
        '''
        get gps info by address
        '''
        if not address:
            raise "invlid address"
        url = config.APIURL + address
        res = self.__get_data_from_tx_server(url, {})
        if res['status'] == 0:
            return (res['result']['location']['lng'], res['result']['location']['lat'])
        else:
            return False

    def get_distance_by_gps(self,src_gps=None,dest_gps=None):
        '''
        get distance between two locations.
        '''
        src_latitude,src_longitude = src_gps
        dest_latitude,dest_longitude = dest_gps

        url = config.DISTANCEURL
        params = {
            'from':str(src_latitude)+','+str(src_longitude),
            'to':str(dest_latitude)+','+str(dest_longitude)
        }
        res = self.__get_data_from_tx_server(url,params)
        # _logger.info(res)
        if res['status'] == 0:
            return res['result']['elements'][0]['distance']
        else:
            return False



if __name__ == "__main__":
    txmap = TxMap()
    # print(txmap.get_distance_by_gps((39.9219,116.44355),(39.922131184440,116.4488867887)))
    print(txmap.get_distance_by_gps((22.13151,113.54153),(22.133851,113.54153)))
