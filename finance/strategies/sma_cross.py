'''
SMA cross strategy.
'''

import typing
import talib as ta
import vfin
import vfin_ops
import vplot
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
    COEFS = {'long entry fast sma',
             'long entry slow sma',
             'long exit fast sma',
             'long exit slow sma',
             'short entry fast sma',
             'short entry slow sma',
             'short exit fast sma',
             'short exit slow sma'}

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
                'long entry fast sma',
                'long entry slow sma',
                'long exit fast sma',
                'long exit slow sma',
                'short entry fast sma',
                'short entry slow sma',
                'short exit fast sma',
                'short exit slow sma'.
            initial_cash
            add_cash: the amount of cash to be added
            add_cash_alarm: rules for adding the `add_cash` amount
            price_info: description of the asset price data
        '''
        if not price_info.di['price close']:
            raise ValueError
        if not isinstance(coefs, dict):
            raise TypeError
        for k, v in coefs.items():
            if k not in self.COEFS:
                raise ValueError
            if not isinstance(v, int):
                raise TypeError

        self.coefs = {}
        for c in self.COEFS:
            if c in coefs:
                self.coefs[c] = coefs[c]
            else:
                self.coefs[c] = 0

        vfin_ops.TradingOpGen.__init__(self,
                                       initial_cash=initial_cash,
                                       add_cash=add_cash,
                                       add_cash_alarm=add_cash_alarm,
                                       price_info=price_info)
        self._init_di_coefs()

    def _init_di_coefs(self):
        for c in self.COEFS:
            self.di[c] = vfin.DataInfo(self.name, c)

    def ops_prepare(self) -> list[vfin.Operation]:
        '''
        Perform preparation operations before the main cycle.

        Generate operations to:
        - Calculate SMAs
        '''
        ops = []
        for c in self.COEFS:
            if self.coefs[c]:
                ops += [
                    vfin_ops.Call(
                        function=lambda x, d: ta.SMA(x, d)[-1],
                        kwargs={'x': self.opgens['price close'].di['src'],
                                'd': self.coefs[c]},
                        ret=self.di[c]),
                ]
            else:
                ops += [
                    vfin_ops.Set(0, self.di[c])
                ]
        return ops

    def ops_long_entry_signal(self) -> list[vfin.Operation]:
        '''
        Long entry signal.

        Generate operations to:
        - Calculate long entry signal self.di['long entry signal']
        '''
        if not self.coefs['long entry slow sma'] \
                or not self.coefs['long entry fast sma']:
            return []
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
        if not self.coefs['long exit slow sma'] \
                or not self.coefs['long exit fast sma']:
            return []
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
        if not self.coefs['short entry slow sma'] \
                or not self.coefs['short entry fast sma']:
            return []
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
        if not self.coefs['short exit slow sma'] \
                or not self.coefs['short exit fast sma']:
            return []
        ops = [
            vfin_ops.Call(function=lambda fast, slow: fast[-1] > slow[-1],
                          kwargs={'fast': self.di['short exit fast sma'],
                                  'slow': self.di['short exit slow sma']},
                          ret=self.di['short exit signal']),
        ]
        return ops

    def debug_subplots(self, table, first_row=1) -> list[vplot.Subplot]:
        '''
        Return a list of debug subplots.
        Also used to draw debug_plot().

        Args:
            table: pd.DataFrame object containing the data to debug.
        '''
        subplots = vfin_ops.TradingOpGen.debug_subplots(self,
                                                        table,
                                                        first_row=first_row)
        subplots += [
            vplot.Subplot(
                col=1,
                row=first_row + len(subplots),
                traces=[
                    vplot.Scatter(
                        x=table.index,
                        y=table[self.di['long entry fast sma'].name],
                        color=vplot.CSSColor.RED,
                        width=1.0,
                        mode='lines',
                        name='long entry fast sma'),
                    vplot.Scatter(
                        x=table.index,
                        y=table[self.di['long entry slow sma'].name],
                        color=vplot.CSSColor.BLUE,
                        width=1.0,
                        mode='lines',
                        name='long entry slow sma'),
                ]
            ),
            vplot.Subplot(
                col=1,
                row=first_row + len(subplots) + 1,
                traces=[
                    vplot.Scatter(
                        x=table.index,
                        y=table[self.di['long exit fast sma'].name],
                        color=vplot.CSSColor.RED,
                        width=1.0,
                        mode='lines',
                        name='long exit fast sma'),
                    vplot.Scatter(
                        x=table.index,
                        y=table[self.di['long exit slow sma'].name],
                        color=vplot.CSSColor.BLUE,
                        width=1.0,
                        mode='lines',
                        name='long exit slow sma'),
                ]
            ),
            vplot.Subplot(
                col=1,
                row=first_row + len(subplots) + 2,
                traces=[
                    vplot.Scatter(
                        x=table.index,
                        y=table[self.di['short entry fast sma'].name],
                        color=vplot.CSSColor.RED,
                        width=1.0,
                        mode='lines',
                        name='short entry fast sma'),
                    vplot.Scatter(
                        x=table.index,
                        y=table[self.di['short entry slow sma'].name],
                        color=vplot.CSSColor.BLUE,
                        width=1.0,
                        mode='lines',
                        name='short entry slow sma'),
                ]
            ),
            vplot.Subplot(
                col=1,
                row=first_row + len(subplots) + 3,
                traces=[
                    vplot.Scatter(
                        x=table.index,
                        y=table[self.di['short exit fast sma'].name],
                        color=vplot.CSSColor.RED,
                        width=1.0,
                        mode='lines',
                        name='short exit fast sma'),
                    vplot.Scatter(
                        x=table.index,
                        y=table[self.di['short exit slow sma'].name],
                        color=vplot.CSSColor.BLUE,
                        width=1.0,
                        mode='lines',
                        name='short exit slow sma'),
                ]
            )
        ]
        return subplots
        # TODO: create a way to return only part of debug (definite subplots),
        #       not all
