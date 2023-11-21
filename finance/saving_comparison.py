'''
Experiment for testing money saving.
'''
import datetime
import vfin
import vtime
import strategies.saving
import strategies.money_avg

data = vfin.Data({
    '^SPX': vfin.fetch_ticker('^SPX',
                              start=datetime.datetime(2000, 1, 1),
                              end=datetime.datetime(2023, 11, 1))
})

monthly_alarm = vtime.Alarm('monthly')
saving1_opgen = strategies.saving.SavingOpGen(
    initial_value=1000)

saving2_opgen = strategies.saving.SavingOpGen(
    initial_value=1000,
    add_value=100,
    add_alarm=monthly_alarm)

money_avg_opgen = strategies.money_avg.MoneyAvgOpGen(
    initial_value=1000,
    add_value=100,
    add_alarm=monthly_alarm,
    price_di=vfin.DataInfo('^SPX', 'Close'),
    price_slippage_pct=0.5
)

vfin.BacktestEngine(
    data,
    saving1_opgen.ops() +
    saving2_opgen.ops() +
    money_avg_opgen.ops()
).run()

print(saving1_opgen.total(data.big_table()))
print(saving2_opgen.total(data.big_table()))
print(money_avg_opgen.total(data.big_table()))

# debug
saving1_opgen.debug_plot(data.big_table(), 'test_saving1.svg')
saving2_opgen.debug_plot(data.big_table(), 'test_saving2.svg')
money_avg_opgen.debug_plot(data.big_table(), 'test_money_avg.svg')
