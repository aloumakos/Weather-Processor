from datetime import datetime

def extract_date(filename):
    parts = filename.split('_')
    date_part = parts[1]
    cycle_part = parts[2]
    return date_part, cycle_part

def get_tabs_from_files(report_ls, cycle):

    tabs = {}
    tabs[0] = tabs[1] = tabs[2] = tabs[3] = "TBA"
    filtered_list = [item for item in report_ls if item.startswith('report_2023')]
    fn = None
    for file in filtered_list:
        tab_l = extract_date(file)
        date = datetime.strptime(tab_l[0],'%Y-%m-%d')
        date = date.strftime('%d-%m-%Y')
        filename = f"{date} - {tab_l[1]}"
    
        if filename.endswith('00'): tabs['00']= filename 
        elif filename.endswith('06'): tabs['06'] = filename
        elif filename.endswith('12'): tabs['12']= filename
        elif filename.endswith('18'): tabs['18'] = filename
        if filename.endswith(cycle): fn = file

    return tabs, fn

def calculate_color(value):
    try:
        numeric_value = float(value)
        if -100 < numeric_value <= 0:
            red_value = max(int(255 - abs(numeric_value) * 75),95-abs(numeric_value))
            return f'rgb(255, {red_value}, {red_value})'
        elif 0 <= numeric_value < 100:
            blue_value = max(int(255 - abs(numeric_value) * 75),95-abs(numeric_value))
            return f'rgb({blue_value}, {blue_value}, 255)'
        else:
            return 'rgb(73,77,74)'
    except ValueError:
        return 'rgb(73,77,74)'