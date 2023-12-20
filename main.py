import boto3
from botocore import UNSIGNED
from botocore.client import Config
from datetime import datetime
import time
import pygrib
import pandas as pd
from dateutil.relativedelta import relativedelta
import os
import argparse
from tqdm import tqdm
import numpy as np
import re
from bootstrap import upload_report, delete_report
import json
import redis
import random

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

parser = argparse.ArgumentParser(
                    prog='Get Weather Data',
                    description='Downloads weather data from an S3 Bucket and processes them into a DataFrame',)

parser.add_argument('-d',)
parser.add_argument('-c',)  
args = parser.parse_args()

with open('normal_tdd.json', 'r') as openfile:
    normal_dict = json.load(openfile)
ct_df = pd.read_csv("usregions.csv")[:30000]
lls = list(zip(ct_df['lat'], ct_df['lng']))

if args.d is None:
    dt = datetime.now()
else:
    month = int(args.d.split('/')[0])
    day = int(args.d.split('/')[1])
    dt = datetime(datetime.now().year, month, day)


client = boto3.client('s3', config=Config(signature_version=UNSIGNED))

if args.c is None:
    file_dt = "".join(list(map(str,[dt.year,f"{dt.month:02d}",f"{dt.day:02d}"])))
    bucket = client.list_objects(Bucket='noaa-gefs-pds', Prefix = "gefs."+file_dt+"/", Delimiter="/",)

    while True:
        if bucket.get('CommonPrefixes') is not None:
            fldr = bucket.get('CommonPrefixes')[-1].get('Prefix')
            break
        else:
            time.sleep(300)
    cycle = fldr.split('/')[-2]
    base = f'{fldr[:-1]}/atmos/pgrb2ap5/geavg.t{cycle}z.pgrb2a.0p50.f'
else:
    if args.c == "18" and args.d is None:
        dt = dt + relativedelta(days=-1)
        file_dt = "".join(list(map(str,[dt.year,f"{dt.month:02d}",f"{dt.day:02d}"])))
    else:
        file_dt = "".join(list(map(str,[dt.year,f"{dt.month:02d}",f"{dt.day:02d}"])))
    cycle = f'{int(args.c):02d}'
    base = f'gefs.{file_dt}/{cycle}/atmos/pgrb2ap5/geavg.t{cycle}z.pgrb2a.0p50.f'

tabs = r.hgetall("tabs")
tabs[cycle] = f'{ dt.strftime("%d-%m-%Y")} [{cycle}]'
r.hset('tabs', mapping=tabs)
r.set('peepo', random.choice(os.listdir('./assets/icons/')))

try:
    report_ls = os.listdir("./reports")
    r = re.compile(f"_{((int(cycle)-6)%24):02d}$")
    fn = list(filter(r.search, report_ls))[0]

    last_report = pd.read_csv(f"./reports/{fn}")
    last_report = last_report.iloc[:-1].to_dict()
except:
    last_report = report_dict = {
        "Current FC": [],
        "FC 6 hours ago": [],
        "FC 12 hours ago": [],
        "FC 18 hours ago": [],
        "FC 24 hours ago": [],
    }
def _combine_reports(current_cycle, past_cycle, last_forecast):
    if current_cycle <= past_cycle:
        return list(last_forecast.values())[1:] + [np.NaN]
    return last_forecast

report_dict = {
        "Date": [(dt+relativedelta(days=i)).strftime("%a, %d %b %Y") for i in range(1,16)],
        "Normal": [normal_dict[(dt+relativedelta(days=i)).strftime("%d-%m")] for i in range(1,16)],
        "Diff from normal": [],
        "Current FC": [],
        "FC 6 hours ago": _combine_reports(int(cycle),(int(cycle)-6)%24, last_report['Current FC']),
        "FC 12 hours ago": _combine_reports(int(cycle),(int(cycle)-6)%24, last_report['FC 6 hours ago']),
        "FC 18 hours ago": _combine_reports(int(cycle),(int(cycle)-6)%24, last_report['FC 12 hours ago']),
        "FC 24 hours ago": _combine_reports(int(cycle),(int(cycle)-6)%24, last_report['FC 18 hours ago']),
        "Diff 12 hours ago": [],
        "Diff 24 hours ago": []
    }

files = []
for i in range(24-int(cycle),243,3):
    files.append(base+f"{i:03d}")
for i in range(246,390-int(cycle),6):
    files.append(base+f"{i}")

def process(file, cycle):
    grbs = pygrib.open(file)
    grb = grbs.select(name='Temperature')[-2]
    data = grb.data()[0]
    
    def f(lat, lon):
        return round(abs(data[int(round(-2*lat)+180),int(round(2*lon))]*1.8-459.67-65),2)
    
    ct_df['dd_'+cycle] = [f(lat, lon) for lat,lon in lls]
    
    grbs.close()
def _to_state(x):
    return pd.Series({'dd':(x['population'] * x['dd']/x['population'].sum()).sum(),'population': x['population'].sum()})
def _to_region(x):
    return pd.Series({'dd':(x['population'] * x['dd']/x['population'].sum()).sum(),'population': x['population'].sum()})

try:
    report_ls = os.listdir("./reports")
    r = re.compile(f"_{int(cycle):02d}$")
    fn = list(filter(r.search, report_ls))[0]
    os.remove(f"./reports/{fn}")
except:
    pass

cycles = []
error_flag = False
pbar = tqdm(total=len(files))
while files:
    idx = int(files[0].split(".")[-1][-3:])
    try:    
        if idx%24==(24-int(cycle))%24 and idx>24-int(cycle) and not error_flag:
            ct_df['dd'] = ct_df[cycles].sum(axis=1)/len(cycles)
            
            state_df = ct_df.groupby(['state_name','region'])[['population', 'dd']].apply(_to_state).reset_index()
            region_df = state_df.groupby(['region'])[['population','dd']].apply(_to_region).reset_index()
            national_dd = round((region_df['population']*region_df['dd']).sum()/region_df['population'].sum(),2)
            report_dict['Current FC'].append(national_dd)
            
            report_df = pd.DataFrame(dict([ (k,pd.Series(v,dtype=np.float16)) if k != 'Date' else (k,pd.Series(v)) for k,v in report_dict.items() ]))
            report_df['Diff from normal'] = report_df['Current FC']-report_df['Normal']
            report_df['Diff 12 hours ago'] = report_df['Current FC']-report_df['FC 12 hours ago']
            report_df['Diff 24 hours ago'] = report_df['Current FC']-report_df['FC 24 hours ago']
            report_df.loc['Total']= report_df[report_df.columns[1:]][:-1].sum(min_count=1)
            report_df = report_df.round(2)
            report_df.drop(columns=['Normal']).to_csv(f'reports/report_{ dt.strftime("%Y-%m-%d")}_{cycle}', index=False)
            r.set(cycle, report_df.drop(columns=['Normal']).to_csv(index=False))

            cycles = []
        client.download_file('noaa-gefs-pds', files[0], 'temp')
        cycles.append(f"dd_{idx%24:02d}")
        process('temp', f"{idx%24:02d}")
        time.sleep(2)
        pbar.update()
        del files[0]
        error_flag = False
    except Exception as e:
        # print(e, flush=True)
        error_flag = True
        time.sleep(60)
pbar.close()

try:  
    os.remove('temp')
    delete_report(f'report_{ (dt+relativedelta(days=-1)).strftime("%Y-%m-%d")}_{cycle}')
    upload_report(f'reports/report_{ dt.strftime("%Y-%m-%d")}_{cycle}')
except:
    pass
    

    
