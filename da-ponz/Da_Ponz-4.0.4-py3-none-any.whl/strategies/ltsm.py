import da_ponz.strategies.common_functions as common_functions
import keras
import math
import sklearn.metrics as skl_met


def calculate_rmse(batch_size, data, epochs, neuron, scaler, test_scaled, train_scaled):
    model = create_model(batch_size, epochs, neuron, train_scaled)
    train_reshaped = train_scaled[:, :-1].reshape(train_scaled.shape[0], 1, train_scaled.shape[1] - 1)
    model.predict(train_reshaped, batch_size=batch_size)
    test_reshaped = test_scaled[:, :-1].reshape(test_scaled.shape[0], 1, test_scaled.shape[1] - 1)
    output = model.predict(test_reshaped, batch_size=batch_size)
    predictions = common_functions.calculate_yhat(data, output, scaler, test_scaled)
    rmse = math.sqrt(skl_met.mean_squared_error(data[-len(predictions):], predictions))

    return rmse


def create_data_sets(batch_size, columns_list, diff_data):
    supervised_data = common_functions.make_data_supervised(columns_list, diff_data, output_var='close')
    split_point = int(round(supervised_data.shape[0] * .333))
    test = common_functions.split_data_set(batch_size, supervised_data.values, slice(-split_point, None))
    train = common_functions.split_data_set(batch_size, supervised_data.values, slice(0, -split_point))
    scaler = common_functions.build_scaler((-1, 1), 'MinMaxScaler', train)
    test_scaled = common_functions.scale_data(test, scaler)
    train_scaled = common_functions.scale_data(train, scaler)

    return scaler, test_scaled, train_scaled


def create_model(batch_size, nb_epoch, neurons, train):
    X = train[:, :-1]  # Drops the last column, which has the output_var
    X = X.reshape((X.shape[0], 1, X.shape[1]))
    y = train[:, -1]  # Keeps the last column

    model = keras.Sequential()
    model.add(keras.layers.LSTM(neurons, batch_input_shape=(batch_size, X.shape[1], X.shape[2]), stateful=True))
    model.add(keras.layers.Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')

    for i in range(nb_epoch):
        model.fit(X, y, batch_size=batch_size, epochs=1, shuffle=False, verbose=0)
        model.reset_states()

    return model