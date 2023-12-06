'''
SMA cross strategy.
'''

import typing
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

    def ops_long_entry(self):
        '''
        Generate operations to:
        - Calculate long entry signal into self.di['long entry signal']
        - Calculate long cash diff self.di['long cash diff']
        '''
        # TODO: Add
        # TODO: Update docstring
        pass

    def ops_long_exit(self):
        # TODO: Add
        # TODO: Update docstring
        pass

    def ops_short_entry(self):
        # TODO: Add
        # TODO: Update docstring
        pass

    def ops_short_exit(self):
        # TODO: Add
        # TODO: Update docstring
        pass
