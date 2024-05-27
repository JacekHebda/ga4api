from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest
from google.auth import load_credentials_from_file
from datetime import datetime, timedelta
import csv

KEY_FILE_PATH = 'service-account-key.json'

# GA4 property IDs
PARKIET = '355480364'
WSZYSTKIE = '355490887'

properties = [PARKIET]
metrics=['totalUsers', 'activeUsers', 'newUsers', 'screenPageViews', 'sessions']
dimensions_list=[['yearMonth', 'hostName']]
#TODO add all the desired reports to the list above

def monthly_intervals(start_date, end_date):
    """
    Returns monthly intervals from the 1st to the last day of the month between start_date and end_date.

    :param start_date: Start date in the format 'YYYY-MM-DD'
    :param end_date: End date in the format 'YYYY-MM-DD'
    :return: List of tuples where each tuple contains (start_of_month, end_of_month)
    """
    intervals = []

    # Convert string dates to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Initialize the current date to the first day of the month of the start date
    current_date = start_date.replace(day=1)

    while current_date <= end_date:
        # Calculate the start and end of the current month
        start_of_month = current_date
        next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)  # first day of the next month
        end_of_month = next_month - timedelta(days=1)

        # Adjust the start_of_month if it's before the provided start_date
        if start_of_month < start_date:
            start_of_month = start_date

        # Adjust the end_of_month if it's after the provided end_date
        if end_of_month > end_date:
            end_of_month = end_date

        # Append the interval as a tuple (start_of_month, end_of_month)
        intervals.append((start_of_month.strftime('%Y-%m-%d'), end_of_month.strftime('%Y-%m-%d')))
        
        # Move to the first day of the next month
        current_date = next_month

    return intervals

def get_ga4_data(start_date, end_date, property_id, dimensions, metrics):
    # Load credentials from the service account key file
    credentials, _ = load_credentials_from_file(KEY_FILE_PATH)

    # Create a client
    client = BetaAnalyticsDataClient(credentials=credentials)

    with open(f'{property_id}_{[dimension for dimension in dimensions]}.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(dimensions + metrics)
        
        dimensions_object = [{'name': dimension} for dimension in dimensions]
        metrics_object = [{'name': metric} for metric in metrics]

        for interval in monthly_intervals(start_date, end_date):
            # Create a request to the API
            request = RunReportRequest(
                property=f'properties/{property_id}',
                dimensions=dimensions_object,
                metrics=metrics_object,
                date_ranges=[{'start_date': f'{interval[0]}', 'end_date': f'{interval[1]}'}]
            )

            # Fetch the report
            response = client.run_report(request)   

            # Write data rows
            for row in response.rows:
                writer.writerow([dimension_value.value for dimension_value in row.dimension_values]
                                  + [metric_value.value for metric_value in row.metric_values])

if __name__ == '__main__':

    for property in properties:
        for dimensions in dimensions_list:
            get_ga4_data(start_date='2023-03-01', end_date='2024-05-26', 
                         property_id=property, dimensions=dimensions, metrics=metrics)
