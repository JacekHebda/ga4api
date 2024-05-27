from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest
from google.auth import load_credentials_from_file
from datetime import datetime, timedelta
import csv

KEY_FILE_PATH = 'service-account-key.json'

# parkiet GA4 property ID
PROPERTY_ID = '355480364'

def get_ga4_data(start_date, end_date):
    # Load credentials from the service account key file
    credentials, _ = load_credentials_from_file(KEY_FILE_PATH)

    # Create a client
    client = BetaAnalyticsDataClient(credentials=credentials)

    # Create a request to the API
    request = RunReportRequest(
        property=f'properties/{PROPERTY_ID}',
        dimensions=[{'name': 'yearMonth'}, 
                    {'name': 'hostName'}],
        metrics=[{'name': 'totalUsers'}, 
                 {'name': 'activeUsers'},
                 {'name': 'newUsers'},
                 {'name': 'screenPageViews'},
                 {'name': 'sessions'}],
        date_ranges=[{'start_date': f'{start_date}', 'end_date': f'{end_date}'}]
    )

     # Fetch the report
    response = client.run_report(request)

    with open(f'hostname_{start_date}_{end_date}.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(['yearMonth', 'hostName', 
                         'totalUsers', 'activeUsers', 'newUsers', 'screenPageViews', 'sessions'])
        
        # Write data rows
        for row in response.rows:
            writer.writerow([row.dimension_values[0].value, row.dimension_values[1].value, 
                             row.metric_values[0].value, row.metric_values[1].value, 
                             row.metric_values[2].value, row.metric_values[3].value,
                             row.metric_values[4].value])

if __name__ == '__main__':

    today = datetime.today().date()
    start_date = today.replace(day=1) if today.day > 4 else (today - timedelta(months=1)).replace(day=1)
    end_date = today - timedelta(days=1) if today.day > 4 else today.replace(day=1) - timedelta(days=1)
    
    get_ga4_data('2024-03-01', '2024-03-31')
    get_ga4_data('2024-04-01', '2024-04-30')
    get_ga4_data(start_date=start_date, end_date=end_date)