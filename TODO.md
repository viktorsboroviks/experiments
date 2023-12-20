# TODO

## goal

- always day one
- keep simple
- optimize when needed
- inspiring, fantastically beautiful graphs

## tasks

- fix tools make examples and warnings in those
- fix reasonable TODOs

- find optimal sma cross parameters for daily SPX

- publish tool
- publish sma cross experiment

- add simple broker simulation
- add summary statistics
- compare to known framework

- test RSI strategy
- test parameter optimization
- run parameter optimization

- run profiling
- find bottlenecks
- try compiling
- try separating calls: vectors / sequences
  - run vectors first over all data at once
  - run sequrnces after
- try optimizing

- find decision making points, where market slows down to make a decision
  and either goes up or down
  - best place to enter/exit
- try different options for best entry/exist points
- try different strategies relative to such points

- calculate probabilities at different point in time for different moves
- try graphing a heatmap of probabilities (experiment with resolution) -
  where the price would end based on combination of triggered strategies
- multiplication of such heatmaps based on triggers

- find some weak/simple working strategy (ma, rsi)

- try market heatmap strategy

- add tests?

- describe in article
- create ibkr or binance account
- setup bot

strategies:

- how to find the best strategy?
  - take some rule to buy/sell, parametrize, find best parameters
  - create a probabalistic heatmap of the market future, based on indicators
    - list indicators
    - for every indicator find probability distribution over time for
      predicting a market move from current point to some quadrant
      - e.g. after sma20>sma5
        - price goest up
          - probability of it over time to stop at a particular distance range
            from the starting point
          - higher probability - brighter heatmap
    - overlap indicators

suggestions:

- performance test - graph table size/execution time
