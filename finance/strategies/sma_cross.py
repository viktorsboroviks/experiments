'''
SMA cross strategy.
'''

import typing
import talib as ta
import vfin
import vfin_ops
import vtime


class SmaCrossOpGen(vfin_ops.TradingOpGen):
    '''
    Generate an operation sequence for an SMA cross trading strategy.

    Long:
        Enter when fast SMA is above slow SMA.
        Exit when fast SMA is below slow SMA.

    Short:
        Enter when fast SMA is below slow SMA.
        Exit when fast SMA is above slow SMA.

    SMA coefficients for Long and Short may differ.
    '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 coefs: dict[str, int],
                 initial_cash: typing.Union[int, float],
                 add_cash: typing.Union[int, float] = 0,
                 add_cash_alarm: typing.Union[str, vtime.Alarm] = None,
                 price_info: vfin.InstrumentInfo = None):
        '''
        Init.

        Args:
            coefs: int SMA coefficients, allowed keys are:
                'long_entry_fast_sma',
                'long_entry_slow_sma',
                'long_exit_fast_sma',
                'long_exit_slow_sma',
                'short_entry_fast_sma',
                'short_entry_slow_sma',
                'short_exit_fast_sma',
                'short_exit_slow_sma'.
            initial_cash
            add_cash: the amount of cash to be added
            add_cash_alarm: rules for adding the `add_cash` amount
            price_info: description of the asset price data
        '''
        vfin_ops.TradingOpGen.__init__(self,
                                       initial_cash=initial_cash,
                                       add_cash=add_cash,
                                       add_cash_alarm=add_cash_alarm,
                                       price_info=price_info)
        if not price_info.di_close:
            raise ValueError
        if not isinstance(coefs, dict):
            raise TypeError
        for k, v in coefs.items():
            if k not in ('long_entry_fast_sma',
                         'long_entry_slow_sma',
                         'long_exit_fast_sma',
                         'long_exit_slow_sma',
                         'short_entry_fast_sma',
                         'short_entry_slow_sma',
                         'short_exit_fast_sma',
                         'short_exit_slow_sma'):
                raise ValueError
            if not isinstance(v, int):
                raise TypeError

        self.coefs = coefs
        self._init_di_coefs()

    def _init_di_coefs(self):
        self.di['long entry fast sma'] = vfin.DataInfo(self.name,
                                                       'long entry fast sma')
        self.di['long entry slow sma'] = vfin.DataInfo(self.name,
                                                       'long entry slow sma')
        self.di['long exit fast sma'] = vfin.DataInfo(self.name,
                                                      'long exit fast sma')
        self.di['long exit slow sma'] = vfin.DataInfo(self.name,
                                                      'long exit slow sma')
        self.di['short entry fast sma'] = vfin.DataInfo(self.name,
                                                        'short entry fast sma')
        self.di['short entry slow sma'] = vfin.DataInfo(self.name,
                                                        'short entry slow sma')
        self.di['short exit fast sma'] = vfin.DataInfo(self.name,
                                                       'short exit fast sma')
        self.di['short exit slow sma'] = vfin.DataInfo(self.name,
                                                       'short exit slow sma')

    def ops_prepare(self) -> list[vfin.Operation]:
        '''
        Perform preparation operations before the main cycle.

        Generate operations to:
        - Calculate SMAs
        '''
        ops = [
            vfin_ops.Call(
                function=lambda price:
                    ta.SMA(price, self.long_entry_fast_sma)[-1],
                kwargs={'price': self.opgen['price close'].di['src']},
                ret=self.di['long entry fast sma']),
            vfin_ops.Call(
                function=lambda price:
                    ta.SMA(price, self.long_entry_slow_sma)[-1],
                kwargs={'price': self.opgen['price close'].di['src']},
                ret=self.di['long entry slow sma']),
            vfin_ops.Call(
                function=lambda price:
                    ta.SMA(price, self.long_exit_fast_sma)[-1],
                kwargs={'price': self.opgen['price close'].di['src']},
                ret=self.di['long exit fast sma']),
            vfin_ops.Call(
                function=lambda price:
                    ta.SMA(price, self.long_exit_slow_sma)[-1],
                kwargs={'price': self.opgen['price close'].di['src']},
                ret=self.di['long exit slow sma']),
            vfin_ops.Call(
                function=lambda price:
                    ta.SMA(price, self.short_entry_fast_sma)[-1],
                kwargs={'price': self.opgen['price close'].di['src']},
                ret=self.di['short entry fast sma']),
            vfin_ops.Call(
                function=lambda price:
                    ta.SMA(price, self.short_entry_slow_sma)[-1],
                kwargs={'price': self.opgen['price close'].di['src']},
                ret=self.di['short entry slow sma']),
            vfin_ops.Call(
                function=lambda price:
                    ta.SMA(price, self.short_exit_fast_sma)[-1],
                kwargs={'price': self.opgen['price close'].di['src']},
                ret=self.di['short exit fast sma']),
            vfin_ops.Call(
                function=lambda price:
                    ta.SMA(price, self.short_exit_slow_sma)[-1],
                kwargs={'price': self.opgen['price close'].di['src']},
                ret=self.di['short exit slow sma']),
        ]
        return ops

    def ops_long_entry_signal(self) -> list[vfin.Operation]:
        '''
        Long entry signal.

        Generate operations to:
        - Calculate long entry signal self.di['long entry signal']
        '''
        ops = [
            vfin_ops.Call(function=lambda fast, slow: fast[-1] > slow[-1],
                          kwargs={'fast': self.di['long entry fast sma'],
                                  'slow': self.di['long entry slow sma']},
                          ret=self.di['long entry signal']),
        ]
        return ops

    def ops_long_exit_signal(self) -> list[vfin.Operation]:
        '''
        Long exit signal.

        Generate operations to:
        - Calculate long exit signal self.di['long exit signal']
        '''
        ops = [
            vfin_ops.Call(function=lambda fast, slow: fast[-1] < slow[-1],
                          kwargs={'fast': self.di['long exit fast sma'],
                                  'slow': self.di['long exit slow sma']},
                          ret=self.di['long exit signal']),
        ]
        return ops

    def ops_short_entry_signal(self) -> list[vfin.Operation]:
        '''
        Short entry signal.

        Generate operations to:
        - Calculate short entry signal self.di['short entry signal']
        '''
        ops = [
            vfin_ops.Call(function=lambda fast, slow: fast[-1] < slow[-1],
                          kwargs={'fast': self.di['short entry fast sma'],
                                  'slow': self.di['short entry slow sma']},
                          ret=self.di['short entry signal']),
        ]
        return ops

    def ops_short_exit_signal(self) -> list[vfin.Operation]:
        '''
        short exit signal.

        Generate operations to:
        - Calculate short exit signal self.di['short exit signal']
        '''
        ops = [
            vfin_ops.Call(function=lambda fast, slow: fast[-1] > slow[-1],
                          kwargs={'fast': self.di['short exit fast sma'],
                                  'slow': self.di['short exit slow sma']},
                          ret=self.di['short exit signal']),
        ]
        return ops
