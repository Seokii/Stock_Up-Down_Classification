from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np

code = '005930' # 삼성전자 코드두
url = f'https://finance.naver.com/item/sise_day.naver?code={code}'
headers = {'User-agent': 'Mozilla/5.0'}
req = requests.get(url, headers=headers)
html = BeautifulSoup(req.text, "lxml")

# 네이버 주식 크롤링
pgrr = html.find('td', class_='pgRR')
s = pgrr.a['href'].split('=')
last_page = s[-1]

df = None

for page in range(1, int(last_page)+1):
    req = requests.get(f'{url}&page={page}', headers=headers)
    df = pd.concat([df, pd.read_html(req.text, encoding = 'euc-kr')[0]], ignore_index=True)

# 데이터가 없는 행 일괄 삭제
df.dropna(inplace = True)

# 인덱스 재배열
df.reset_index(drop=True, inplace=True)

# 1년 평균 250거래일
df = df.loc[:1251].copy()

df['종가_등락률'] = round((df['종가']-df['종가'].shift(-1)) / df['종가'].shift(-1) *100, 2)
df['거래량_등락률'] = round((df['거래량']-df['거래량'].shift(-1)) / df['거래량'].shift(-1) *100, 2)
df['고가-종가_비율'] = round((df['고가']-df['종가']) / df['고가'] * 100, 2)
df['종가-저가_비율'] = round((df['종가']-df['저가']) / df['종가'] * 100, 2)

df['연속상승'] = np.nan
df['연속하락'] = np.nan

for i in range(len(df) - 1):
    if df['종가_등락률'][i] > 0 and df['종가_등락률'][i + 1] > 0:
        df['연속상승'][i] = 1
    else:
        df['연속상승'][i] = 0

    if df['종가_등락률'][i] < 0 and df['종가_등락률'][i + 1] < 0:
        df['연속하락'][i] = 1
    else:
        df['연속하락'][i] = 0

df['target'] = np.nan

for i in range(1, len(df)-1):
    if df['종가_등락률'][i-1] > 0:
        df['target'][i] = 1
    else:
        df['target'][i] = 0



df_result = df.iloc[1:-1,7:].copy()
df_result['target'] = df_result['target'].astype('int')
df_result['연속상승'] = df_result['연속상승'].astype('int')
df_result['연속하락'] = df_result['연속하락'].astype('int')

df_result = df_result.replace([np.inf, -np.inf], np.nan)
df_result.isnull().sum()

df_result.to_csv('df_result.csv', index=False)