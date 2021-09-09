import google.auth
from django.conf import settings
from google.cloud import bigquery, bigquery_storage


class GcloudService:

    def __init__(self):
        credentials, your_project_id = google.auth.load_credentials_from_file(settings.GCLOUD_FILE)
        self.bqclient = bigquery.Client(credentials=credentials, project=your_project_id)
        self.bqstorageclient = bigquery_storage.BigQueryReadClient(credentials=credentials)

    def execute_query_q(self, q):
        query_string = q
        self.bqclient.query(query_string)
        other_columns = (
            self.bqclient.query(query_string)
            .result()
            .to_dataframe(bqstorage_client=self.bqstorageclient)
        )

        return other_columns

    def execute_with_params(self, query, param_name, param_val):
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ArrayQueryParameter(param_name, "STRING", param_val), ])

        deeds_dataframe = (
            self.bqclient.query(query, job_config=job_config, timeout=300000)
                .result()
                .to_dataframe(bqstorage_client=self.bqstorageclient)
        )

        return deeds_dataframe
