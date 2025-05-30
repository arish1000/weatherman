import os
import sys
from constants import REPORT_TYPES
import calendar
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union


class ReportGenerator:
    @staticmethod
    def generate_monthly_averages_report(results):
        print("Monthly Averages Report:")
        print(f"- Highest Average: {results.avg_highest_temp}C")
        print(f"- Lowest Average: {results.avg_lowest_temp}C")
        print(f"- Average Mean Humidity: {results.avg_mean_humidity}%")
        print("-" * 40)

    @staticmethod
    def generate_yearly_summary_report(results):
        print("Yearly Summary Report:")
        print(f"- Highest: {results.highest_temp}C on {results.highest_temp_date}")
        print(f"- Lowest: {results.lowest_temp}C on {results.lowest_temp_date}")
        print(f"- Humidity: {results.most_humidity}% on {results.most_humidity_date}")
        print("-" * 48)

    @staticmethod
    def generate_daily_temperature_chart(weather_data, month: str, year: str) -> None:
        print(f"{month} - {year}")


        for date, reading in weather_data.readings.items():
            day = date.split('-')[2]

            high_bars = '+' * reading.max_temperature
            low_bars = '+' * reading.min_temperature

            print(f"{day} {high_bars} {reading.max_temperature}C")
            print(f"{day} {low_bars} {reading.min_temperature}C")

    @staticmethod
    def generate_combined_daily_bar_chart(weather_data, month: str, year: str) -> None:
        print(f"{month} - {year}")

        for date, reading in weather_data.readings.items():
            day = date.split('-')[2]
            total_bars = '+' * (reading.max_temperature + reading.min_temperature)
            print(f"{day} {total_bars} {reading.min_temperature}C - {reading.max_temperature}C")

@dataclass
class CalculationResults:
    avg_highest_temp: Optional[float] = None
    avg_lowest_temp: Optional[float] = None
    avg_mean_humidity: Optional[float] = None
    highest_temp: Optional[int] = None
    highest_temp_date: Optional[str] = None
    lowest_temp: Optional[int] = None
    lowest_temp_date: Optional[str] = None
    most_humidity: Optional[int] = None
    most_humidity_date: Optional[str] = None



class WeatherCalculator:

    @staticmethod
    def calculate_monthly_averages(weather_data):
        readings = weather_data.get_all_readings()

        if not readings:
            return CalculationResults()

        highest_temps = [reading.max_temperature for reading in readings]
        lowest_temps = [reading.min_temperature for reading in readings]
        mean_humidities = [reading.mean_humidity for reading in readings]

        return CalculationResults(
            avg_highest_temp=round(statistics.mean(highest_temps), 1),
            avg_lowest_temp=round(statistics.mean(lowest_temps), 1),
            avg_mean_humidity=round(statistics.mean(mean_humidities), 1)
        )

    @staticmethod
    def calculate_yearly_extremes(all_weather_data):
        results = CalculationResults()
        results.highest_temp = float('-inf')
        results.lowest_temp = float('inf')
        results.most_humidity = 0

        for weather_data in all_weather_data.values():
            for reading in weather_data.get_all_readings():
                if reading.max_temperature > results.highest_temp:
                    results.highest_temp = reading.max_temperature
                    results.highest_temp_date = reading.date

                if reading.min_temperature < results.lowest_temp:
                    results.lowest_temp = reading.min_temperature
                    results.lowest_temp_date = reading.date

                if reading.max_humidity > results.most_humidity:
                    results.most_humidity = reading.max_humidity
                    results.most_humidity_date = reading.date

        return results


@dataclass
class ReportRequest:
    report_type: str
    year: str
    month: Optional[str] = None
    file_names: Union[str, List[str]] = None


    @staticmethod
    def process_report_requests(requests, data):
        for request in requests:
            combined_data = WeatherData()
            if isinstance(request.file_names, list):
                all_weather_data = {}
                for file_name in request.file_names:
                    if file_name in data:
                        all_weather_data[file_name] = data[file_name]
                        for reading in data[file_name].get_all_readings():
                            combined_data.add_reading(reading)
            else:
                if request.file_names in data:
                    combined_data = data[request.file_names]
                    all_weather_data = {request.file_names: combined_data}
                else:
                    print(f"Warning: File {request.file_names} not found")
                    return


            if request.report_type == 'Monthly Averages Report':
                results = WeatherCalculator.calculate_monthly_averages(combined_data)
                ReportGenerator.generate_monthly_averages_report(results)

            elif request.report_type == 'Yearly Summary Report':
                results = WeatherCalculator.calculate_yearly_extremes(all_weather_data)
                ReportGenerator.generate_yearly_summary_report(results)

            elif request.report_type == 'Daily Temperature Chart (Bars)':
                ReportGenerator.generate_daily_temperature_chart(
                    combined_data, request.month, request.year
                )

            elif request.report_type == 'Combined Daily Bar Chart':
                ReportGenerator.generate_combined_daily_bar_chart(
                    combined_data, request.month, request.year
                )

    @staticmethod
    def print_requested_reports(reports):
        for request in reports:
            print(f"- {request.report_type} for {request.year}" +
                  (f"/{request.month}" if request.month else ""))


