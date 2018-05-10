import da_ponz.utilities.api_tools as api_tools
import da_ponz.strategies.augmented_dickey_fuller as adf
import da_ponz.strategies.common_functions as common_functions
import da_ponz.utilities.logging_tools as logging_tools
import da_ponz.utilities.settings_tools as settings_tools
import da_ponz.strategies.ltsm as ltsm
import da_ponz.utilities.sql_tools as sql_tools
import itertools
import sys


def test_ltsm(columns_list, diff_data, engine, granularity, logger, raw_data, repeats, symbol):
    batches_list = [1, 2, 4]
    epochs_list = [500, 1000, 2000, 4000]
    neurons_list = [1, 2, 3, 4, 5]

    for item in itertools.product(batches_list, epochs_list, neurons_list):
        batches = item[0]
        epochs = item[1]
        neurons = item[2]
        scaler, test_scaled, train_scaled = ltsm.create_data_sets(batches, columns_list, diff_data)

        for i in range(1, repeats + 1):
            rmse = ltsm.calculate_rmse(batches, raw_data, epochs, neurons, scaler, test_scaled, train_scaled)
            message = '\nSymbol: {}\nGranularity: {}\nBatches: {}\nEpochs: {}\nNeurons: {}\n' \
                      'Test Number: {} of {}\nTest RMSE: {:.6}\n'.format(symbol, granularity, batches, epochs, neurons, i,
                                                                 repeats, rmse)
            logging_tools.log_event('info', logger, message)
            test_result = {'batches': batches, 'epochs': epochs, 'granularity': granularity, 'neurons': neurons,
                           'rmse': rmse, 'symbol': symbol, 'test_number': i, 'total_tests': repeats}
            table = sql_tools.get_table(engine, logger, 'ltsm_testing')
            insert = sql_tools.insert_data(engine, table, test_result)
            logging_tools.log_event(insert['result'], logger, insert['message'])


def persistence(column_list, data):
    df = common_functions.create_dataframe(column_list, data)
    split_point = int(df.shape[0] * .2)
    test = common_functions.create_split_data_sets(df, (slice(split_point, None), slice(None, None)))
    train = common_functions.create_split_data_sets(df, (slice(None, split_point), slice(None, None)))
    predictions = common_functions.make_persistence_prediction(test, train)
    history = {'loss': predictions, 'val_loss': test}
    rmse = common_functions.calculate_rmse(test, predictions)

    return history, rmse


# TODO: Coinbase Index (https://am.coinbase.com/index)


def setup_testing(engine, exchange, logger):
    columns_list = ['close', 'high', 'low', 'open', 'volume']
    granularity_list = [900, 3600]
    limit = 40
    repeats = 30
    symbols_list = api_tools.create_symbols_list(exchange, 'USD')

    for item in itertools.product(granularity_list, symbols_list):
        granularity = item[0]
        symbol = item[1]
        test_data = common_functions.get_test_data(columns_list, engine, granularity, logger, symbol, limit=limit)
        df = common_functions.create_dataframe(columns_list, test_data)
        adf_data = adf.run_test(df['close'])
        logging_tools.log_event(adf_data['result'], logger, adf_data['message'])

        if not adf_data['stationary']:
            diff_data = df.diff().dropna()

        else:
            diff_data = df

        #test_ltsm(['close'], diff_data, engine, granularity, logger, df, repeats, symbol)
        test_ltsm(columns_list, diff_data, engine, granularity, logger, df, repeats, symbol)


if __name__ == '__main__':
    settings = settings_tools.load_settings(sys.argv[1])
    exchange_id = 'gdax'
    api_settings = settings['api'][exchange_id]
    logger = logging_tools.create_logger(sys.argv[2])
    engine = sql_tools.create_engine(settings['mysql_connection'])
    exchange = api_tools.create_connection(exchange_id, api_settings)
    setup_testing(engine, exchange, logger)