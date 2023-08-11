import json

from api_connectors.kairosdb import KairosDBAPIClient

if __name__ == "__main__":
    API_ENDPOINT = "http://<ip>:<port>"
    kairos_api = KairosDBAPIClient(api_endpoint=API_ENDPOINT)

    print(f"{kairos_api.version}")
    print(f"{kairos_api.health_status}")
    print(f"{kairos_api.health_check}")
    result = kairos_api.query_metrics(
        metrics="1220006.SIN.B1009_PESOACUMULADO_TOTAL",
        start_datetime="2023-08-11 00:00:00",
        end_datetime="2023-08-11 00:01:00",
    )
    print(json.dumps(result, indent=2))
