import da_ponz.utilities.sql_tools as sql_tools
import numpy
import pandas
import sklearn.preprocessing as skl_pre


def build_scaler(feature_range, scaler_name, train):
    feature_range = tuple(feature_range)
    scaler_function = getattr(skl_pre, scaler_name)
    scaler = scaler_function(feature_range=feature_range)
    scaler.fit(train)

    return scaler


def calculate_yhat(data, output, scaler, test_scaled):
    yhat = []

    for i in range(output.shape[0]):
        inverted = invert_scale(scaler, test_scaled[i, 0:-1], output[i, 0])
        interval = test_scaled.shape[0] + 1 - i
        inverse_difference = inverted + data.values[-interval]
        yhat.append(inverse_difference)

    return yhat


def create_dataframe(columns_list, data, transpose=False):
    dataframe = pandas.DataFrame(data, columns=columns_list)

    if transpose:
        dataframe = dataframe.T

    return dataframe


def get_test_data(column_list, engine, granularity, logger, symbol, limit=None, table_name='testing_data'):
    table = sql_tools.get_table(engine, logger, table_name)
    order = {'field': 'utc_timestamp', 'direction': 'desc'}
    where = [table.c.symbol == symbol, table.c.timeframe == granularity]
    test_data = sql_tools.select_data(column_list, engine, table, where, limit=limit, order=order)

    return test_data


def invert_scale(scaler, X, yhat):
    new_row = [x for x in X] + [yhat]
    array = numpy.array(new_row)
    array = array.reshape(1, len(array))
    inverted = scaler.inverse_transform(array)[0, -1]

    return inverted


def make_data_supervised(column_list, df, output_var, dropnan=True, n_in=1, n_out=1):
    cols = []
    names = []

    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        names.extend(['{}(t-{})'.format(column_list[j], i) for j in range(len(column_list))])

    for i in range(0, n_out):
        cols.append(df[output_var].shift(-i))

        if i == 0:
            names.extend(['{}(t)'.format(output_var)])

        else:
            names.extend(['{}(t+{})'.format(output_var, i)])

    supervised_data = pandas.concat(cols, axis=1)
    supervised_data.columns = names

    if dropnan:
        supervised_data.dropna(inplace=True)

    return supervised_data


def make_persistence_prediction(test, train):
    history = [x for x in train]
    predictions = []

    for i in range(test.shape[0]):
        predictions.append(history[-1])
        history.append(test[i])

    return numpy.array(predictions)


def scale_data(data, scaler):
    data = data.reshape(data.shape[0], data.shape[1])
    scaled_data = scaler.transform(data)

    return scaled_data


def split_data_set(batch_size, data, slicer):
    data_set = data[slicer]
    size = data_set.shape[0]

    # Stateful networks require that the number of inputs be evenly divisible by the batch size.
    # Check if this is the case and if not, adjust the size of the data set.
    if not size % batch_size == 0:
        nearest_multiple = size - (size % batch_size)
        data_set = data_set[size - nearest_multiple:, :]

    return data_set