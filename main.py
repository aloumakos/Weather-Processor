import boto3
from botocore import UNSIGNED
from botocore.client import Config
from datetime import datetime, date
import time
import pygrib
import pandas as pd
from dateutil.relativedelta import relativedelta
import os
import argparse
from tqdm import tqdm
import numpy as np

parser = argparse.ArgumentParser(
                    prog='Get Weather Data',
                    description='Downloads weather data from an S3 Bucket and processes them into a DataFrame',)

parser.add_argument('-d',)
parser.add_argument('-c',)  
args = parser.parse_args()


ct_df = pd.read_csv("usregions.csv")[:30000]
lls = list(zip(ct_df['lat'], ct_df['lng']))

if args.d is None:
    dt = datetime.now()
else:
    month = int(args.d.split('/')[0])
    day = int(args.d.split('/')[1])
    dt = datetime(datetime.now().year, month, day)
    
file_dt = "".join(list(map(str,[dt.year,dt.month,f"{dt.day:02d}"])))
client = boto3.client('s3', config=Config(signature_version=UNSIGNED))

if args.c is None:
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
    cycle = f'{int(args.c):02d}'
    base = f'gefs.{file_dt}/{cycle}/atmos/pgrb2ap5/geavg.t{cycle}z.pgrb2a.0p50.f'
try:
    if int(cycle) ==0:
        last_report_fn = f'./reports/report_{ (dt+relativedelta(days=-1)).strftime("%Y-%m-%d")}_{((int(cycle)-6)%24):02d}'
    else:
        last_report_fn = f'./reports/report_{ dt.strftime("%Y-%m-%d")}_{((int(cycle)-6)%24):02d}'
    last_report = pd.read_csv(last_report_fn)
    last_report = last_report.iloc[:-1].to_dict()
except:
    last_report = report_dict = {
        "Current FC": [],
        "FC 6 hours ago": [],
        "FC 12 hours ago": [],
        "FC 18 hours ago": [],
        "FC 24 hours ago": [],
    }
report_dict = {
        "Date": [(date.today()+relativedelta(days=i)).strftime("%a, %d %b %Y") for i in range(1,16)],
        "Current FC": [],
        "FC 6 hours ago": last_report['Current FC'],
        "FC 12 hours ago": last_report['FC 6 hours ago'],
        "FC 18 hours ago": last_report['FC 12 hours ago'],
        "FC 24 hours ago": last_report['FC 18 hours ago'],
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
    grb = grbs.select(name='Temperature')[-1]
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
    os.remove(f'./reports/report_{ (dt+relativedelta(days=-1)).strftime("%Y-%m-%d")}_{cycle}')
except:
    pass

cycles = []
pbar = tqdm(files)
for file in pbar:
    idx = int(file.split(".")[-1][-3:])
    # print(file, idx, cycle)
    try:
        
        if idx%24==(24-int(cycle))%24 and idx>24-int(cycle):
            ct_df['dd'] = ct_df[cycles].sum(axis=1)/len(cycles)
            
            state_df = ct_df.groupby(['state_name','region'])[['population', 'dd']].apply(_to_state).reset_index()
            region_df = state_df.groupby(['region'])[['population','dd']].apply(_to_region).reset_index()
            national_dd = round((region_df['population']*region_df['dd']).sum()/region_df['population'].sum(),2)
            report_dict['Current FC'].append(national_dd)
            
            report_df = pd.DataFrame(dict([ (k,pd.Series(v,dtype=np.float16)) if k != 'Date' else (k,pd.Series(v)) for k,v in report_dict.items() ]))
            report_df['Diff 12 hours ago'] = report_df['Current FC']-report_df['FC 12 hours ago']
            report_df['Diff 24 hours ago'] = report_df['Current FC']-report_df['FC 24 hours ago']
            report_df.loc['Total']= report_df[report_df.columns[1:]].sum(min_count=1)
            report_df = report_df.round(2)
            report_df.to_csv(f'reports/report_{ dt.strftime("%Y-%m-%d")}_{cycle}', index=False)
            
            cycles = []

        client.download_file('noaa-gefs-pds', file, 'temp')
        cycles.append(f"dd_{idx%24:02d}")
        process('temp', f"{idx%24:02d}")
        time.sleep(2)
    except Exception as e:
        print(e, flush=True)
        time.sleep(60)

try:
    os.remove('temp')
except:
    pass
    

    
