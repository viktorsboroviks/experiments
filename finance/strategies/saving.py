'''
Simple saving strategy.
'''
import vfin
import vfin_ops
import vplot
import vtime


# pylint: disable=too-few-public-methods
class SavingOpGen(vfin_ops.TradingOpGen):
    '''
    Generate an operation sequence for  saving over time.
    '''
    def __init__(self,
                 initial_value: float,
                 add_value: float = None,
                 add_alarm: vtime.Alarm = None):
        vfin_ops.TradingOpGen.__init__(self,
                                       initial_value,
                                       add_value,
                                       add_alarm)

        self.datainfo['total'] = vfin.DataInfo(self.name,
                                               'total',
                                               first_value=initial_value)
        if add_value:
            self.opgens['alarm'] = vfin_ops.AlarmOpGen(add_alarm)

    def ops(self):
        '''
        Generate operations for this sequence.
        '''
        ops = [
            # move assets from previous datetime
            vfin_ops.Call(function=lambda x: x[-2],
                          kwargs={'x': self.datainfo['total']},
                          ret=self.datainfo['total']),
        ]
        if self.add_value:
            ops += self.opgens['alarm'].ops()
            ops += [
                # receive monthly deposit
                vfin_ops.Call(function=lambda m, x: \
                              (x[-1] + self.add_value) if m[-1] else x[-1],
                              kwargs={'m': self.opgens['alarm'].datainfo['alarm'],
                                      'x': self.datainfo['total']},
                              ret=self.datainfo['total']),
            ]
        return ops

    def debug_subplots(self, table):
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
                        y=table[self.datainfo['total'].name],
                        color=vplot.CSSColor.GREEN,
                        width=1.0,
                        name='total',
                        showlegend=False,
                        showannotation=True,
                    )
                ]
            )
        ]
        if self.add_value:
            subplots += [
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
                            name='alarm',
                            showlegend=False,
                            showannotation=True,
                        )
                    ]
                ),
            ]
        return subplots
