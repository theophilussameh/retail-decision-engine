"""
شغّله من مجلد app/:  streamlit run app_customer.py
واجهة العميل: يختار منتج، ويشوف المنتجات اللي بتتشترى معاه غالبًا
(مبنية على association rules من market_basket_rules_model.ipynb).
"""
import streamlit as st
from data_loader import load_association_rules, refresh_all_data

st.set_page_config(page_title="You Might Also Like", layout="centered")

if st.sidebar.button("🔄 Refresh data"):
    refresh_all_data()
    st.rerun()

st.title("🛒 You Might Also Like")

rules = load_association_rules()

# قايمة منتجات فريدة من الـ antecedents عشان المستخدم يختار منها
all_products = sorted(set(
    p.strip()
    for names in rules['antecedents_names']
    for p in names.split(',')
))

selected_product = st.selectbox("اختار منتج في سلتك:", all_products)

matches = rules[rules['antecedents_names'].str.contains(selected_product, regex=False)]
matches = matches.sort_values('lift', ascending=False).head(10)

if matches.empty:
    st.info("مفيش توصيات كافية لهذا المنتج لسه.")
else:
    st.subheader(f"You Might Also Like")
    for _, row in matches.iterrows():
        st.markdown(f"- **{row['consequents_names']}**  \n")
                   #  f"  (confidence: {row['confidence']:.2f}, lift: {row['lift']:.2f})")