class ArgumentParser:
    @staticmethod
    def generate_file_name(year: str, month: Optional[str] = None):
        if month is None:
            file_names = []
            for month in range(1, 13):
                month_abr = calendar.month_name[month][:3]
                file_name = f"Murree_weather_{year}_{month_abr}.txt"
                file_names.append(file_name)
            return file_names
        else:

            month_abr = calendar.month_name[int(month)][:3]
            file_name = f"Murree_weather_{year}_{month_abr}.txt"
            return file_name

    @staticmethod
    def parse_arguments(args: List[str]):
        requests = []
        i = 0
        while i < len(args):
            if args[i] in REPORT_TYPES:
                if i + 1 >= len(args):
                    print(f"Error: Missing argument for {args[i]}")
                    i += 1
                    continue
                date_parts = args[i + 1].split('/')
                year = date_parts[0]
                month = date_parts[1] if len(date_parts) > 1 else None

                month_name = None
                if month:
                    month_name = calendar.month_name[int(month)]
                file_names = ArgumentParser.generate_file_name(year, month)
                request = ReportRequest(
                    report_type=REPORT_TYPES[args[i]],
                    year=year,
                    month=month_name,
                    file_names=file_names
                )
                requests.append(request)
                i += 2
            else:
                i += 1

        return requests


@dataclass()
class WeatherReading:
    date: str
    max_temperature: int
    min_temperature: int
    max_humidity: int
    mean_humidity: int

    @classmethod
    def from_csv_row(cls, date: str, row_data: Dict[str, str]):
        return cls( date=date,
            max_temperature=int(row_data.get('Max TemperatureC', 0)),
            min_temperature=int(row_data.get('Min TemperatureC', 0)),
            max_humidity=int(row_data.get('Max Humidity', 0)),
            mean_humidity=int(row_data.get(' Mean Humidity', 0)))


@dataclass
class WeatherData:
   readings: Dict[str, WeatherReading] = field(default_factory=dict)

   def add_reading(self, reading: WeatherReading):
       self.readings[reading.date] = reading

   def get_reading(self, date):
        return self.readings[date]

   def get_all_readings(self):
       return list(self.readings.values())


class WeatherDataParser:

    @staticmethod
    def parse_csv_file(file_path):
        weather_data = WeatherData()
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                header = file.readline().strip().split(',')

                for line in file:
                    values = line.strip().split(',')
                    if len(values) < len(header):
                        continue
                    date = values[0]
                    row_data = {header[i] : values[i] for i in range(len(header))}
                    reading = WeatherReading.from_csv_row(date, row_data)
                    weather_data.add_reading(reading)


        except (FileNotFoundError, ValueError, IndexError) as e:
            print(f"Error parsing file {file_path}: {e}")
        return weather_data


    @staticmethod
    def parse_data_directory(data_dir_path):
        all_data = {}

        if not os.path.exists(data_dir_path):
            print(f"Error: Directory {data_dir_path} does not exist")
            return all_data

        try:
            files = os.listdir(data_dir_path)
            for file in files:
                file_path = os.path.join(data_dir_path, file)
                file_data = WeatherDataParser.parse_csv_file(file_path)
                all_data[file] = file_data
        except OSError as e:
            print(f"Error: Unable to open directory {data_dir_path}: {e}")

        return all_data


def main():

    if len(sys.argv) < 2:
        print("Usage: python weatherman.py <data_directory> <report_options>")
        print("\nOptions:")
        print("  -e YEAR        : Yearly summary report")
        print("  -a YEAR/MONTH  : Monthly averages report")
        print("  -b YEAR/MONTH  : Daily temperature chart")
        print("  -c YEAR/MONTH  : Combined daily bar chart")
        sys.exit(1)

    data_dir_path = sys.argv[1]
    reports_args = sys.argv[2:]
    print("Data Directory:", data_dir_path)
    print("Report Options:", reports_args)

    print("Loading weather data...")
    data = WeatherDataParser.parse_data_directory(data_dir_path)

    if not data:
        print("No data found")
        sys.exit(1)

    report_requests = ArgumentParser.parse_arguments(reports_args)
    if not report_requests:
        print("No reports found")
        sys.exit(1)
    else:
        print("\nRequested Reports:")
        ReportRequest.print_requested_reports(report_requests)

    ReportRequest.process_report_requests(report_requests, data)





if __name__ == "__main__":
    main()





