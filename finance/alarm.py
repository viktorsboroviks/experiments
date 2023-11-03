import vfin
import vfin_ops
import datetime

data = vfin.Data({
    '^SPX': vfin.fetch_ticker('^SPX',
                              start=datetime.datetime(2020, 1, 1),
                              end=datetime.datetime(2023, 11, 1))
})

alarm_ops = vfin_ops.AlarmOpGen('Monthly timer', 'monthly')

vfin.BacktestEngine(
    data,
    alarm_ops.get_ops()
).run()

alarm_ops.debug_plot(data.big_table(), 'test_alarm.svg')
