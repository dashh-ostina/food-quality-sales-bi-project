from pathlib import Path
import csv
import random
import math
from datetime import date, timedelta
from bisect import bisect_right
from collections import defaultdict

SEED = 42
random.seed(SEED)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = date(2024, 1, 1)
END_DATE = date(2025, 12, 31)

PRODUCTS = [
    ("P001", "Greek Yogurt Strawberry 150g", "Dairy", "Yogurt", 150, 21, 89.0, 43.0, "2023-01-15", 72),
    ("P002", "Greek Yogurt Blueberry 150g", "Dairy", "Yogurt", 150, 21, 92.0, 44.0, "2023-02-01", 65),
    ("P003", "Natural Yogurt 150g", "Dairy", "Yogurt", 150, 21, 79.0, 38.0, "2022-09-01", 82),
    ("P004", "Drinking Yogurt Strawberry 270g", "Dairy", "Drinking Yogurt", 270, 18, 109.0, 54.0, "2023-03-10", 78),
    ("P005", "Drinking Yogurt Peach 270g", "Dairy", "Drinking Yogurt", 270, 18, 109.0, 54.0, "2023-03-10", 70),
    ("P006", "Kefir 1% 500g", "Dairy", "Kefir", 500, 14, 99.0, 51.0, "2022-05-01", 90),

    ("P007", "Orange Juice 1L", "Beverages", "Juice", 1000, 180, 169.0, 91.0, "2022-02-01", 84),
    ("P008", "Apple Juice 1L", "Beverages", "Juice", 1000, 180, 159.0, 86.0, "2022-02-01", 88),
    ("P009", "Berry Juice 1L", "Beverages", "Juice", 1000, 180, 179.0, 96.0, "2023-01-20", 61),
    ("P010", "Iced Tea Lemon 500ml", "Beverages", "Iced Tea", 500, 270, 109.0, 51.0, "2023-04-01", 96),
    ("P011", "Iced Tea Peach 500ml", "Beverages", "Iced Tea", 500, 270, 109.0, 51.0, "2023-04-01", 87),
    ("P012", "Sparkling Lemonade 500ml", "Beverages", "Soft Drink", 500, 180, 119.0, 57.0, "2023-05-01", 92),

    ("P013", "Granola Bar Nuts 40g", "Snacks", "Granola Bar", 40, 270, 69.0, 29.0, "2023-01-01", 76),
    ("P014", "Granola Bar Chocolate 40g", "Snacks", "Granola Bar", 40, 270, 72.0, 31.0, "2023-01-01", 105),
    ("P015", "Wholegrain Crackers 100g", "Snacks", "Crackers", 100, 240, 99.0, 46.0, "2022-08-01", 70),
    ("P016", "Cheese Crackers 100g", "Snacks", "Crackers", 100, 240, 105.0, 49.0, "2022-08-01", 66),

    ("P017", "Granola Berries 300g", "Breakfast", "Granola", 300, 300, 219.0, 111.0, "2023-02-15", 58),
    ("P018", "Granola Nuts 300g", "Breakfast", "Granola", 300, 300, 229.0, 116.0, "2023-02-15", 54),
    ("P019", "Corn Flakes 300g", "Breakfast", "Cereal", 300, 360, 179.0, 82.0, "2022-01-15", 68),
    ("P020", "Chocolate Cereal 300g", "Breakfast", "Cereal", 300, 360, 199.0, 92.0, "2022-01-15", 73),

    ("P021", "Chocolate Pudding 150g", "Desserts", "Pudding", 150, 30, 94.0, 45.0, "2023-06-01", 64),
    ("P022", "Vanilla Pudding 150g", "Desserts", "Pudding", 150, 30, 91.0, 43.0, "2023-06-01", 60),
    ("P023", "Fruit Dessert Mango 120g", "Desserts", "Fruit Dessert", 120, 45, 119.0, 58.0, "2024-02-01", 47),
    ("P024", "Fruit Dessert Berry 120g", "Desserts", "Fruit Dessert", 120, 45, 119.0, 58.0, "2024-02-01", 50),
]

