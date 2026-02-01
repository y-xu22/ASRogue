import os
import datetime
import requests



date = [
    datetime.date(2024, 10, 5), datetime.date(2024, 10, 4), datetime.date(2024, 10, 3), datetime.date(2024, 10, 2), datetime.date(2024, 10, 1),
    datetime.date(2024, 9, 30), datetime.date(2024, 9, 29), datetime.date(2024, 9, 28), datetime.date(2024, 9, 27),
    datetime.date(2024, 9, 26), datetime.date(2024, 9, 25), datetime.date(2024, 9, 24), 
    datetime.date(2024, 9, 21), datetime.date(2024, 9, 20), datetime.date(2024, 9, 19), datetime.date(2024, 9, 18), datetime.date(2024, 9, 17),
    datetime.date(2024, 9, 14), datetime.date(2024, 9, 13), datetime.date(2024, 9, 12), datetime.date(2024, 9, 11), datetime.date(2024, 9, 10), 
    datetime.date(2024, 9, 5), datetime.date(2024, 9, 4), datetime.date(2024, 9, 3), datetime.date(2024, 9, 2), datetime.date(2024, 9, 1)
]

for target_date in date:
    date_str = target_date.strftime("%Y%m%d")  # 20250930
    year_month = target_date.strftime("%Y.%m") # 2025.09
    year_month_rv = target_date.strftime("%Y.%m")
    time_str = "0000"
    
    BASE_DIR = "BGP RIB/bgp_rib_" + date_str
    os.makedirs(BASE_DIR, exist_ok=True)


    ripe_rrcs = [
        "rrc00", "rrc01", "rrc03", "rrc04", "rrc05", "rrc06", "rrc07", "rrc10", "rrc11",
        "rrc12", "rrc13", "rrc14", "rrc15", "rrc16", "rrc18", "rrc19", "rrc20", "rrc21"
        # "rrc00"
    ]

    def download_file(url: str, out_path: str):
        if os.path.exists(out_path):
            return
        try:
            resp = requests.get(url, stream=True, timeout=60)
            if resp.status_code != 200:
                return
            with open(out_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
        except Exception as e:
            print(f"[!] {url}: {e}")

    for rrc in ripe_rrcs:
        url = f"https://data.ris.ripe.net/{rrc}/{year_month}/bview.{date_str}.{time_str}.gz"
        out_name = f"ripe_{rrc}_bview_{date_str}_{time_str}.gz"
        out_path = os.path.join(BASE_DIR, out_name)
        download_file(url, out_path)

    routeviews_collectors = [
        "route-views.eqix",
        "route-views.isc",
        "route-views.kixp",
        "route-views.linx",
        "route-views.napafrica",
        "route-views.nwax",
        "route-views.perth",
        "route-views2",
        "route-views3",
        # "route-views",
        "route-views.sfmix",
        "route-views.sg",
        "route-views.soxrs",
        "route-views.sydney",
        "route-views.telxatl",
        "route-views.wide",
    ]

    rv_base = "http://archive.routeviews.org"

    for collector in routeviews_collectors:
        url = f"{rv_base}/{collector}/bgpdata/{year_month_rv}/RIBS/rib.{date_str}.{time_str}.bz2"
        out_name = f"{collector}_rib_{date_str}_{time_str}.bz2"
        out_path = os.path.join(BASE_DIR, out_name)
        download_file(url, out_path)

