# -*- coding: utf-8 -*-

"""anyex: CryptoCurrency eXchange Trading Library (Async)"""

# -----------------------------------------------------------------------------

__version__ = '0.0.1'

# -----------------------------------------------------------------------------

from anyex.async.base.exchange import Exchange                   # noqa: F401

from anyex.base.decimal_to_precision import decimal_to_precision  # noqa: F401
from anyex.base.decimal_to_precision import TRUNCATE              # noqa: F401
from anyex.base.decimal_to_precision import ROUND                 # noqa: F401
from anyex.base.decimal_to_precision import DECIMAL_PLACES        # noqa: F401
from anyex.base.decimal_to_precision import SIGNIFICANT_DIGITS    # noqa: F401
from anyex.base.decimal_to_precision import NO_PADDING            # noqa: F401
from anyex.base.decimal_to_precision import PAD_WITH_ZERO         # noqa: F401

from anyex.base import errors                                    # noqa: F401
from anyex.base.errors import BaseError                          # noqa: F401
from anyex.base.errors import ExchangeError                      # noqa: F401
from anyex.base.errors import NotSupported                       # noqa: F401
from anyex.base.errors import AuthenticationError                # noqa: F401
from anyex.base.errors import PermissionDenied                   # noqa: F401
from anyex.base.errors import InvalidNonce                       # noqa: F401
from anyex.base.errors import InsufficientFunds                  # noqa: F401
from anyex.base.errors import InvalidOrder                       # noqa: F401
from anyex.base.errors import OrderNotFound                      # noqa: F401
from anyex.base.errors import OrderNotCached                     # noqa: F401
from anyex.base.errors import CancelPending                      # noqa: F401
from anyex.base.errors import NetworkError                       # noqa: F401
from anyex.base.errors import DDoSProtection                     # noqa: F401
from anyex.base.errors import RequestTimeout                     # noqa: F401
from anyex.base.errors import ExchangeNotAvailable               # noqa: F401
from anyex.base.errors import InvalidAddress                     # noqa: F401