REGIONS = [
    ("R01", "Москва", "Центральный", 1.35),
    ("R02", "Московская область", "Центральный", 1.15),
    ("R03", "Санкт-Петербург", "Северо-Западный", 1.10),
    ("R04", "Республика Татарстан", "Приволжский", 0.86),
    ("R05", "Свердловская область", "Уральский", 0.81),
    ("R06", "Новосибирская область", "Сибирский", 0.76),
]

CHANNELS = [
    ("C01", "Федеральные сети", 1.30, 0.060),
    ("C02", "Региональные сети", 0.92, 0.045),
    ("C03", "E-commerce", 0.66, 0.085),
    ("C04", "Дистрибьюторы", 0.78, 0.115),
]

PLANTS = [
    ("PL01", "Московская площадка", "Москва", 1_900_000),
    ("PL02", "Тульская площадка", "Тула", 1_650_000),
    ("PL03", "Нижегородская площадка", "Нижний Новгород", 1_450_000),
]

PLANT_BY_CATEGORY = {
    "Dairy": "PL01",
    "Desserts": "PL01",
    "Beverages": "PL02",
    "Snacks": "PL03",
    "Breakfast": "PL03",
}

SEASONALITY = {
    "Dairy":      {1:1.00,2:1.00,3:1.02,4:1.03,5:1.04,6:1.02,7:0.99,8:0.99,9:1.04,10:1.05,11:1.04,12:1.05},
    "Beverages":  {1:0.70,2:0.74,3:0.83,4:0.96,5:1.15,6:1.35,7:1.52,8:1.45,9:1.18,10:0.95,11:0.80,12:0.73},
    "Snacks":     {1:1.04,2:1.01,3:1.00,4:0.98,5:0.96,6:0.94,7:0.93,8:0.96,9:1.04,10:1.08,11:1.11,12:1.18},
    "Breakfast":  {1:1.12,2:1.08,3:1.04,4:0.99,5:0.94,6:0.90,7:0.89,8:0.93,9:1.12,10:1.10,11:1.08,12:1.05},
    "Desserts":   {1:1.12,2:1.10,3:1.05,4:1.00,5:0.96,6:0.91,7:0.89,8:0.91,9:0.98,10:1.03,11:1.08,12:1.17},
}

DEFECTS_BY_CATEGORY = {
    "Dairy": [("Packaging", 0.28), ("Labeling", 0.13), ("Net Weight", 0.12),
              ("Appearance", 0.12), ("Taste / Smell", 0.13), ("Consistency", 0.17),
              ("Microbiological", 0.05)],
    "Beverages": [("Packaging", 0.42), ("Labeling", 0.16), ("Net Weight", 0.12),
                  ("Appearance", 0.08), ("Taste / Smell", 0.10), ("Consistency", 0.04),
                  ("Microbiological", 0.08)],
    "Snacks": [("Packaging", 0.40), ("Labeling", 0.15), ("Net Weight", 0.16),
               ("Appearance", 0.17), ("Taste / Smell", 0.08), ("Consistency", 0.02),
               ("Microbiological", 0.02)],
    "Breakfast": [("Packaging", 0.36), ("Labeling", 0.16), ("Net Weight", 0.16),
                  ("Appearance", 0.16), ("Taste / Smell", 0.10), ("Consistency", 0.03),
                  ("Microbiological", 0.03)],
    "Desserts": [("Packaging", 0.27), ("Labeling", 0.12), ("Net Weight", 0.11),
                 ("Appearance", 0.14), ("Taste / Smell", 0.13), ("Consistency", 0.18),
                 ("Microbiological", 0.05)],
}

SEVERITY = {
    "Packaging": ["Low", "Medium", "Medium", "High"],
    "Labeling": ["Low", "Low", "Medium"],
    "Net Weight": ["Medium", "Medium", "High"],
    "Appearance": ["Low", "Medium"],
    "Taste / Smell": ["Medium", "High", "High"],
    "Consistency": ["Low", "Medium", "High"],
    "Microbiological": ["Critical"],
}

COMPLAINT_TYPES = {
    "Packaging": "Packaging / leakage",
    "Labeling": "Labeling",
    "Net Weight": "Underweight",
    "Appearance": "Appearance",
    "Taste / Smell": "Taste / smell",
    "Consistency": "Consistency",
    "Microbiological": "Product safety",
}

