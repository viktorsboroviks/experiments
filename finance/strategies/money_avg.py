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
        initial_value: initial cash
        add_value: cash that is added periodically
        add_alarm: alarm for adding cash
        price_di: price data for buying/selling asset
        price_slippage_pct: price slippage in percents
    '''
    def __init__(self,
                 initial_value: float,
                 add_value: float,
                 add_alarm: vtime.Alarm,
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
                                       initial_value,
                                       add_value,
                                       add_alarm)

        # total worth
        self.datainfo['total'] = vfin.DataInfo(self.name,
                                               'total')
        self.datainfo['cash'] = vfin.DataInfo(self.name,
                                              'cash',
                                              first_value=self.initial_value)
        self.datainfo['asset'] = vfin.DataInfo(self.name,
                                               'asset',
                                               first_value=0)

        self.opgens['alarm'] = vfin_ops.AlarmOpGen(self.add_alarm)
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
                          kwargs={'x': self.datainfo['cash']},
                          ret=self.datainfo['cash']),
            vfin_ops.Call(function=lambda x: x[-2],
                          kwargs={'x': self.datainfo['asset']},
                          ret=self.datainfo['asset']),
            vfin_ops.Call(function=lambda x: x[-2],
                          kwargs={'x': self.datainfo['total']},
                          ret=self.datainfo['total']),

            # receive monthly deposit
            vfin_ops.Call(function=lambda m, x: \
                          (x[-1] + self.add_value) if m[-1] else x[-1],
                          kwargs={'m': self.opgens['alarm'].datainfo['alarm'],
                                  'x': self.datainfo['cash']},
                          ret=self.datainfo['cash']),
            # buy asset
            vfin_ops.Call(function=lambda b, asset, cash, buy_price: \
                          (asset[-1] + cash[-1]/buy_price[-1]) if b[-1] else asset[-1],
                          kwargs={'b': self.opgens['alarm'].datainfo['alarm'],
                                  'asset': self.datainfo['asset'],
                                  'cash': self.datainfo['cash'],
                                  'buy_price': self.opgens['price'].datainfo['buy']},
                          ret=self.datainfo['asset']),
            # update cash
            vfin_ops.Call(function=lambda b, cash: \
                          0 if b[-1] else cash[-1],
                          kwargs={'b': self.opgens['alarm'].datainfo['alarm'],
                                  'cash': self.datainfo['cash']},
                          ret=self.datainfo['cash']),
            # total worth (in cash)
            vfin_ops.Call(function=lambda cash, asset, sell_price: \
                          cash[-1] + (asset[-1] * sell_price[-1]),
                          kwargs={'cash': self.datainfo['cash'],
                                  'asset': self.datainfo['asset'],
                                  'sell_price': self.opgens['price'].datainfo['sell']},
                          ret=self.datainfo['total']),
        ]
        return ops

    # pylint: disable=too-many-arguments
    def _debug_plot(self,
                    table,
                    filename_svg,
                    width,
                    height,
                    font_size):
        # TODO: adjust
        vplot.PlotlyPlot(
            height=height,
            width=width,
            font_size=font_size,
            subplots=[
                vplot.Subplot(
                    col=1,
                    row=1,
                    traces=[
                        vplot.Step(
                            x=table.index,
                            y=table[self.datainfo['total'].name],
                            color=vplot.CSSColor.GREEN,
                            width=1.0,
                            name=self.datainfo['total'].name,
                            showlegend=False,
                            showannotation=True,
                        ),
                        vplot.Step(
                            x=table.index,
                            y=table[self.datainfo['cash'].name],
                            color=vplot.CSSColor.BLACK,
                            width=1.0,
                            name=self.datainfo['cash'].name,
                            showlegend=False,
                            showannotation=True,
                        ),
                        vplot.Step(
                            x=table.index,
                            y=table[self.datainfo['asset'].name],
                            color=vplot.CSSColor.BLUE,
                            width=1.0,
                            name=self.datainfo['asset'].name,
                            showlegend=False,
                            showannotation=True,
                        ),
                    ]
                ),
                vplot.LogicSignalSubplot(
                    col=1,
                    row=2,
                    yshift=1.2,
                    steps=[
                        vplot.Step(
                            x=table.index,
                            y=table[self.opgens['alarm'].datainfo['alarm'].name],
                            color=vplot.CSSColor.BLACK,
                            width=1.0,
                            name=self.opgens['alarm'].datainfo['alarm'].name,
                            showlegend=False,
                            showannotation=True,
                        )
                    ]
                ),
            ]
        ).svg(filename_svg)
