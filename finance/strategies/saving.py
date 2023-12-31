'''
Simple saving strategy.
'''
import vfin_ops
import vplot
import vtime
import vtable


class SavingOpGen(vfin_ops.TradingOpGen):
    '''
    Generate an operation sequence for  saving over time.
    '''
    def __init__(self,
                 initial_cash: float,
                 add_cash: float = None,
                 add_cash_alarm: vtime.Alarm = None):
        vfin_ops.TradingOpGen.__init__(self,
                                       initial_cash,
                                       add_cash,
                                       add_cash_alarm)

        self.di['total'] = vtable.DataInfo(self.name,
                                           'total',
                                           first_value=initial_cash)
        if add_cash:
            self.opgens['alarm'] = vfin_ops.AlarmOpGen(add_cash_alarm)

    def ops(self):
        '''
        Generate operations for this sequence.
        '''
        ops = [
            # move assets from previous datetime
            vfin_ops.Call(function=lambda x: x[-2],
                          kwargs={'x': self.di['total']},
                          ret=self.di['total']),
        ]
        if self.add_cash:
            ops += self.opgens['alarm'].ops()
            ops += [
                # receive monthly deposit
                vfin_ops.Call(function=lambda m, x: \
                              (x[-1] + self.add_cash) if m[-1] else x[-1],
                              kwargs={'m': self.opgens['alarm'].di['signal'],
                                      'x': self.di['total']},
                              ret=self.di['total']),
            ]
        return ops

    def debug_subplots(self, table) -> list[vplot.Subplot]:
        '''
        Return a list of debug subplots.
        Also used to draw debug_plot().

        Args:
            table: pd.DataFrame object containing the data to debug.
        '''
        subplots = [
            vplot.Subplot(
                col=1,
                row=1,
                traces=[
                    vplot.Step(
                        x=table.index,
                        y=table[self.di['total'].name],
                        color=vplot.CSSColor.GREEN,
                        width=1.0,
                        name='total',
                        showlegend=False,
                        showannotation=True,
                    )
                ]
            )
        ]
        if self.add_cash:
            subplots += [
                vplot.LogicSignalSubplot(
                    col=1,
                    row=2,
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
