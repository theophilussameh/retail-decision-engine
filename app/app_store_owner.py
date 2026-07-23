"""
شغّله من مجلد app/:  streamlit run app_store_owner.py
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from data_loader import (
    load_segments, load_reorder_products, load_department_reorder,
    load_peak_hours, load_store_context, refresh_all_data
)

st.set_page_config(page_title="AI Business Advisor - Store Owner", layout="wide")

# ---------- Sidebar ----------
st.sidebar.title("⚙️ Controls")
if st.sidebar.button("🔄 Refresh data"):
    refresh_all_data()
    st.rerun()

page = st.sidebar.radio("العرض", ["📊 Dashboard", "🤖 AI Advisor"])

# ==========================================================
# صفحة الـ Dashboard
# ==========================================================
if page == "📊 Dashboard":
    st.title("Customer Behavior Dashboard")

    segments = load_segments()
    reorder = load_reorder_products()
    dept_reorder = load_department_reorder()
    peak_hours = load_peak_hours()

    # مقاس ثابت لكل الرسومات عشان الأحجام تبقى متناسقة في الصفحة كلها
    FIG_SIZE = (6, 3.8)

    tab1, tab2, tab3 = st.tabs(["👥 Segments", "🔁 Reorder Rate", "🕐 Peak Hour"])

    # --- Widget 1: Segmentation ---
    with tab1:
        st.subheader("Customer Segments (RFM Clustering)")

        summary = segments.groupby('cluster_name')[
            ['last_days_since_prior', 'frequency', 'avg_basket_size']
        ].mean().round(1)
        counts = segments['cluster_name'].value_counts()

        biggest = counts.idxmax()
        vip_row = summary.loc[summary['frequency'].idxmax()]
        vip_name = summary['frequency'].idxmax()

        st.markdown(
            f"أكبر شريحة عملاء هي **{biggest}** بعدد **{counts[biggest]:,}** عميل. "
            f"شريحة **{vip_name}** هي الأكثر نشاطًا: متوسط **{vip_row['frequency']:.0f}** طلب لكل عميل "
            f"وآخر شراء منذ **{vip_row['last_days_since_prior']:.0f}** يوم فقط في المتوسط."
        )

        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots(figsize=FIG_SIZE)
            counts.plot(kind='bar', ax=ax, color='#2a78d6')
            ax.set_ylabel("عدد العملاء")
            ax.set_xlabel("")
            plt.xticks(rotation=20)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
        with col2:
            st.dataframe(summary, use_container_width=True, height=180)

        col3, col4 = st.columns(2)
        with col3:
            fig, ax = plt.subplots(figsize=FIG_SIZE)
            sns.boxplot(data=segments, x='cluster_name', y='frequency', ax=ax)
            ax.set_xlabel("")
            plt.xticks(rotation=20)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
        with col4:
            # رسمة التحقق البصري (PCA) بتاعة الـ clustering
            if 'pca1' in segments.columns and 'pca2' in segments.columns:
                fig, ax = plt.subplots(figsize=FIG_SIZE)
                sns.scatterplot(
                    data=segments, x='pca1', y='pca2', hue='cluster_name',
                    alpha=0.4, s=10, ax=ax
                )
                ax.set_title("Customer Segments (PCA Projection)")
                plt.tight_layout()
                st.pyplot(fig, use_container_width=True)
            else:
                st.info(
                    "رسمة الـ PCA مش متاحة — لازم تضيف عمودي pca1/pca2 لملف "
                    "segments.parquet من export cell الجديدة في notebook الـ clustering."
                )

    # --- Widget 2: Reorder Rate ---
    with tab2:
        st.subheader("Most Loyal Products")
        top_n = st.slider("عدد المنتجات المعروضة", 5, 30, 15)
        top_loyal = reorder.sort_values('reorder_rate', ascending=False).head(top_n)
        top_dept = dept_reorder.sort_values('avg_reorder_rate', ascending=False).iloc[0]

        st.markdown(
            f"قسم **{top_dept['department']}** هو الأعلى ولاءً بمتوسط reorder rate "
            f"**{top_dept['avg_reorder_rate']:.0%}** عبر **{int(top_dept['n_products'])}** منتج. "
            f"أعلى منتج فرديًا هو **{top_loyal.iloc[0]['product_name']}** بنسبة "
            f"**{top_loyal.iloc[0]['reorder_rate']:.0%}**."
        )

        fig, ax = plt.subplots(figsize=(6, max(3.8, top_n * 0.28)))
        sns.barplot(data=top_loyal, y='product_name', x='reorder_rate', hue='department', dodge=False, ax=ax)
        ax.set_ylabel("")
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)

        st.subheader("Reorder Rate by Department")
        st.dataframe(
            dept_reorder.sort_values('avg_reorder_rate', ascending=False),
            use_container_width=True
        )

    # --- Widget 3: Peak Hour ---
    with tab3:
        st.subheader("Peak Hour per Department")

        earliest = peak_hours.loc[peak_hours['order_hour_of_day'].idxmin()]
        latest = peak_hours.loc[peak_hours['order_hour_of_day'].idxmax()]
        st.markdown(
            f"كل الأقسام تقريبًا بتتفعل في نفس النافذة العامة (الضهر لحد بداية الليل). "
            f"أبكر قسم ذروة هو **{earliest['department']}** الساعة **{int(earliest['order_hour_of_day'])}**، "
            f"وأكتر قسم متأخر هو **{latest['department']}** الساعة **{int(latest['order_hour_of_day'])}**."
        )

        st.dataframe(
            peak_hours.sort_values('order_hour_of_day'),
            use_container_width=True
        )

# ==========================================================
# صفحة الـ AI Advisor (chat)
# ==========================================================
else:
    st.title("🤖 AI Business Advisor")
    st.caption("اسأل عن أي حاجة في الداشبورد (segments, reorder rate, peak hours)")

    context = load_store_context()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("اكتب سؤالك هنا...")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        # -------------------------------------------------
        # TODO: هنا هيتحط استدعاء الـ LLM الحقيقي لاحقًا.
        # الفانكشن دي placeholder بترجع رد ثابت دلوقتي.
        # context (dict) فيه كل أرقام الداشبورد جاهزة كـ JSON.
        # -------------------------------------------------
        def ask_llm(user_question: str, context: dict) -> str:
            return (
                "🔧 مكان الـ LLM لسه فاضي — هنا هيتحط الاستدعاء الحقيقي "
                "(مثلاً Anthropic API) اللي ياخد context + السؤال ويرجع تقرير بلغة طبيعية."
            )

        answer = ask_llm(question, context)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)