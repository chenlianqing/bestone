#! /Users/chenlianqing/anaconda/bin python3
# -*- coding: utf-8 -*-


import tushare as ts
import datetime
import pandas as pd


# 无风险利率设定
zero_risk = 0.039

# 股价及市值
today_all = ts.get_today_all()
today_all['date'] = datetime.datetime.now().strftime('%Y-%m-%d')
today_all['mktcap'] = today_all['mktcap']/10000
today_all_end = today_all.loc[:,['code','name','date','trade','mktcap','per','pb']]

# 净利润
profit = ts.get_profit_data(year=2016, quarter=4)
profit['net_profits'] = profit['net_profits']/100

# 近3年平均净利润
profit_avg = pd.DataFrame()
now_year = datetime.datetime.now().year
early_year = now_year - 3

for i in range(early_year, now_year):
    profit_data = ts.get_profit_data(year=i, quarter=4)
    profit_data['year'] = i
    profit_avg = profit_avg.append(profit_data)

profit_avg['net_profits'] = profit_avg['net_profits']/100
profit_avg3 = profit_avg.groupby('code').agg({'net_profits':'mean'})
profit_avg3['code'] = profit_avg3.index
profit_avg3.columns = ['profits_avg3', 'code']

# 内在价值
profit['int_value'] = profit['net_profits']/zero_risk
profit_end = profit.loc[:,['code','name','net_profits','int_value','roe','net_profit_ratio']]

# 数据合并
data_all = pd.merge(left=today_all_end,right=profit_end,how='left',on=['code','name'])
data_all['int_times'] = data_all['mktcap']/data_all['int_value']
data_all = pd.merge(left=data_all, right=profit_avg3, how='left', on='code')
data_all['profits_gap'] = data_all['net_profits'] - data_all['profits_avg3']
data_all['profits_gap_rate'] = data_all['profits_gap']/data_all['profits_avg3']

# 持仓股票现状
print(data_all.loc[(data_all['name']=='兴业银行') | (data_all['name']=='中信证券'),:])

# 股票筛选
data_select = data_all.loc[(data_all['int_times'] <= 0.3) & (data_all['mktcap'] >= 100) & (data_all['net_profits'] >= 50) & (data_all['profits_gap_rate'] <= 1.0),:]

# 结果展示
print('There are ',len(data_select), 'stocks selected.')
print(data_select)

# 结果导出
# writer = pd.ExcelWriter('/Users/chenlianqing/Desktop/%s.xlsx' % datetime.datetime.now().strftime('%Y-%m-%d'))
# data_select.to_excel(writer, index=False)
# writer.save()
# writer.close()
