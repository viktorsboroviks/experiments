import pandas as pd
import vcore
import vfin
import vfin_ops
import vplot
import vtime


class CashSaving(vfin.TradingStrategy):
    '''
    Generate a cash saving trading strategy.
    '''
    def __init__(self,
                 strategy_name: str,
                 initial_cash: float,
                 add_cash: float = None,
                 add_cash_when: vtime.Alarm = None,
                 currency_name: str = 'USD'):
        vfin.TradingStrategy.__init__(self,
                       strategy_name,
                       initial_cash,
                       add_cash,
                       add_cash_when,
                       currency_name)
        # TODO: rename to Total smth, find a common name
        # TODO: create a common getter?
        self.di_saving = vfin.DataInfo(strategy_name, currency_name,
                                       first_value=initial_cash)
        if add_cash_when:
            self.seq_add_cash = vfin_ops.TimePeriodSeq('Alarm', add_cash_when)
        else:
            self.seq_add_cash = None

    def get_ops(self):
        ops = [
            # move assets from previous datetime
            vfin_ops.Call(function=lambda x: x[-2],
                          kwargs={'x': self.di_saving},
                          ret=self.di_saving),
        ]
        if self.seq_add_cash:
            ops += self.seq_add_cash.get_ops()
            ops += [
                # receive monthly deposit
                vfin_ops.Call(function=lambda m, x: \
                              (x[-1] + self.add_cash) if m[-1] else x[-1],
                              kwargs={'m': self.seq_add_cash.di_alarm,
                                      'x': self.di_saving},
                              ret=self.di_saving),
            ]
        return ops

    # pylint: disable=too-many-arguments
    def debug_plot(self,
                   table: pd.DataFrame,
                   filename_svg: str,
                   width=1000,
                   height=750,
                   font_size=10):
        if not isinstance(table, pd.DataFrame):
            raise TypeError
        if not isinstance(filename_svg, str):
            raise TypeError

        subplots = [
            vplot.Subplot(
                col=1,
                row=1,
                traces=[
                    vplot.Step(
                        x=table.index,
                        y=table[self.di_saving.pd_col_name()],
                        color=vcore.CSSColor.GREEN,
                        width=1.0,
                        name=self.di_saving.pd_col_name(),
                        showlegend=False,
                        showannotation=True,
                    )
                ]
            )
        ]
        if self.seq_add_cash:
            subplots += [
                vplot.LogicSignalSubplot(
                    col=1,
                    row=2,
                    yshift=1.2,
                    steps=[
                        vplot.Step(
                            x=table.index,
                            y=table[self.seq_add_cash.di_alarm.pd_col_name()],
                            color=vcore.CSSColor.BLACK,
                            width=1.0,
                            name=f'{self.seq_add_cash.di_alarm.col}',
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
