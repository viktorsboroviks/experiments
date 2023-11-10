'''
Experiment for generating alarm.
'''
import vfin
import vfin_ops
import datetime

data = vfin.Data({
    '^SPX': vfin.fetch_ticker('^SPX',
                              start=datetime.datetime(2020, 1, 1),
                              end=datetime.datetime(2023, 11, 1))
})

alarm_opgen = vfin_ops.AlarmOpGen('monthly')
# debug name
print(alarm_opgen.name)

vfin.BacktestEngine(
    data,
    alarm_opgen.ops()
).run()

alarm_opgen.debug_plot(data.big_table(), 'test_alarm.svg')