PRODUCT = {p[0]: {
    "product_name": p[1], "category": p[2], "subcategory": p[3],
    "package_size_g": p[4], "shelf_life_days": p[5],
    "list_price": p[6], "standard_cost": p[7],
    "launch_date": p[8], "base_daily_units": p[9]
} for p in PRODUCTS}

REGION_FACTOR = {r[0]: r[3] for r in REGIONS}
CHANNEL_FACTOR = {c[0]: c[2] for c in CHANNELS}
CHANNEL_DISCOUNT = {c[0]: c[3] for c in CHANNELS}

def date_id(d):
    return int(d.strftime("%Y%m%d"))

def daterange(start, end):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)

def weighted_choice(items):
    x = random.random()
    total = 0.0
    for name, weight in items:
        total += weight
        if x <= total:
            return name
    return items[-1][0]

def write_csv(filename, header, rows):
    with open(DATA_DIR / filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

def generate_dimensions():
    product_rows = []
    for p in PRODUCTS:
        product_rows.append(p[:-1])
    write_csv(
        "dim_product.csv",
        ["product_id","product_name","category","subcategory","package_size_g",
         "shelf_life_days","list_price_rub","standard_cost_rub","launch_date"],
        product_rows
    )

    date_rows = []
    for d in daterange(START_DATE, END_DATE):
        date_rows.append([
            date_id(d), d.isoformat(), d.year, f"Q{((d.month-1)//3)+1}",
            d.month, d.strftime("%B"), d.isocalendar().week,
            d.strftime("%A"), 1 if d.weekday() >= 5 else 0
        ])
    write_csv(
        "dim_date.csv",
        ["date_id","date","year","quarter","month_num","month_name",
         "week_num","day_of_week","is_weekend"],
        date_rows
    )

    write_csv(
        "dim_region.csv",
        ["region_id","region_name","federal_district"],
        [(r[0], r[1], r[2]) for r in REGIONS]
    )
    write_csv(
        "dim_channel.csv",
        ["channel_id","channel_name"],
        [(c[0], c[1]) for c in CHANNELS]
    )
    write_csv(
        "dim_plant.csv",
        ["plant_id","plant_name","city","monthly_capacity_units"],
        PLANTS
    )

def generate_sales():
    rows = []
    sales_id = 1
    for d in daterange(START_DATE, END_DATE):
        progress = (d - START_DATE).days / max(1, (END_DATE - START_DATE).days)
        trend = 1.0 + 0.12 * progress

        for product_id, meta in PRODUCT.items():
            if d < date.fromisoformat(meta["launch_date"]):
                continue

            season = SEASONALITY[meta["category"]][d.month]
            price_factor = 1.00 if d.year == 2024 else 1.055
            cost_factor = 1.00 if d.year == 2024 else 1.040

            for region_id, _, _, _ in REGIONS:
                for channel_id, _, _, _ in CHANNELS:
                    active_prob = 0.31
                    if channel_id == "C01":
                        active_prob += 0.08
                    if region_id in ("R01", "R02", "R03"):
                        active_prob += 0.04
                    if random.random() > active_prob:
                        continue

                    weekend = 1.0
                    if d.weekday() >= 5:
                        weekend = 1.08 if channel_id == "C03" else 1.02

                    noise = max(0.55, random.gauss(1.0, 0.18))
                    demand = (meta["base_daily_units"] * REGION_FACTOR[region_id] *
                              CHANNEL_FACTOR[channel_id] * season * trend * weekend * noise)

                    # 2025 growth in e-commerce and selected eastern regions
                    if d.year == 2025 and channel_id == "C03":
                        demand *= 1.15
                    if d.year == 2025 and region_id in ("R05", "R06"):
                        demand *= 1.08

                    units = max(1, int(round(demand)))
                    unit_price = meta["list_price"] * price_factor
                    gross = units * unit_price

                    discount_rate = max(
                        0.0,
                        CHANNEL_DISCOUNT[channel_id] + random.gauss(0, 0.012)
                    )
                    discount = gross * discount_rate
                    net = gross - discount

                    unit_cost = meta["standard_cost"] * cost_factor * random.uniform(0.985, 1.020)
                    cost = units * unit_cost

                    rows.append([
                        f"S{sales_id:07d}", date_id(d), product_id, region_id, channel_id,
                        units, round(gross, 2), round(discount, 2),
                        round(net, 2), round(cost, 2)
                    ])
                    sales_id += 1

    write_csv(
        "fact_sales.csv",
        ["sales_id","date_id","product_id","region_id","channel_id",
         "units_sold","gross_revenue_rub","discount_amount_rub",
         "net_revenue_rub","cost_amount_rub"],
        rows
    )
    return rows

def generate_production_and_quality():
    production_rows = []
    quality_rows = []
    batches_by_product = defaultdict(list)

    batch_num = 1
    quality_num = 1

    for product_id, meta in PRODUCT.items():
        plant_id = PLANT_BY_CATEGORY[meta["category"]]
        d = max(START_DATE, date.fromisoformat(meta["launch_date"]))

        while d <= END_DATE:
            base_volume = 7200 + meta["base_daily_units"] * 45
            season = SEASONALITY[meta["category"]][d.month]
            produced = int(base_volume * season * random.uniform(0.82, 1.18))

            base_reject_rate = random.uniform(0.006, 0.014)

            # Controlled scenario 1:
            # packaging problem at PL02 in summer 2025, strongest for P010-P012
            beverage_anomaly = (
                plant_id == "PL02"
                and product_id in ("P010", "P011", "P012")
                and date(2025, 6, 15) <= d <= date(2025, 9, 15)
            )
            if beverage_anomaly:
                base_reject_rate = random.uniform(0.040, 0.065)

            # Controlled scenario 2:
            # packaging issue for a high-selling granola bar
            bar_anomaly = (
                product_id == "P014"
                and date(2025, 2, 1) <= d <= date(2025, 5, 31)
            )
            if bar_anomaly:
                base_reject_rate = random.uniform(0.030, 0.050)

            rejected = max(1, int(round(produced * base_reject_rate)))
            rework_rate = random.uniform(0.0015, 0.0060)
            if beverage_anomaly:
                rework_rate = random.uniform(0.006, 0.012)
            reworked = int(round(produced * rework_rate))

            production_cost = produced * meta["standard_cost"] * random.uniform(0.94, 1.02)
            batch_id = f"B{batch_num:06d}"

            production_rows.append([
                batch_id, date_id(d), product_id, plant_id,
                produced, rejected, reworked, round(production_cost, 2)
            ])
            batches_by_product[product_id].append((d, batch_id, plant_id))

            total_affected = max(rejected, 1)
            n_events = 1 if total_affected < 80 else random.choice([1, 2, 2, 3])

            defect_weights = list(DEFECTS_BY_CATEGORY[meta["category"]])
            if beverage_anomaly:
                defect_weights = [
                    ("Packaging", 0.72), ("Labeling", 0.08), ("Net Weight", 0.06),
                    ("Appearance", 0.04), ("Taste / Smell", 0.04),
                    ("Consistency", 0.02), ("Microbiological", 0.04)
                ]
            if bar_anomaly:
                defect_weights = [
                    ("Packaging", 0.66), ("Labeling", 0.08), ("Net Weight", 0.08),
                    ("Appearance", 0.10), ("Taste / Smell", 0.05),
                    ("Consistency", 0.01), ("Microbiological", 0.02)
                ]

            remaining = total_affected
            for i in range(n_events):
                defect = weighted_choice(defect_weights)
                severity = random.choice(SEVERITY[defect])
                if i == n_events - 1:
                    affected = remaining
                else:
                    upper = max(1, remaining - (n_events - i - 1))
                    affected = max(1, int(upper * random.uniform(0.25, 0.65)))
                remaining -= affected

                disposition = "Reject"
                if severity in ("Low", "Medium") and random.random() < 0.28:
                    disposition = "Rework"

                quality_rows.append([
                    f"Q{quality_num:07d}", batch_id, date_id(d),
                    product_id, plant_id, defect, severity, affected, disposition
                ])
                quality_num += 1

            batch_num += 1
            step = random.choice([2, 3, 3, 4, 4, 5])
            d += timedelta(days=step)

    write_csv(
        "fact_production.csv",
        ["batch_id","production_date_id","product_id","plant_id",
         "produced_units","rejected_units","reworked_units","production_cost_rub"],
        production_rows
    )

    write_csv(
        "fact_quality.csv",
        ["quality_event_id","batch_id","check_date_id","product_id","plant_id",
         "defect_type","severity","affected_units","disposition"],
        quality_rows
    )

    return production_rows, quality_rows, batches_by_product

def choose_recent_batch(batches_by_product, product_id, sale_date):
    batches = batches_by_product[product_id]
    dates = [x[0] for x in batches]
    idx = bisect_right(dates, sale_date) - 1
    if idx < 0:
        return None
    start = max(0, idx - 4)
    return random.choice(batches[start:idx+1])

def generate_complaints(sales_rows, batches_by_product):
    rows = []
    complaint_num = 1

    for s in sales_rows:
        _, sale_date_id, product_id, region_id, channel_id, units, *_ = s
        sale_date = date(
            int(str(sale_date_id)[:4]),
            int(str(sale_date_id)[4:6]),
            int(str(sale_date_id)[6:8])
        )
        meta = PRODUCT[product_id]

        rate_per_10k = {
            "Dairy": 1.8,
            "Beverages": 1.5,
            "Snacks": 1.4,
            "Breakfast": 1.2,
            "Desserts": 1.7,
        }[meta["category"]]

        multiplier = 1.0
        if channel_id == "C03":
            multiplier *= 1.20

        beverage_anomaly = (
            product_id in ("P010", "P011", "P012")
            and date(2025, 7, 1) <= sale_date <= date(2025, 10, 10)
        )
        if beverage_anomaly:
            multiplier *= 4.3

        bar_anomaly = (
            product_id == "P014"
            and date(2025, 2, 15) <= sale_date <= date(2025, 6, 20)
        )
        if bar_anomaly:
            multiplier *= 3.2

        probability = min(0.15, units * rate_per_10k / 10000.0 * multiplier)

        n_complaints = 0
        if random.random() < probability:
            n_complaints = 1
            if random.random() < probability * 0.08:
                n_complaints += 1

        for _ in range(n_complaints):
            batch = choose_recent_batch(batches_by_product, product_id, sale_date)
            if not batch:
                continue

            _, batch_id, _ = batch

            if beverage_anomaly and random.random() < 0.68:
                defect = "Packaging"
            elif bar_anomaly and random.random() < 0.58:
                defect = "Packaging"
            else:
                defect = weighted_choice(DEFECTS_BY_CATEGORY[meta["category"]])

            complaint_type = COMPLAINT_TYPES[defect]
            severity = random.choice(SEVERITY[defect])

            delay = random.randint(1, 14)
            complaint_date = min(END_DATE, sale_date + timedelta(days=delay))
            units_affected = random.choices([1, 2, 3], weights=[0.83, 0.14, 0.03])[0]

            price_factor = 1.00 if complaint_date.year == 2024 else 1.055
            price = meta["list_price"] * price_factor

            sev_factor = {"Low":0.35, "Medium":0.75, "High":1.45, "Critical":3.00}[severity]
            compensation = round(price * sev_factor * random.uniform(0.70, 1.30), 2)

            return_amount = 0.0
            return_prob = {"Low":0.25, "Medium":0.52, "High":0.78, "Critical":0.95}[severity]
            if random.random() < return_prob:
                return_amount = round(price * units_affected, 2)

            status = random.choices(
                ["Closed", "In Review", "Open"],
                weights=[0.86, 0.09, 0.05]
            )[0]

            rows.append([
                f"CMP{complaint_num:06d}", date_id(complaint_date),
                product_id, region_id, channel_id, batch_id,
                complaint_type, severity, units_affected,
                compensation, return_amount, status
            ])
            complaint_num += 1

    write_csv(
        "fact_complaints.csv",
        ["complaint_id","complaint_date_id","product_id","region_id","channel_id",
         "batch_id","complaint_type","severity","units_affected",
         "compensation_amount_rub","return_amount_rub","status"],
        rows
    )
    return rows

def main():
    generate_dimensions()
    sales = generate_sales()
    production, quality, batches = generate_production_and_quality()
    complaints = generate_complaints(sales, batches)

    print("Generated:")
    print(f"  fact_sales:       {len(sales):,} rows")
    print(f"  fact_production:  {len(production):,} rows")
    print(f"  fact_quality:     {len(quality):,} rows")
    print(f"  fact_complaints:  {len(complaints):,} rows")

if __name__ == "__main__":
    main()
