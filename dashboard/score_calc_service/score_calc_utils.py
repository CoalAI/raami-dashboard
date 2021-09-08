import time
from datetime import datetime

import pandas as pd
from gcloud_bq import GcloudService

service = GcloudService()
score_directory_path = '/home/ammar/deeds_scores/'


def get_all_records(county):

    query_string = f"""
    SELECT DISTINCT parcel.apn, deed.recording_date, owner.formatted_street_address as formatted_street_addres_x,
    parcel.county_name as county_name,owner.name as name, owner.second_name as second_name,
    owner.city as city_x, owner.state as state_x, owner.zip_code as zip_code_x,
    address.formatted_street_address as formatted_street_address_y, address.city as city_y,
    address.state as state_y, address.zip_code as zip_code_y, owner.owner_occupied as owner_occupied
    from `heroic-habitat-279715.owners.parcels` as parcel join `heroic-habitat-279715.owners.owners` as owner
    ON parcel.apn = owner.apn and CAST(parcel.fips AS STRING) = CAST(owner.fips AS STRING)
    JOIN `heroic-habitat-279715.owners.addresses` as address
    ON parcel.apn=address.apn and CAST(parcel.fips AS STRING) = CAST(address.fips AS STRING)
    JOIN `heroic-habitat-279715.owners.deeds` as deed ON deed.apn=parcel.apn and
    CAST(deed.fips AS STRING) = CAST(parcel.fips AS STRING)
    WHERE parcel.county_name = '{county}'

    """

    return service.execute_query_q(query_string)


def get_deeds_records(county, now_date='2018-01-01'):
    deed_records = f"""
    SELECT DISTINCT deed.apn FROM `heroic-habitat-279715.owners.parcels` as parcel
    join `heroic-habitat-279715.owners.deeds` as deed on parcel.apn = deed.apn and recording_date <'{now_date}'
    where parcel.county_name = '{county}'
    """

    return service.execute_query_q(deed_records)


def get_deeds_records_with_state(county, state, now_date='2018-01-01'):
    deed_records = f"""
    SELECT DISTINCT deed.apn FROM `heroic-habitat-279715.owners.parcels` as parcel
    join `heroic-habitat-279715.owners.deeds` as deed on parcel.apn = deed.apn
    join `heroic-habitat-279715.owners.addresses` as address on parcel.apn=address.apn
    where parcel.county_name = '{county}' and recording_date <'{now_date}' and address.state like '{state}'
    """

    return service.execute_query_q(deed_records)


def compute_score(apns, delta, months, now_date='2018-01-01'):
    score_cal_query = f"""
    SELECT apn,
        CASE
            WHEN counts > 3 THEN
            CASE
                WHEN days_count>{delta} THEN 0
                WHEN months_count>.95 AND days_count<=0 THEN 100
                WHEN months_count>.90 AND days_count<=0 THEN 99
                WHEN months_count>.85 AND days_count<=0 THEN 98
                WHEN months_count>.70 AND days_count<=0 THEN 85
                WHEN months_count>.50 AND days_count<=0 THEN 75
                WHEN days_count<=0 THEN 50
                WHEN months_count>.85 THEN 97
                WHEN months_count>.65 THEN
                CASE
                    WHEN (100 - (days_count/{delta}*100))*1.1 > 97 THEN 97
                    ELSE (100 - (days_count/{delta}*100))*1.1
                END
                ELSE 100 - (days_count/{delta}*100)
            END
            ELSE 0
        END AS score
        FROM (
            SELECT apn,
            DATE_DIFF( DATE_ADD(last_recording_date, INTERVAL CAST(avg_months AS INT64) MONTH), '{now_date}', DAY) AS days_count,
            sum_months/counts AS months_count, counts
            FROM (
                SELECT apn,
                MAX(PARSE_DATE('%Y-%m-%d', recording_date)) AS last_recording_date,
                AVG(months) AS avg_months,
                COUNT(CASE WHEN months < {months} THEN months END) AS sum_months,
                COUNT(*) AS counts
                FROM (
                    SELECT t.apn, t.recording_date,t.next_date,
                        CASE
                            WHEN t.next_date IS NOT NULL THEN
                            DATE_DIFF(PARSE_DATE('%Y-%m-%d', t.next_date), PARSE_DATE('%Y-%m-%d', t.recording_date), MONTH)
                            ELSE 0
                        END AS months
                    FROM (
                        SELECT apn, recording_date,
                        CASE
                            WHEN LEAD(apn) OVER (ORDER BY apn, recording_date) = apn THEN
                            LEAD(recording_date) OVER (ORDER BY apn, recording_date)
                            ELSE NULL
                        END AS next_date
                        FROM (
                            SELECT DISTINCT apn, recording_date
                            FROM `heroic-habitat-279715.owners.deeds`
                            WHERE SAFE.PARSE_DATE('%Y-%m-%d', recording_date) IS NOT NULL
                            AND apn IN UNNEST(@ids) AND recording_date < '{now_date}'
                        ) AS t0
                        ORDER BY apn, recording_date
                    ) as t
                ) AS t2
                GROUP BY apn
            ) AS t3
        ) t4
    """
    return service.execute_with_params(score_cal_query, "ids", apns)


def main(county_name, state, _date, delta, months):

    start = time.time()

    now_date = datetime.today().strftime('%Y-%m-%d')
    if _date:
        now_date = _date

    delta = int(delta)
    months = int(months)

    print(f'county: {county_name} state: {state} now_date: {now_date} delta: {delta} months: {months}')

    apns = None
    if state:
        apns = get_deeds_records_with_state(county_name, state, now_date)
    else:
        apns = get_deeds_records(county_name, now_date)

    no_of_apns = len(apns)
    no_of_dfs = int(float(no_of_apns) / 100000)

    print(no_of_apns)
    print(no_of_dfs)

    if no_of_apns < 120000:
        final_df = compute_score(list(apns['apn']), delta=delta, months=months)
    else:
        start = 0
        end = 100000
        score_dfs = []

        while start < no_of_apns:
            print(f'start: {start} , end: {end}')
            _df = compute_score(list(apns.loc[start: end, 'apn']), delta=delta, months=months)
            score_dfs.append(_df)
            start = end + 1
            end = end + 100000 if end + 100000 < no_of_apns else no_of_apns - 1

        final_df = pd.concat(score_dfs)

    other_colums = get_all_records(county_name)

    final_df2 = final_df.merge(other_colums, on='apn', how='left')
    final_df2.to_csv(f'{score_directory_path}scores_{county_name}_[{delta}:{months}].csv')


def get_counties():
    query_string = """
    SELECT DISTINCT county_name FROM `heroic-habitat-279715.owners.parcels` as parcel
    """
    return service.execute_query_q(query_string)['county_name'].tolist()


def get_states():
    query_string = """
    SELECT DISTINCT state FROM `heroic-habitat-279715.owners.addresses` as address
    """
    return service.execute_query_q(query_string)['state'].tolist()
