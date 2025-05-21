import os
import sys
from constants import report_types
import calendar
import statistics

def requested_reports(args):
    requested_reports = []
    i = 0
    while i < len(args):
        if args[i] == '-e':
            splits = args[i + 1].split('/')
            year = args[i + 1].split('/')[0]
            fileName = []
            for month_number in range(1, 13):
                month_name = calendar.month_name[int(month_number)][:3]
                file_name = ('_').join(['Murree', 'weather', year, month_name]) + '.txt'
                fileName.append(file_name)
            requested_reports.append({'type': report_types[args[i]], 'year': year, 'month': None, 'fileName': fileName })
            i += 2
        elif args[i] == '-a':
            splits = args[i + 1].split('/')
            year = splits[0]
            month = splits[1]
            month_name = calendar.month_name[int(month)][:3]
            fileName = ('_').join(['Murree', 'weather', year, month_name]) + '.txt'
            requested_reports.append(
                {'type': report_types[args[i]], 'year': year, 'month': calendar.month_name[int(month)], 'fileName': fileName})
            i += 2
        elif args[i] == '-b':
            year = args[i + 1].split('/')[0]
            month = args[i + 1].split('/')[1]
            month_name = calendar.month_name[int(month)][:3]
            fileName = ('_').join(['Murree', 'weather', year, month_name]) + '.txt'
            requested_reports.append(
                {'type': report_types[args[i]], 'year': year, 'month': calendar.month_name[int(month)], 'fileName': fileName})
            i += 2
        elif args[i] == '-c':
            year = args[i + 1].split('/')[0]
            month = args[i + 1].split('/')[1]
            month_name = calendar.month_name[int(month)][:3]
            fileName = ('_').join(['Murree', 'weather', year, month_name]) + '.txt'
            requested_reports.append(
                {'type': report_types[args[i]], 'year': year, 'month': calendar.month_name[int(month)], 'fileName': fileName})
            i += 2
        else:
            pass

    print("Requested Reports:")
    for report in requested_reports:
        print(f'- {report}')
    return requested_reports

def parse_file(file_path):
        with open(file_path, 'r') as file:
            header = file.readline().strip().split(',')
            data = {}
            for line in file:
                values = line.strip().split(',')
                date = values[0]
                # Create dictionary with header keys
                row = {}
                for i, column in enumerate(header):
                    if i < len(values):
                        row[column] = values[i]
                data[date]=row
            return data

def parse_data(data_dir_path):
    files = os.listdir(data_dir_path)
    data = {}
    for file in files:
       parsed_file = parse_file(os.path.join(data_dir_path, file))
       data[file] = parsed_file
    return data

def calc_avg_monthly_report(file_data):
    report = {}
    highest_temps = []
    lowest_temps = []
    mean_humidities = []
    for key, value in file_data.items():
        highest_temps.append(int(value['Max TemperatureC']))
        lowest_temps.append(int(value['Min TemperatureC']))
        mean_humidities.append(int(value[' Mean Humidity']))
    report['avg_highest_temp'] = round(statistics.mean(highest_temps), 0)
    report['avg_lowest_temp'] = round(statistics.mean(lowest_temps), 0)
    report['mean_humidity'] = round(statistics.mean(mean_humidities), 0)
    print("Monthly Averages Report:")
    print(f"- Highest Average: {round(statistics.mean(highest_temps), 0)}C")
    print(f"- Lowest Average: {round(statistics.mean(lowest_temps), 0)}C")
    print(f"- Average Mean Humidity: {round(statistics.mean(mean_humidities), 0)}%")
    print("-----------------------------------------")

def calc_yearly_summary_report(file_data):

    highest_temp = 0
    highest_temp_date = ''
    lowest_temp = 0
    lowest_temp_date = ''
    most_humidity = 0
    most_humidity_date = ''

    for value in file_data.values():
        for key, val in value.items():
            high_temp = int(val['Max TemperatureC'])
            low_temp = int(val['Min TemperatureC'])
            humidity = int(val['Max Humidity'])
            if high_temp > int(highest_temp):
                highest_temp = high_temp
                highest_temp_date = key
            if low_temp < int(lowest_temp):
                lowest_temp = low_temp
                lowest_temp_date = key
            if humidity > int(most_humidity):
                most_humidity = humidity
                most_humidity_date = key
    print("Yearly Summary Report:")
    print(f"- Highest: {highest_temp}C on {highest_temp_date}")
    print(f"- Lowest: {lowest_temp}C on {lowest_temp_date}")
    print(f"- Humidity: {most_humidity}% on {most_humidity_date}")
    print("------------------------------------------------")

def calc_daily_temp_chart(month, year, file_data):
    print(f"{month} - {year}")
    for key, value in file_data.items():
        highest_temp = int(value['Max TemperatureC'])
        lowest_temp = int(value['Min TemperatureC'])
        date = key.split('-')[2]
        highest_temp_stars = ['+' for x in range(0, highest_temp)]
        lowest_temp_stars = ['+' for x in range(0, lowest_temp)]

        print(f'{date} {("").join(highest_temp_stars)} {highest_temp}C')
        print(f'{date} {("").join(lowest_temp_stars)} {lowest_temp}C')

def calc_combined_daily_bar_chart(month, year, file_data):
    print(f"{month} - {year}")
    for key, value in file_data.items():
        highest_temp = int(value['Max TemperatureC'])
        lowest_temp = int(value['Min TemperatureC'])
        date = key.split('-')[2]
        stars = ['+' for x in range(0, highest_temp + lowest_temp)]
        print(f'{date} {("").join(stars)} {lowest_temp}C - {highest_temp}C')

def calc_report(report, data):
    if report['type'] == "Monthly Averages Report":
        calc_avg_monthly_report(data)
    elif report['type'] == "Yearly Summary Report":
        calc_yearly_summary_report(data)
    elif report['type'] == "Daily Temperature Chart (Bars)":
        calc_daily_temp_chart(report['month'], report['year'], data)
    elif report['type'] == "Combined Daily Bar Chart":
        calc_combined_daily_bar_chart(report['month'], report['year'], data)
    else:
        report = {}
        return report

def generate_reports(reports, data):
    for report in reports:
        file_name = report['fileName']
        file_data = {}
        if type(file_name) is list:
            for file in file_name:
                file_data[file] = data[file] | {}
        else:
            file_data = data[file_name] | {}
        calc_report(report, file_data)
    return {}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python weatherman.py <report_type> <month/year>")
        sys.exit(1)
    data_dir_path = sys.argv[1]
    reports_args = sys.argv[2:]
    requested_reports = requested_reports(reports_args)
    parsed_data = parse_data(data_dir_path)
    reports = generate_reports(requested_reports, parsed_data)




