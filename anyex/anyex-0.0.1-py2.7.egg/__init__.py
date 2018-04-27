# -*- coding: utf-8 -*-

"""anyex: CryptoCurrency eXchange Trading Library"""

# MIT License
# Copyright (c) 2017 Igor Kroitor
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# ----------------------------------------------------------------------------

__version__ = '0.0.1'

# ----------------------------------------------------------------------------

from anyex.base.exchange import Exchange                     # noqa: F401

from anyex.base.decimal_to_precision import decimal_to_precision  # noqa: F401
from anyex.base.decimal_to_precision import TRUNCATE              # noqa: F401
from anyex.base.decimal_to_precision import ROUND                 # noqa: F401
from anyex.base.decimal_to_precision import DECIMAL_PLACES        # noqa: F401
from anyex.base.decimal_to_precision import SIGNIFICANT_DIGITS    # noqa: F401
from anyex.base.decimal_to_precision import NO_PADDING            # noqa: F401
from anyex.base.decimal_to_precision import PAD_WITH_ZERO         # noqa: F401

from anyex.base import errors                                # noqa: F401
from anyex.base.errors import BaseError                      # noqa: F401
from anyex.base.errors import ExchangeError                  # noqa: F401
from anyex.base.errors import NotSupported                   # noqa: F401
from anyex.base.errors import AuthenticationError            # noqa: F401
from anyex.base.errors import PermissionDenied               # noqa: F401
from anyex.base.errors import InvalidNonce                   # noqa: F401
from anyex.base.errors import InsufficientFunds              # noqa: F401
from anyex.base.errors import InvalidOrder                   # noqa: F401
from anyex.base.errors import OrderNotFound                  # noqa: F401
from anyex.base.errors import OrderNotCached                 # noqa: F401
from anyex.base.errors import CancelPending                  # noqa: F401
from anyex.base.errors import NetworkError                   # noqa: F401
from anyex.base.errors import DDoSProtection                 # noqa: F401
from anyex.base.errors import RequestTimeout                 # noqa: F401
from anyex.base.errors import ExchangeNotAvailable           # noqa: F401
from anyex.base.errors import InvalidAddress                 # noqa: F401

from anyex._1broker import _1broker                          # noqa: F401
from anyex._1btcxe import _1btcxe                            # noqa: F401
from anyex.acx import acx                                    # noqa: F401
from anyex.allcoin import allcoin                            # noqa: F401
from anyex.anxpro import anxpro                              # noqa: F401
from anyex.bibox import bibox                                # noqa: F401
from anyex.binance import binance                            # noqa: F401
from anyex.bit2c import bit2c                                # noqa: F401
from anyex.bitbank import bitbank                            # noqa: F401
from anyex.bitbay import bitbay                              # noqa: F401
from anyex.bitfinex import bitfinex                          # noqa: F401
from anyex.bitfinex2 import bitfinex2                        # noqa: F401
from anyex.bitflyer import bitflyer                          # noqa: F401
from anyex.bithumb import bithumb                            # noqa: F401
from anyex.bitkk import bitkk                                # noqa: F401
from anyex.bitlish import bitlish                            # noqa: F401
from anyex.bitmarket import bitmarket                        # noqa: F401
from anyex.bitmex import bitmex                              # noqa: F401
from anyex.bitso import bitso                                # noqa: F401
from anyex.bitstamp import bitstamp                          # noqa: F401
from anyex.bitstamp1 import bitstamp1                        # noqa: F401
from anyex.bittrex import bittrex                            # noqa: F401
from anyex.bitz import bitz                                  # noqa: F401
from anyex.bl3p import bl3p                                  # noqa: F401
from anyex.bleutrade import bleutrade                        # noqa: F401
from anyex.braziliex import braziliex                        # noqa: F401
from anyex.btcbox import btcbox                              # noqa: F401
from anyex.btcchina import btcchina                          # noqa: F401
from anyex.btcexchange import btcexchange                    # noqa: F401
from anyex.btcmarkets import btcmarkets                      # noqa: F401
from anyex.btctradeim import btctradeim                      # noqa: F401
from anyex.btctradeua import btctradeua                      # noqa: F401
from anyex.btcturk import btcturk                            # noqa: F401
from anyex.btcx import btcx                                  # noqa: F401
from anyex.bxinth import bxinth                              # noqa: F401
from anyex.ccex import ccex                                  # noqa: F401
from anyex.cex import cex                                    # noqa: F401
from anyex.chbtc import chbtc                                # noqa: F401
from anyex.chilebit import chilebit                          # noqa: F401
from anyex.cobinhood import cobinhood                        # noqa: F401
from anyex.coincheck import coincheck                        # noqa: F401
from anyex.coinegg import coinegg                            # noqa: F401
from anyex.coinex import coinex                              # noqa: F401
from anyex.coinexchange import coinexchange                  # noqa: F401
from anyex.coinfloor import coinfloor                        # noqa: F401
from anyex.coingi import coingi                              # noqa: F401
from anyex.coinmarketcap import coinmarketcap                # noqa: F401
from anyex.coinmate import coinmate                          # noqa: F401
from anyex.coinnest import coinnest                          # noqa: F401
from anyex.coinone import coinone                            # noqa: F401
from anyex.coinsecure import coinsecure                      # noqa: F401
from anyex.coinspot import coinspot                          # noqa: F401
from anyex.coolcoin import coolcoin                          # noqa: F401
from anyex.cryptopia import cryptopia                        # noqa: F401
from anyex.dsx import dsx                                    # noqa: F401
from anyex.ethfinex import ethfinex                          # noqa: F401
from anyex.exmo import exmo                                  # noqa: F401
from anyex.exx import exx                                    # noqa: F401
from anyex.flowbtc import flowbtc                            # noqa: F401
from anyex.foxbit import foxbit                              # noqa: F401
from anyex.fybse import fybse                                # noqa: F401
from anyex.fybsg import fybsg                                # noqa: F401
from anyex.gatecoin import gatecoin                          # noqa: F401
from anyex.gateio import gateio                              # noqa: F401
from anyex.gdax import gdax                                  # noqa: F401
from anyex.gemini import gemini                              # noqa: F401
from anyex.getbtc import getbtc                              # noqa: F401
from anyex.hadax import hadax                                # noqa: F401
from anyex.hitbtc import hitbtc                              # noqa: F401
from anyex.hitbtc2 import hitbtc2                            # noqa: F401
from anyex.huobi import huobi                                # noqa: F401
from anyex.huobicny import huobicny                          # noqa: F401
from anyex.huobipro import huobipro                          # noqa: F401
from anyex.ice3x import ice3x                                # noqa: F401
from anyex.independentreserve import independentreserve      # noqa: F401
from anyex.indodax import indodax                            # noqa: F401
from anyex.itbit import itbit                                # noqa: F401
from anyex.jubi import jubi                                  # noqa: F401
from anyex.kraken import kraken                              # noqa: F401
from anyex.kucoin import kucoin                              # noqa: F401
from anyex.kuna import kuna                                  # noqa: F401
from anyex.lakebtc import lakebtc                            # noqa: F401
from anyex.lbank import lbank                                # noqa: F401
from anyex.liqui import liqui                                # noqa: F401
from anyex.livecoin import livecoin                          # noqa: F401
from anyex.luno import luno                                  # noqa: F401
from anyex.lykke import lykke                                # noqa: F401
from anyex.mercado import mercado                            # noqa: F401
from anyex.mixcoins import mixcoins                          # noqa: F401
from anyex.negociecoins import negociecoins                  # noqa: F401
from anyex.nova import nova                                  # noqa: F401
from anyex.okcoincny import okcoincny                        # noqa: F401
from anyex.okcoinusd import okcoinusd                        # noqa: F401
from anyex.okex import okex                                  # noqa: F401
from anyex.paymium import paymium                            # noqa: F401
from anyex.poloniex import poloniex                          # noqa: F401
from anyex.qryptos import qryptos                            # noqa: F401
from anyex.quadrigacx import quadrigacx                      # noqa: F401
from anyex.quoinex import quoinex                            # noqa: F401
from anyex.southxchange import southxchange                  # noqa: F401
from anyex.surbitcoin import surbitcoin                      # noqa: F401
from anyex.therock import therock                            # noqa: F401
from anyex.tidebit import tidebit                            # noqa: F401
from anyex.tidex import tidex                                # noqa: F401
from anyex.urdubit import urdubit                            # noqa: F401
from anyex.vaultoro import vaultoro                          # noqa: F401
from anyex.vbtc import vbtc                                  # noqa: F401
from anyex.virwox import virwox                              # noqa: F401
from anyex.wex import wex                                    # noqa: F401
from anyex.xbtce import xbtce                                # noqa: F401
from anyex.yobit import yobit                                # noqa: F401
from anyex.yunbi import yunbi                                # noqa: F401
from anyex.zaif import zaif                                  # noqa: F401
from anyex.zb import zb                                      # noqa: F401

