"""
يشتغل من مجلد app/. يقرا الملفات المُصدّرة من الـ 3 notebooks
ويبني store_owner_context.json عشان الـ LLM يستخدمه كـ context.
شغّله: python generate_store_context.py
"""
import pandas as pd
import json
import os

DATA_DIR = 'data/processed'

segments = pd.read_parquet(f'{DATA_DIR}/segments.parquet')
reorder = pd.read_parquet(f'{DATA_DIR}/reorder_products.parquet')
dept_reorder = pd.read_parquet(f'{DATA_DIR}/department_reorder.parquet')
peak_hours = pd.read_parquet(f'{DATA_DIR}/peak_hours.parquet')

context = {"customer_segments": [], "reorder_insights": {}, "peak_hours": []}

for name, group in segments.groupby('cluster_name'):
    context["customer_segments"].append({
        "segment_name": name,
        "num_customers": int(len(group)),
        "avg_days_since_last_order": round(float(group['last_days_since_prior'].mean()), 1),
        "avg_orders_count": round(float(group['frequency'].mean()), 1),
        "avg_basket_size": round(float(group['avg_basket_size'].mean()), 1)
    })

top5 = reorder.sort_values('reorder_rate', ascending=False).head(5)
bottom5 = reorder.sort_values('reorder_rate', ascending=True).head(5)
dept_reorder_sorted = dept_reorder.sort_values('avg_reorder_rate', ascending=False)

context["reorder_insights"] = {
    "top_loyal_products": top5[['product_name', 'department', 'reorder_rate']].round(2).to_dict('records'),
    "least_loyal_products": bottom5[['product_name', 'department', 'reorder_rate']].round(2).to_dict('records'),
    "best_department": dept_reorder_sorted.iloc[0]['department'],
    "best_department_rate": round(float(dept_reorder_sorted.iloc[0]['avg_reorder_rate']), 2)
}

for _, row in peak_hours.iterrows():
    context["peak_hours"].append({
        "department": row['department'],
        "peak_hour": int(row['order_hour_of_day'])
    })

os.makedirs(DATA_DIR, exist_ok=True)
with open(f'{DATA_DIR}/store_owner_context.json', 'w', encoding='utf-8') as f:
    json.dump(context, f, ensure_ascii=False, indent=2)

print("✅ saved store_owner_context.json")