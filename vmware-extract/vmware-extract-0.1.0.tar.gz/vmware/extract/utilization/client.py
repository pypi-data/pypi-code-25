"""
#*===================================================================
#*
#* Licensed Materials - Property of IBM
#* IBM Cost And Asset Management
#* Copyright IBM Corporation 2017. All Rights Reserved.
#*
#*===================================================================
"""
from requests.exceptions import ConnectionError, ChunkedEncodingError, ReadTimeout, ConnectTimeout
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from vmware.extract.strings import VMware_strings
from vmware.extract import utils
from path import Path
import logging.config
import traceback
import requests
import datetime
import logging
import json
import os
import pika
from vmware.extract.serverinstance import ServerInstance as SI
import pytz
import pandas as pd
from time import strptime



class Client:
    logger = logging.getLogger('{}'.format(
        __name__
    ))

    def __init__(self, workdir, tempdir, ch, props, envextdir,run_by=None):
        self._workdir = workdir
        self._tempdir = tempdir
        self._settings = utils._load_yaml(
            'utilization/conf.yaml')  # TODO: change the hardcoded path if we place yaml in other directory
        self._dateformat = self._settings['dateformat']
        self._start_time = utils.now('%Y%m%d%H%M%S')
        self._ch = ch
        self._properties = props
        self.envextdir = Path(envextdir).makedirs_p()
        self._config = utils.load()
        self.deletetempfiles = self._config['vmware']['deletetempfiles']

        self.logger.info('Work Dir :' + self._workdir)
        self.logger.info('Temp Dir :' + self._tempdir)
        self.logger.info('Start time : ' + self._start_time)
        self.run_by = run_by

    def extract_utilization_files_vSphere_60(self, billingaccount, assetaccount, period):
        asset_account_number = assetaccount['asset_account_number']
        billing_account_number = billingaccount['billing_account_number']
        dt = datetime.datetime.now()  # store asset data only in current month folder
        ym = dt.strftime("%Y%m")
        y_m = dt.strftime('%Y-%m')
        ym_extdir = self.envextdir / ym / self._settings['provider'] / billing_account_number / asset_account_number
        ym_extdir.makedirs_p()
        si = SI(billingaccount['vserver'], billingaccount['username'], billingaccount['password'])
        self.publish_progress(utils.reply_body('utilization', billing_account_number, asset_account_number,
                                               VMware_strings.STATUS_EXTRACT_STARTED, y_m, "", "", ""),self.run_by)

        utilization_gpd_file = self.get_metrics_data(si, period, billingaccount, asset_account_number, False)

        # merge all pages data to single csv, and filter if any with regular expression :TODO explain below in README

        utilization_zipfilename = Path(
            ym_extdir / self._settings['gpdfileformat'].format(asset_account_number, self._start_time, 'csv.zip'))
        utilization_zip = utils.compress(utilization_zipfilename, utilization_gpd_file)

        if self.deletetempfiles:
            self.logger.debug("removing tempdir : %s", self._tempdir)
            utils.rmtree(self._tempdir)

        if utilization_gpd_file and utilization_zip:
            self.logger.info('Persisted Utilization data in file %s', utilization_zip)
            body = utils.reply_body('utilization', billing_account_number, asset_account_number,
                                    VMware_strings.STATUS_EXTRACT_COMPLETED, period,
                                    requests.codes.ok,
                                    VMware_strings.RESPONSE_SUCCESS, "")
            self.publish_progress(body,self.run_by)
            return utilization_zip
        else:
            self.logger.error('Failed to Persist utilization data for account', asset_account_number)
            body = utils.reply_body('utilization', billingaccount, asset_account_number,
                                    VMware_strings.STATUS_EXTRACT_FAILED, period,
                                    requests.codes.ok,
                                    VMware_strings.RESPONSE_SUCCESS, "")
            self.publish_progress(body,self.run_by)
            return None

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~GET METRICS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_metrics_data(self, si, period, billingaccount, asset_account_number,used_to_calculate_cost = False):
        # get start date of utilization report which is "period" months back
        # start_date = datetime.date.today() - relativedelta(months=period)  # TODO:This if currentdate - period month
        start_date = (datetime.datetime.utcnow() - relativedelta(months=period)).replace(
            day=1)  # TODO: This if currentdate - 1st of (period month)
        end_date = datetime.datetime.today()  # Till today
        self.logger.debug('start_date : %s  end_date : %s', start_date, end_date)
        asset_account_number = asset_account_number
        #TODO : remove hardcoded va;
        fieldnames = [
            'assetAccountId', 'providerAssetId', 'startTime',
            'endTime', 'minValue', 'maxValue', 'avgValue', 'unitOfMeasure']
        cols = self._settings['headers'].split()
        fn = Path(
            self._tempdir / self._settings['gpdfileformat'].format(asset_account_number, self._start_time, 'csv'))
        metrics_data = None
        metrics_url = ''
        try:
            # Get VM's for this subscription
            list_of_vms = si.get_registered_vms()
            perf_manager = si.get_performance_manager()
            counterInfo = {}
            #list of metrics we need
            metrics_required = ["cpu.usage.average","disk.maxTotalLatency.latest","net.usage.average","disk.usage.average"]
            metric_id_required = []
            # counterInfo will have UOM : CounterId mapping
            # for eg: counterInfo['percent']=4
            for c in perf_manager.perfCounter:
                metricUnit = c.unitInfo.key
                counterInfo[c.key] = metricUnit
                metric_name = c.groupInfo.key + "." + c.nameInfo.key + "." + c.rollupType
                self.logger.debug('Metric name and key mapping : '+ metric_name + "  "  + str(c.key))
                if metric_name in metrics_required :
                    self.logger.debug(c.groupInfo.key + "." + c.nameInfo.key + "." + c.rollupType+ " ==== " + str(c.key))
                    metric_id_required.append(c.key)

            newdf = pd.DataFrame()
            # Loop through all the VMs
            for vm in list_of_vms:
                self.logger.debug("Extracting Metrics data ......")
                # Get all available metric IDs for this VM
                available_perf_metric = si.get_available_performance_metric(vm)
                #list of counter IDs available
                counterIDs = [m.counterId for m in
                              available_perf_metric]

                #list of counter IDs we need based on metrics we need
                counterIDs_reqd = []
                for m_id in metric_id_required:
                    if m_id in counterIDs:
                        counterIDs_reqd.append(m_id)

                self.logger.debug('The list of counterIds for which usage data is derived : ')
                self.logger.debug(counterIDs_reqd)
                if not counterIDs_reqd:
                    continue
                # Using the IDs form a list of MetricId
                # objects for building the Query Spec
                metricIDs = [si.get_metric_ID(c)
                             for c in counterIDs_reqd]

                # Build the specification to be used
                # for querying the performance manager

                startDates = []
                currentday = datetime.datetime.utcnow().day

                for mo in range(period,-1,-1):
                    startDates.append(datetime.datetime.utcnow() - relativedelta(months=mo,days=currentday-1))

                spec_list = [si.get_query_spec(startDate, vm, metricIDs) for startDate in startDates]


                # spec = vim.PerformanceManager.QuerySpec(maxSample = 1,
                # entity=child,
                # metricId=metricIDs)
                # Query the performance manager
                # based on the metrics created above
                result=si.get_metric(spec_list)

                for metric_csv_entity in result:
                    timer_list_temp = []
                    timer_list = []
                    start_timer_list = []
                    end_timer_list = []
                    sample_info_csv = metric_csv_entity.sampleInfoCSV
                    metric_series_csv_list = metric_csv_entity.value
                    timer_list_temp = sample_info_csv.split(",")
                    timer_list = timer_list_temp[1::2]
                    start_timer_list = [(datetime.datetime.strptime(start_timer,'%Y-%m-%dT%H:%M:%SZ')) for start_timer in timer_list]
                    end_timer_list = [(startTimer + relativedelta(hours=1,minutes=59)) for startTimer in start_timer_list]


                    for metric_series_csv in metric_series_csv_list:
                        sampledf = pd.DataFrame()
                        value_list = metric_series_csv.value.split(",")
                        sampledf["startTime"] = start_timer_list
                        sampledf["endTime"] = end_timer_list
                        sampledf["avgValue"] = value_list
                        sampledf["maxValue"] = value_list
                        sampledf["minValue"] = value_list
                        sampledf["unitOfMeasure"] = counterInfo[metric_series_csv.id.counterId]
                        sampledf["assetAccountId"] = asset_account_number
                        sampledf["providerAssetId"] = vm.summary.config.instanceUuid
                        if used_to_calculate_cost:
                            sampledf["providerAssetName"] = vm.summary.config.name
                        newdf = newdf.append(sampledf)

            self.logger.debug("Completed Extracting utilization Data ")
            self.logger.debug("Converting utilization Data to GPD format")
            if used_to_calculate_cost:
                return newdf
            else:
                newdf.to_csv(fn, columns=cols, index=False)
                self.logger.info("GPD Usage Data loaded to csv")
                return fn
                self.logger.info('processing metrics data is complete')
        except (ConnectionError, ChunkedEncodingError, ReadTimeout, ConnectTimeout) as e:
            body = utils.reply_body('utilization', billingaccount, asset_account_number,
                                    VMware_strings.STATUS_EXTRACT_FAILED, '',
                                    '0', json.dumps(str(e)), "")
            self.publish_progress(body,self.run_by)
            self.logger.error('max tries exceeded, error getting metrics data from provider: %s', e)
            raise Exception('retry API call to provider failed : ', metrics_url)
        except Exception as ea:
            self.logger.error('error getting metrics data from provider: %s', ea)
            self.logger.error(traceback.format_exc())
            body = utils.reply_body('utilization', billingaccount, asset_account_number,
                                    VMware_strings.STATUS_EXTRACT_FAILED,
                                    '', '0', json.dumps(str(ea)), "")
            self.publish_progress(body,self.run_by)
            raise Exception('Error getting metrics data from provider:: ' + str(ea))




    def publish_progress(self, message,run_by=None):
        self.logger.debug('message to publish : %s', message)
        if run_by == 'cmd':
            self.logger.info(message)
        else:
            try:
                self.publish_message(message)
            except:  # on connection closed reconnect and publish the message again
                self.logger.info('Got exception when trying to publish message, reconnecting')
                self._ch = utils.create_connection()
                self.publish_message(message)

    def publish_message(self, message):
        self._ch.basic_publish(exchange='', routing_key=self._properties.reply_to,
                               properties=pika.BasicProperties(correlation_id=self._properties.correlation_id),
                               body=str(message))

    def get_columns(self, d):
        d1 = {}
        for k, v in d.iteritems():
            if v is not None:
                d1[k] = v
        d2 = {y: x for x, y in d1.iteritems()}  # Reverse key - values, this is needed when renaming columns
        self.logger.debug('headers %s, columns %s', d1, d2)
        return d1, d2

