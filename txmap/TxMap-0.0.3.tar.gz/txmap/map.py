
import config
import requests


class TxMap(object):

    def __get_data_from_tx_server(self, url, param):
        param['key'] = config.APIKEY
        res = requests.get(url, param)
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
        if res['status'] == 0:
            return res['result']['distance']
        else:
            return False



if __name__ == "__main__":
    txmap = TxMap()
    print(txmap.get_distance_by_gps((39.9219,116.44355),(39.922131184440,116.4488867887)))
    # print(txmap.get_gps_via_address('广东省深圳市布吉街道中兴路金运家园1栋128号'))
