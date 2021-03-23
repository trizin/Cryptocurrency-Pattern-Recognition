# %%
from patterns import candlestick_patterns
from patterns import candle_rankings
from generate_data import createData
import sys
import pandas as pd
import math
import plotly.graph_objs as go
import plotly.express as px
from plotly.graph_objs.scatter.marker import Line
from plotly.offline import plot
import numpy as np
import talib

TICKER = sys.argv[1]+"_"+sys.argv[2]
DAYS = sys.argv[3]
if len(sys.argv) == 5:
    GET_ALL = True if sys.argv[4] == "all" else False
else:
    GET_ALL = False
df = createData(TICKER, DAYS)

pattern_to_candle = {v: k for k, v in candlestick_patterns.items()}
patterns = []
pattern_names = []
for pattern in candlestick_patterns.keys():
    pattern_function = getattr(talib, pattern)
    results = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
    last = sum(results.tail(5))
    if sum(results) == 0:
        continue
    if GET_ALL or last != 0:
        patterns.append(results)
        pattern_names.append(candlestick_patterns[pattern])
    if last > 0:
        print('Bullish!', candlestick_patterns[pattern])
    elif last < 0:
        print('Bearish!', candlestick_patterns[pattern])
if patterns == []:
    print("No patterns found!")
    sys.exit(0)
patterns = np.array(patterns)

trace = go.Candlestick(
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close'])
ema = talib.EMA(df['Close'], timeperiod=30)
for i in range(len(ema)):
    if math.isnan(ema[i]):
        ema[i] = 0
trace2 = go.Scatter(x=ema)

data = [trace]

fig = go.Figure(data=data)


figures = []
for arr in range(len(patterns)):
    copy_fig = go.Figure(fig)
    shapes = []
    annotations = []
    for i in range(len(patterns[arr])):
        if patterns[arr][i] > 0 or patterns[arr][i] < 0:
            toadd = patterns[arr][i] / patterns[arr].max() / 2
            rank = 0
            if patterns[arr][i] > 0:
                color = "green"
            else:
                color = "red"
            shapes.append(dict(
                fillcolor=color,
                opacity=0.3,
                x0=i-1, x1=i, y0=0.5, y1=0.5 + toadd, xref='x', yref='paper',
                line_width=1))

    hi_rank = candle_rankings[f"{pattern_to_candle[pattern_names[arr]]}_Bull"]
    low_rank = candle_rankings[f"{pattern_to_candle[pattern_names[arr]]}_Bear"]
    copy_fig.update_layout(
        title=f"{TICKER} {pattern_names[arr]} Bull:{hi_rank}\nBear:{low_rank}",
        yaxis_title=f"",
        shapes=shapes,
        annotations=annotations
    )
    figures.append(copy_fig)

with open(f'./html/{TICKER}.html', 'w') as f:
    for fig in figures:
        f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