exchanges = [
    '_1broker',
    '_1btcxe',
    'acx',
    'allcoin',
    'anxpro',
    'bibox',
    'binance',
    'bit2c',
    'bitbank',
    'bitbay',
    'bitfinex',
    'bitfinex2',
    'bitflyer',
    'bithumb',
    'bitkk',
    'bitlish',
    'bitmarket',
    'bitmex',
    'bitso',
    'bitstamp',
    'bitstamp1',
    'bittrex',
    'bitz',
    'bl3p',
    'bleutrade',
    'braziliex',
    'btcbox',
    'btcchina',
    'btcexchange',
    'btcmarkets',
    'btctradeim',
    'btctradeua',
    'btcturk',
    'btcx',
    'bxinth',
    'ccex',
    'cex',
    'chbtc',
    'chilebit',
    'cobinhood',
    'coincheck',
    'coinegg',
    'coinex',
    'coinexchange',
    'coinfloor',
    'coingi',
    'coinmarketcap',
    'coinmate',
    'coinnest',
    'coinone',
    'coinsecure',
    'coinspot',
    'coolcoin',
    'cryptopia',
    'dsx',
    'ethfinex',
    'exmo',
    'exx',
    'flowbtc',
    'foxbit',
    'fybse',
    'fybsg',
    'gatecoin',
    'gateio',
    'gdax',
    'gemini',
    'getbtc',
    'hadax',
    'hitbtc',
    'hitbtc2',
    'huobi',
    'huobicny',
    'huobipro',
    'ice3x',
    'independentreserve',
    'indodax',
    'itbit',
    'jubi',
    'kraken',
    'kucoin',
    'kuna',
    'lakebtc',
    'lbank',
    'liqui',
    'livecoin',
    'luno',
    'lykke',
    'mercado',
    'mixcoins',
    'negociecoins',
    'nova',
    'okcoincny',
    'okcoinusd',
    'okex',
    'paymium',
    'poloniex',
    'qryptos',
    'quadrigacx',
    'quoinex',
    'southxchange',
    'surbitcoin',
    'therock',
    'tidebit',
    'tidex',
    'urdubit',
    'vaultoro',
    'vbtc',
    'virwox',
    'wex',
    'xbtce',
    'yobit',
    'yunbi',
    'zaif',
    'zb',
]

base = [
    'Exchange',
    'exchanges',
    'decimal_to_precision',
]

__all__ = base + errors.__all__ + exchanges
