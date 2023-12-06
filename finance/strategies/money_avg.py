'''
Simple money averaging strategy.
'''
import typing
import vfin
import vfin_ops
import vplot
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
                 initial_cash: float,
                 add_cash: float,
                 add_cash_alarm: vtime.Alarm,
                 price_di: vfin.DataInfo,
                 price_slippage_pct: typing.Union[int, float] = 0.5):

        if not isinstance(price_di, vfin.DataInfo):
            raise TypeError
        if price_slippage_pct and not isinstance(price_slippage_pct,
                                                 (int, float)):
            raise TypeError

        self.price_di = price_di
        self.price_slippage_pct = price_slippage_pct

        vfin_ops.TradingOpGen.__init__(self,
                                       initial_cash,
                                       add_cash,
                                       add_cash_alarm)

        # total worth
        self.di['total'] = vfin.DataInfo(self.name,
                                         'total')
        self.di['cash'] = vfin.DataInfo(self.name,
                                        'cash',
                                        first_value=self.initial_cash)
        self.di['asset'] = vfin.DataInfo(self.name,
                                         'asset',
                                         first_value=0)

        self.opgens['alarm'] = vfin_ops.AlarmOpGen(self.add_cash_alarm)
        self.opgens['price'] = vfin_ops.PriceOpGen(self.price_di,
                                                   self.price_slippage_pct)

    def ops(self):
        '''
        Generate operations for this sequence.
        '''
        ops = []
        # add alarm
        ops += self.opgens['alarm'].ops()
        # add price
        ops += self.opgens['price'].ops()
        ops += [
            # move assets from previous datetime
            vfin_ops.Call(function=lambda x: x[-2],
                          kwargs={'x': self.di['cash']},
                          ret=self.di['cash']),
            vfin_ops.Call(function=lambda x: x[-2],
                          kwargs={'x': self.di['asset']},
                          ret=self.di['asset']),
            vfin_ops.Call(function=lambda x: x[-2],
                          kwargs={'x': self.di['total']},
                          ret=self.di['total']),

            # receive monthly deposit
            vfin_ops.Call(function=lambda m, x: \
                          (x[-1] + self.add_cash) if m[-1] else x[-1],
                          kwargs={'m': self.opgens['alarm'].di['signal'],
                                  'x': self.di['cash']},
                          ret=self.di['cash']),
            # buy asset
            vfin_ops.Call(function=lambda b, asset, cash, buy_price: \
                          (asset[-1] + cash[-1]/buy_price[-1]) if b[-1] else asset[-1],
                          kwargs={'b': self.opgens['alarm'].di['signal'],
                                  'asset': self.di['asset'],
                                  'cash': self.di['cash'],
                                  'buy_price': self.opgens['price'].di['buy']},
                          ret=self.di['asset']),
            # update cash
            vfin_ops.Call(function=lambda b, cash: \
                          0 if b[-1] else cash[-1],
                          kwargs={'b': self.opgens['alarm'].di['signal'],
                                  'cash': self.di['cash']},
                          ret=self.di['cash']),
            # total worth (in cash)
            vfin_ops.Call(function=lambda cash, asset, sell_price: \
                          cash[-1] + (asset[-1] * sell_price[-1]),
                          kwargs={'cash': self.di['cash'],
                                  'asset': self.di['asset'],
                                  'sell_price': self.opgens['price'].di['sell']},
                          ret=self.di['total']),
        ]
        return ops

    def debug_subplots(self, table) -> list[vplot.Subplot]:
        '''
        Return a list of debug subplots.
        Also used to draw debug_plot()

        Args:
            table: pd.DataFrame object containing the data to debug.
        '''
        price_subplots = self.opgens['price'].debug_subplots(table)
        subplots = price_subplots
        subplots += [
            vplot.Subplot(
                col=1,
                row=len(price_subplots) + 1,
                traces=[
                    vplot.Step(
                        x=table.index,
                        y=table[self.di['cash'].name],
                        color=vplot.CSSColor.BLACK,
                        width=1.0,
                        name='cash',
                        showlegend=False,
                        showannotation=True,
                    ),
                ]
            ),
            vplot.Subplot(
                col=1,
                row=len(price_subplots) + 2,
                traces=[
                    vplot.Step(
                        x=table.index,
                        y=table[self.di['asset'].name].diff(),
                        color=vplot.CSSColor.BLUE,
                        width=1.0,
                        name='asset change',
                        showlegend=False,
                        showannotation=True,
                    ),
                ]
            ),
            vplot.Subplot(
                col=1,
                row=len(price_subplots) + 3,
                traces=[
                    vplot.Step(
                        x=table.index,
                        y=table[self.di['asset'].name],
                        color=vplot.CSSColor.BLUE,
                        width=1.0,
                        name='asset',
                        showlegend=False,
                        showannotation=True,
                    ),
                ]
            ),
            vplot.Subplot(
                col=1,
                row=len(price_subplots) + 4,
                traces=[
                    vplot.Step(
                        x=table.index,
                        y=table[self.di['total'].name],
                        color=vplot.CSSColor.GREEN,
                        width=1.0,
                        name='total',
                        showlegend=False,
                        showannotation=True,
                    ),
                ]
            ),
            vplot.LogicSignalSubplot(
                col=1,
                row=len(price_subplots) + 5,
                yshift=1.2,
                steps=[
                    vplot.Step(
                        x=table.index,
                        y=table[self.opgens['alarm'].di['signal'].name],
                        color=vplot.CSSColor.BLACK,
                        width=1.0,
                        name='alarm',
                        showlegend=False,
                        showannotation=True,
                    )
                ]
            ),
        ]
        return subplots
