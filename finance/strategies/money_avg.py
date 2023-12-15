'''
Simple money averaging strategy.
'''
import typing
import vfin
import vfin_ops
import vtime


# pylint: disable=too-few-public-methods
class MoneyAvgOpGen(vfin_ops.TradingOpGen):
    '''
    Generate an operation sequence for money averaging over time.

    Args:
        initial_cash: initial cash
        add_cash: cash that is added periodically
        add_cash_alarm: alarm for adding cash
        price_di: price data for buying/selling asset
        price_slippage_pct: price slippage in percents
    '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 initial_cash: typing.Union[int, float],
                 add_cash: typing.Union[int, float] = 0,
                 add_cash_alarm: typing.Union[str, vtime.Alarm] = None,
                 price_info: vfin.InstrumentInfo = None):

        if not price_info.di['close']:
            raise ValueError

        vfin_ops.TradingOpGen.__init__(self,
                                       initial_cash=initial_cash,
                                       add_cash=add_cash,
                                       add_cash_alarm=add_cash_alarm,
                                       price_info=price_info)

    def ops_long_entry_signal(self) -> list[vfin.Operation]:
        '''
        Long entry signal.

        Generate operations to:
        - Calculate long entry signal self.di['long entry signal']
        '''
        ops = [
            vfin_ops.Call(
                function=lambda x: x[-1],
                kwargs={'x': self.opgens['add cash alarm'].di['signal']},
                ret=self.di['long entry signal'])
        ]
        return ops
