from tempo_client.client import TempoClient
import pprint
import iso8601


ACCESS_TOKEN = '0rWhw0M0JzcF9K5yK4p3zoIBQohYGn'
JIRA_INSTANCE = 'pwitab'

if __name__ == "__main__":

    client = TempoClient(access_token=ACCESS_TOKEN)

    ac = client.get_account_worklogs(account_key='EON_E-LIVE',
                                     start=iso8601.parse_date('2018-03-01'),
                                     stop=iso8601.parse_date('2018-03-30'))

    pprint.pprint(ac)


