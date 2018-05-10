import ccxt
import da_ponz.utilities.api_tools as api_tools
import datetime


def create_order_result_dict(exchange_name, order):
    amount = float(order['size'])
    created_at = datetime.datetime.strptime(order['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
    fees = float(order['fill_fees'])
    price = float(order['executed_value']) / amount
    subtotal = float(order['executed_value'])
    table = order['side'] + '_orders'

    if table == 'buy_orders':
        total = subtotal + fees

    else:
        total = subtotal - fees

    order_result_dict = {'table': table,
                         'order': {'amount': amount, 'created_at': created_at, 'exchange': exchange_name,
                         'fees': fees, 'id': order['id'], 'price': price, 'settled': order['settled'],
                         'subtotal': subtotal, 'symbol': order['product_id'], 'total': total, 'type': order['type']}}

    return order_result_dict


def fund_account(amount, currency, exchange, settings, type):
    if type == 'deposit':
        params = {'coinbase_account_id': settings['external_wallet_id']['incoming_account_id']}

    else:
        params = {'payment_method_id': settings['external_wallet_id']['outgoing_account_id']}

    destination = settings['internal_wallet_id']

    api_tools.fund_account(amount, currency, destination, exchange, type, params=params)


def submit_order(amount, exchange, side, symbol, type, price=None):
    order_variables = [symbol, type, side, amount]

    if type == 'limit':
        order_variables.append(price)

    try:
        order = exchange.create_order(*order_variables)['info']

    except ccxt.InsufficientFunds:
        data = {'result': 'error',
                'message': '{} {} request for {} {} on {} has failed due to insufficient funds.'.
                    format(type, side, amount, symbol, exchange.name)}

    else:
        for i in range(5):
            if not order['settled']:
                order = api_tools.update_order(exchange, order['id'])

            else:
                break

        order_result_dict = create_order_result_dict(exchange.name, order)
        data = {'result': 'info',
                'message': order_result_dict}

    return data