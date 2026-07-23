"""
مكتبة تحميل مشتركة بين app_store_owner.py و app_customer.py.
كل الدوال مُغلّفة بـ @st.cache_data عشان القراءة تحصل مرة واحدة بس
لحد ما تعمل refresh (زر Refresh بيمسح الكاش).
"""
import streamlit as st
import pandas as pd
import json
from pathlib import Path

# المسار بيتحسب نسبةً لمكان ملف data_loader.py نفسه،
# مش نسبةً لمكان تشغيل الـ terminal - عشان يشتغل من أي مكان تشغّله منه
DATA_DIR = Path(__file__).resolve().parent.parent / 'data' / 'processed'


@st.cache_data
def load_segments():
    return pd.read_parquet(f'{DATA_DIR}/segments.parquet')


@st.cache_data
def load_reorder_products():
    return pd.read_parquet(f'{DATA_DIR}/reorder_products.parquet')


@st.cache_data
def load_department_reorder():
    return pd.read_parquet(f'{DATA_DIR}/department_reorder.parquet')


@st.cache_data
def load_peak_hours():
    return pd.read_parquet(f'{DATA_DIR}/peak_hours.parquet')


@st.cache_data
def load_basket_size():
    return pd.read_parquet(f'{DATA_DIR}/basket_size.parquet')


@st.cache_data
def load_association_rules():
    return pd.read_parquet(f'{DATA_DIR}/association_rules.parquet')


@st.cache_data
def load_store_context():
    with open(f'{DATA_DIR}/store_owner_context.json', encoding='utf-8') as f:
        return json.load(f)


def refresh_all_data():
    """زرار في الـ UI بينادي الدالة دي عشان يمسح الكاش ويقرا الملفات تاني."""
    st.cache_data.clear()