from anyex.async._1broker import _1broker                        # noqa: F401
from anyex.async._1btcxe import _1btcxe                          # noqa: F401
from anyex.async.acx import acx                                  # noqa: F401
from anyex.async.allcoin import allcoin                          # noqa: F401
from anyex.async.anxpro import anxpro                            # noqa: F401
from anyex.async.bibox import bibox                              # noqa: F401
from anyex.async.binance import binance                          # noqa: F401
from anyex.async.bit2c import bit2c                              # noqa: F401
from anyex.async.bitbank import bitbank                          # noqa: F401
from anyex.async.bitbay import bitbay                            # noqa: F401
from anyex.async.bitfinex import bitfinex                        # noqa: F401
from anyex.async.bitfinex2 import bitfinex2                      # noqa: F401
from anyex.async.bitflyer import bitflyer                        # noqa: F401
from anyex.async.bithumb import bithumb                          # noqa: F401
from anyex.async.bitkk import bitkk                              # noqa: F401
from anyex.async.bitlish import bitlish                          # noqa: F401
from anyex.async.bitmarket import bitmarket                      # noqa: F401
from anyex.async.bitmex import bitmex                            # noqa: F401
from anyex.async.bitso import bitso                              # noqa: F401
from anyex.async.bitstamp import bitstamp                        # noqa: F401
from anyex.async.bitstamp1 import bitstamp1                      # noqa: F401
from anyex.async.bittrex import bittrex                          # noqa: F401
from anyex.async.bitz import bitz                                # noqa: F401
from anyex.async.bl3p import bl3p                                # noqa: F401
from anyex.async.bleutrade import bleutrade                      # noqa: F401
from anyex.async.braziliex import braziliex                      # noqa: F401
from anyex.async.btcbox import btcbox                            # noqa: F401
from anyex.async.btcchina import btcchina                        # noqa: F401
from anyex.async.btcexchange import btcexchange                  # noqa: F401
from anyex.async.btcmarkets import btcmarkets                    # noqa: F401
from anyex.async.btctradeim import btctradeim                    # noqa: F401
from anyex.async.btctradeua import btctradeua                    # noqa: F401
from anyex.async.btcturk import btcturk                          # noqa: F401
from anyex.async.btcx import btcx                                # noqa: F401
from anyex.async.bxinth import bxinth                            # noqa: F401
from anyex.async.ccex import ccex                                # noqa: F401
from anyex.async.cex import cex                                  # noqa: F401
from anyex.async.chbtc import chbtc                              # noqa: F401
from anyex.async.chilebit import chilebit                        # noqa: F401
from anyex.async.cobinhood import cobinhood                      # noqa: F401
from anyex.async.coincheck import coincheck                      # noqa: F401
from anyex.async.coinegg import coinegg                          # noqa: F401
from anyex.async.coinex import coinex                            # noqa: F401
from anyex.async.coinexchange import coinexchange                # noqa: F401
from anyex.async.coinfloor import coinfloor                      # noqa: F401
from anyex.async.coingi import coingi                            # noqa: F401
from anyex.async.coinmarketcap import coinmarketcap              # noqa: F401
from anyex.async.coinmate import coinmate                        # noqa: F401
from anyex.async.coinnest import coinnest                        # noqa: F401
from anyex.async.coinone import coinone                          # noqa: F401
from anyex.async.coinsecure import coinsecure                    # noqa: F401
from anyex.async.coinspot import coinspot                        # noqa: F401
from anyex.async.coolcoin import coolcoin                        # noqa: F401
from anyex.async.cryptopia import cryptopia                      # noqa: F401
from anyex.async.dsx import dsx                                  # noqa: F401
from anyex.async.ethfinex import ethfinex                        # noqa: F401
from anyex.async.exmo import exmo                                # noqa: F401
from anyex.async.exx import exx                                  # noqa: F401
from anyex.async.flowbtc import flowbtc                          # noqa: F401
from anyex.async.foxbit import foxbit                            # noqa: F401
from anyex.async.fybse import fybse                              # noqa: F401
from anyex.async.fybsg import fybsg                              # noqa: F401
from anyex.async.gatecoin import gatecoin                        # noqa: F401
from anyex.async.gateio import gateio                            # noqa: F401
from anyex.async.gdax import gdax                                # noqa: F401
from anyex.async.gemini import gemini                            # noqa: F401
from anyex.async.getbtc import getbtc                            # noqa: F401
from anyex.async.hadax import hadax                              # noqa: F401
from anyex.async.hitbtc import hitbtc                            # noqa: F401
from anyex.async.hitbtc2 import hitbtc2                          # noqa: F401
from anyex.async.huobi import huobi                              # noqa: F401
from anyex.async.huobicny import huobicny                        # noqa: F401
from anyex.async.huobipro import huobipro                        # noqa: F401
from anyex.async.ice3x import ice3x                              # noqa: F401
from anyex.async.independentreserve import independentreserve    # noqa: F401
from anyex.async.indodax import indodax                          # noqa: F401
from anyex.async.itbit import itbit                              # noqa: F401
from anyex.async.jubi import jubi                                # noqa: F401
from anyex.async.kraken import kraken                            # noqa: F401
from anyex.async.kucoin import kucoin                            # noqa: F401
from anyex.async.kuna import kuna                                # noqa: F401
from anyex.async.lakebtc import lakebtc                          # noqa: F401
from anyex.async.lbank import lbank                              # noqa: F401
from anyex.async.liqui import liqui                              # noqa: F401
from anyex.async.livecoin import livecoin                        # noqa: F401
from anyex.async.luno import luno                                # noqa: F401
from anyex.async.lykke import lykke                              # noqa: F401
from anyex.async.mercado import mercado                          # noqa: F401
from anyex.async.mixcoins import mixcoins                        # noqa: F401
from anyex.async.negociecoins import negociecoins                # noqa: F401
from anyex.async.nova import nova                                # noqa: F401
from anyex.async.okcoincny import okcoincny                      # noqa: F401
from anyex.async.okcoinusd import okcoinusd                      # noqa: F401
from anyex.async.okex import okex                                # noqa: F401
from anyex.async.paymium import paymium                          # noqa: F401
from anyex.async.poloniex import poloniex                        # noqa: F401
from anyex.async.qryptos import qryptos                          # noqa: F401
from anyex.async.quadrigacx import quadrigacx                    # noqa: F401
from anyex.async.quoinex import quoinex                          # noqa: F401
from anyex.async.southxchange import southxchange                # noqa: F401
from anyex.async.surbitcoin import surbitcoin                    # noqa: F401
from anyex.async.therock import therock                          # noqa: F401
from anyex.async.tidebit import tidebit                          # noqa: F401
from anyex.async.tidex import tidex                              # noqa: F401
from anyex.async.urdubit import urdubit                          # noqa: F401
from anyex.async.vaultoro import vaultoro                        # noqa: F401
from anyex.async.vbtc import vbtc                                # noqa: F401
from anyex.async.virwox import virwox                            # noqa: F401
from anyex.async.wex import wex                                  # noqa: F401
from anyex.async.xbtce import xbtce                              # noqa: F401
from anyex.async.yobit import yobit                              # noqa: F401
from anyex.async.yunbi import yunbi                              # noqa: F401
from anyex.async.zaif import zaif                                # noqa: F401
from anyex.async.zb import zb                                    # noqa: F401

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
