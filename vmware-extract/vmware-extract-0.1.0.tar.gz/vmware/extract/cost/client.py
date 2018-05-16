"""
#*===================================================================
#*
#* Licensed Materials - Property of IBM
#* IBM Cost And Asset Management
#* Copyright IBM Corporation 2017. All Rights Reserved.
#*
#*===================================================================
"""

import requests
import logging
import datetime
from path import Path
from dateutil.relativedelta import relativedelta
import pika
from vmware.extract.strings import VMware_strings
import pandas as pd
import traceback
from vmware.extract import utils
from vmware.extract.utils import retry
from requests.exceptions import ConnectionError, ChunkedEncodingError,ReadTimeout,ConnectTimeout
from vmware.extract.utilization.client import Client as UtilizationClient
from vmware.extract.serverinstance import ServerInstance as SI
import json
from os import getenv


class CostClient:
    logger = logging.getLogger('{}'.format(__name__))

    def __init__(self, work_dir,tempdir, ch, properties, envextdir,run_by=None):
        self._settings = utils._load_yaml('cost/default.yaml')
        self._dateformat = self._settings['dateformat']
        self._workdir = work_dir
        self._tempdir = tempdir
        self._start_time = utils.now('%Y%m%d%H%M%S')    # This start_time will be used in extractdate
        self._extractdate = utils.now(self._dateformat)
        self._ch = ch
        self._properties = properties
        self.logger.info('Work Dir :' + self._workdir)
        self.logger.info('Temp Dir :' + self._tempdir)
        self.logger.info('Start time : ' + self._start_time)
        self.envextdir = Path(envextdir).makedirs_p()
        self._config = utils.load()
        self.deletetempfiles = self._config['vmware']['deletetempfiles']
        self.run_by=run_by

    def extract_cost_files(self, _account_number, creds, period):
        self.logger.info('Started extracting Utilization data for cost...')
        rate_card_type = None
        try:
            rate_card_config_dir = getenv('RATE_CARD_CONFIG_DIR')
            rate_card_config_file = utils._load_yaml(rate_card_config_dir + '/rate_card_config.yaml')
            rate_card_config = rate_card_config_file['rate_card']
            rate_card_type = rate_card_config_file['type']

            if rate_card_type == 'flat':
                self.calculate_cost_by_rate_card(_account_number, creds, period, rate_card_config, rate_card_config_dir)
            elif rate_card_type == 'complex':
                self.logger.info('Currently Type II is not supported..')
                # Todo: Type II rate card implementation need to be integrated here
            else:
                self.logger.info('There is no support for custom script as of now..')
                # Todo: Custom Script need to be integrated here
        except Exception as e:
            self.logger.exception('error while reading rate card file from config dir %s', traceback.format_exc())

    # Cost Calculation based on Flat Rate Card
    def calculate_cost_by_rate_card(self, _account_number, creds, period, rate_card_config, rate_card_config_dir):
        self.logger.info('Cost calculation started by using flat rate card..')
        billing_account = _account_number
        cost_account_id = creds['username']
        cost_prefix = self._settings['cost_prefix']

        self.logger.info(VMware_strings.START_COST_EXTRACT_ACCOUNT.format(_account_number))
        body = utils.reply_body('cost', _account_number, "", VMware_strings.STATUS_EXTRACT_STARTED, "", "", "", "")
        self.publish_progress(body, self.run_by)

        si = SI(creds['vserver'], creds['username'], creds['password'])
        usage_channel = ''
        if self.run_by != 'cmd':
            usage_channel = utils.create_connection()

        utilization_client = UtilizationClient(Path.getcwd(), Path(self._tempdir), usage_channel, self._properties,
                                               self.envextdir, self.run_by)
        # Getting utilization dataframe
        utilization_df = utilization_client.get_metrics_data(si, period, billing_account, cost_account_id, True)

        pc_provider_tax_cost = self._settings['cost_constants']['pc_provider_tax_cost']
        provider_final_bill_flag = self._settings['cost_constants']['provider_final_bill_flag']
        provider_name = self._settings['cost_constants']['provider']

        rate_card_file_name = rate_card_config[billing_account]
        self.logger.info('Rate card file for tenant %s is %s', billing_account, rate_card_file_name)
        if rate_card_file_name is not None or rate_card_file_name is not '':
            rate_card_data = json.load(open(rate_card_config_dir + '/' + rate_card_file_name, 'r'))

        for i1 in range(period, -1, -1):
            dt = datetime.datetime.now() - relativedelta(months=i1)
            ym = dt.strftime("%Y%m")
            y_m = dt.strftime('%Y-%m')

            ym_tempdir = self._tempdir / ym
            ym_tempdir.makedirs_p()
            ym_extdir = self.envextdir / ym / provider_name / _account_number
            ym_extdir.makedirs_p()

            self.logger.info(
                VMware_strings.START_COST_EXTRACT_MONTH.format(i1 + 1, period + 1, _account_number))
            body = utils.reply_body('cost', _account_number, "", VMware_strings.STATUS_EXTRACT_STARTED, y_m, "", "", "")
            self.publish_progress(body, self.run_by)

            new_df = pd.DataFrame()
            now = dt
            start_month = datetime.datetime(now.year, now.month, 1)
            end_month = start_month + relativedelta(months=1, days=0, hours=0, minutes=-1)
            start_month = datetime.datetime.strftime(start_month, self._dateformat)
            end_month = datetime.datetime.strftime(end_month, self._dateformat)

            cols = self._settings['headers'].split()
            asset_account_id_list = []
            provider_asset_id_list = []
            average_usage_list = []
            unit_of_measure_list = []
            start_date_list = []
            end_date_list = []
            asset_name_list = []
            unit_cost_list = []
            currency_list = []
            period_list = []
            provider_record_id_list = []
            total_cost_list = []
            description_list = []

            utilization_df_selected = utilization_df[
                (utilization_df.startTime >= start_month) & (utilization_df.startTime <= end_month)]
            self.logger.debug("Utilization Data frame Size :::: %s ", str(len(utilization_df_selected)))
            if len(utilization_df_selected) == 0:
                self.logger.info("Cost can not be calculated since there is no utilization data available for the month"
                                 "%s :: ", ym)
            else:
                for index, row in utilization_df_selected.iterrows():

                    asset_account_id_list.append(row['assetAccountId'])
                    provider_asset_id_list.append(row['providerAssetId'])
                    average_usage_list.append(row['avgValue'])
                    unit_of_measure_list.append(row['unitOfMeasure'])

                    period_list.append(ym)
                    start_date_str = str(row['startTime']).split(' ')[0].split('-')
                    provider_record_data = start_date_str[0] + start_date_str[1] + start_date_str[2]
                    provider_record_id_list.append(provider_record_data)

                    start_date_list.append(row['startTime'])
                    end_date_list.append(row['endTime'])
                    asset_name_list.append(row['providerAssetName'])

                    if row['unitOfMeasure'] == 'percent':
                        usage_data_duration_type = self._settings['cost_constants']['usage_data_duration_type']
                        unit_cost = self.get_unit_cost_from_rate_card(rate_card_data,
                                                                      self._settings['cost_constants'][
                                                                          'policy_type_compute'],
                                                                      self._settings['cost_constants'][
                                                                          'unit_of_measure_per_vcpu'])

                        unit_cost = (unit_cost / 24) * usage_data_duration_type
                        total_cost_list.append(unit_cost * float(row['avgValue']))
                        unit_cost_list.append(unit_cost)

                        currency = self.get_currency_from_rate_card(rate_card_data,
                                                                    self._settings['cost_constants'][
                                                                        'policy_type_compute'],
                                                                    self._settings['cost_constants'][
                                                                        'unit_of_measure_per_vcpu'])
                        description = self.get_description_from_rate_card(rate_card_data,
                                                                    self._settings['cost_constants'][
                                                                        'policy_type_compute'],
                                                                    self._settings['cost_constants'][
                                                                        'unit_of_measure_per_vcpu'])
                        currency_list.append(currency)
                        description_list.append(description)
                    else:
                        unit_cost = self._settings['cost_constants']['default_unit_cost']
                        unit_cost_list.append(unit_cost)
                        currency = self._settings['cost_constants']['default_currency']
                        total_cost = self._settings['cost_constants']['default_total_cost']
                        total_cost_list.append(total_cost)
                        description = self._settings['cost_constants']['default_description']
                        currency_list.append(currency)
                        description_list.append(description)

                new_df["period"] = period_list
                new_df["providerRecordId"] = provider_record_id_list
                new_df["extractDate"] = self._extractdate
                new_df['invoiceStartDate'] = start_date_list
                new_df['invoiceEndDate'] = end_date_list
                new_df['providerFinalBillFlag'] = provider_final_bill_flag
                new_df['pcProviderTaxCost'] = pc_provider_tax_cost
                new_df["providerName"] = provider_name
                new_df["assetAccountId"] = asset_account_id_list
                new_df["billingAccountId"] = billing_account
                new_df["assetName"] = asset_name_list
                new_df["providerAssetId"] = provider_asset_id_list
                new_df["quantity"] = average_usage_list
                new_df["description"] = description_list
                new_df["unitOfMeasure"] = unit_of_measure_list
                new_df["providerCurrency"] = currency_list
                new_df["pcProviderUnitCost"] = unit_cost_list
                new_df["customerCurrency"] = currency_list
                new_df['customerConversionRate'] = self._settings['cost_constants']['customer_conversion_rate']
                new_df['pcCustomerUnitCost'] = unit_cost_list
                new_df['pcCustomerTotalCost'] = total_cost_list
                new_df['pcProviderTotalCost'] = total_cost_list
                new_df['attributes'] = ''
                cost_gpd_file = Path(ym_tempdir) / 'C_{}_{}.csv'.format(cost_account_id, self._start_time)
                new_df.to_csv(cost_gpd_file, columns=cols, index=False)
                cost_zip_file_name = Path(ym_extdir) / '{}_{}_{}.csv.zip'.format(cost_prefix, cost_account_id,
                                                                                 self._start_time)
                cost_zip = utils.compress(cost_zip_file_name, cost_gpd_file)

        if self.deletetempfiles:
            self.logger.debug("removing tempdir : %s", self._tempdir)
            utils.rmtree(self._tempdir)
        if cost_gpd_file and cost_zip:
            self.logger.info('Persisted cost data for account %s, in file %s', cost_account_id, cost_zip)
        else:
            self.logger.info('Failed to persist cost data for account %s ', cost_account_id)

    @retry((ConnectionError, ChunkedEncodingError, ReadTimeout, ConnectTimeout), tries=8, delay=1, backoff=2, logger=logger)
    def connect_vmware(self, url, headers, isjson_resp):
        self.logger.info('Connecting to provider %s', url)
        try:
            q_response = requests.get(url, headers=headers)
            if isjson_resp == 'true':
                output = q_response.json()
            else:
                output = q_response.content
            if q_response.status_code is not None and q_response.status_code != requests.codes.ok: #TODO do we need to check for other codes like created, accepted
                self.logger.error('response code  is %d and q_response is %s', q_response.status_code, output)
                return q_response
            return output
        except Exception as e:
            raise

    """
            get unit cost from rate card
    """

    def get_unit_cost_from_rate_card(self, rate_card_json_data, policy_type, unit_of_measure):
        try:
            if rate_card_json_data is None:
                raise Exception('Empty Rate Card..')
            for data in rate_card_json_data:
                if data['policy_type'] == policy_type and data['unit_of_measure'] == \
                        unit_of_measure:
                    return data['unit_cost']
        except Exception as e:
            self.logger.exception('Exception while reading currency from rate card %s', traceback.format_exc())

    """
        get currency from the rate card
    """

    def get_currency_from_rate_card(self, rate_card_json_data, policy_type, unit_of_measure):
        try:
            if rate_card_json_data is None:
                raise Exception('Empty Rate Card..')
            for data in rate_card_json_data:
                if data['policy_type'] == policy_type and data['unit_of_measure'] == \
                        unit_of_measure:
                    return data['currency']
        except Exception as e:
            self.logger.exception('Exception while reading currency from rate card %s', traceback.format_exc())

    """
        get description from the rate card
    """
    def get_description_from_rate_card(self, rate_card_json_data, policy_type, unit_of_measure):
        try:
            if rate_card_json_data is None:
                raise Exception('Empty Rate Card..')
            for data in rate_card_json_data:
                if data['policy_type'] == policy_type and data['unit_of_measure'] == \
                        unit_of_measure:
                    return data['description']
        except Exception as e:
            self.logger.exception('Exception while reading currency from rate card %s', traceback.format_exc())

    def publish_progress(self, message,run_by=None):
        self.logger.debug('message to publish : %s', message)
        if run_by == 'cmd':
            self.logger.info(message)
        else:
            try:
                self.publish_message(message)
            except: # on connection closed reconnect and publish the message again
                self.logger.info('Got exception when trying to publish message, reconnecting')
                self._ch = utils.create_connection()
                self.publish_message(message)

    def publish_message(self, message):
        self._ch.basic_publish(exchange='', routing_key=self._properties.reply_to,
            properties=pika.BasicProperties(correlation_id=self._properties.correlation_id),body=str(message))