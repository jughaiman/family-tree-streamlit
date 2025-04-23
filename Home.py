import streamlit as st

st.set_page_config(page_title="الصفحة الرئيسية", page_icon="🌿")

st.title("🌿 تطبيق شجرة العائلة")
st.markdown("مرحبًا بك في تطبيقنا 👋")

st.markdown("""
يحتوي هذا التطبيق على:
- 📊 صفحة الإحصائيات (تحليل عدد الأفراد والفروع)
- 🌳 صفحة الشجرة التفاعلية
""")

# روابط مباشرة للصفحات (حسب اسم الملف داخل pages/)
st.markdown("### اختر أحد الخيارات:")

col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/01_stats.py", label="🔢 الإحصائيات", icon="📊")

with col2:
    st.page_link("pages/02_family_tree.py", label="🌳 شجرة العائلة", icon="🌿")

st.markdown("---")
st.info("اختر من الأعلى أو من القائمة الجانبية على اليسار")

# صورة توضيحية (اختياري)
st.image("https://i.imgur.com/8z7Z6Jg.png", caption="مثال على عرض البيانات", use_column_width=True)
