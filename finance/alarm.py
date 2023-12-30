'''
Experiment for generating alarm.
'''
import datetime
import vfin
import vfin_ops
import vtime

dfs = {
    '^SPX': vfin.fetch_ticker('^SPX',
                              start=datetime.datetime(2020, 1, 1),
                              end=datetime.datetime(2023, 11, 1))
}

alarm_opgen = vfin_ops.AlarmOpGen(vtime.Alarm('monthly'))
# debug name
print(alarm_opgen.name)

big_table = vfin.BacktestEngine(
    alarm_opgen.ops(),
    dfs
).run()

alarm_opgen.debug_plot(big_table, 'test_alarm.svg')
