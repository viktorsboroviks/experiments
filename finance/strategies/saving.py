'''
Simple saving strategy.
'''
import pandas as pd
import vcore
import vfin
import vfin_ops
import vplot
import vtime


class SavingOpGen(vfin_ops.TradingOpGen):
    '''
    Generate an operation sequence for  saving over time.
    '''
    def __init__(self,
                 name: str,
                 initial_value: float,
                 add_value: float = None,
                 add_alarm: vtime.Alarm = None):
        vfin_ops.TradingOpGen.__init__(self,
                                       name,
                                       initial_value,
                                       add_value,
                                       add_alarm)

        self.datainfo['total'] = vfin.DataInfo('total', name,
                                 first_value=initial_value)
        if add_value:
            self.opgens['alarm'] = vfin_ops.AlarmOpGen('alarm',
                                                        add_alarm)

    def ops(self):
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

    # pylint: disable=too-many-arguments
    def _debug_plot(self,
                    table,
                    filename_svg,
                    width,
                    height,
                    font_size):

        subplots = [
            vplot.Subplot(
                col=1,
                row=1,
                traces=[
                    vplot.Step(
                        x=table.index,
                        y=table[self.datainfo['total'].name()],
                        color=vcore.CSSColor.GREEN,
                        width=1.0,
                        name=self.datainfo['total'].name(),  # TODO: fix the name. Why "None:"?
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
                            y=table[self.opgens['alarm'].datainfo['alarm'].name()],
                            color=vcore.CSSColor.BLACK,
                            width=1.0,
                            name=self.opgens['alarm'].datainfo['alarm'].name(),
                            showlegend=False,
                            showannotation=True,
                        )
                    ]
                ),
            ]

        vplot.PlotlyPlot(
            height=height,
            width=width,
            font_size=font_size,
            subplots=subplots
        ).svg(filename_svg)
