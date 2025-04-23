import streamlit as st

st.set_page_config(page_title="الصفحة الرئيسية", page_icon="🌿")

st.title("🌿 تطبيق شجرة العائلة")
st.markdown("مرحبًا بك في تطبيقنا 👋")

st.markdown("""
يحتوي هذا التطبيق على:
- 📊 صفحة الإحصائيات
- 🌳 صفحة الشجرة التفاعلية
""")

st.markdown("### اختر أحد الصفحات:")
st.markdown("[🔢 الإحصائيات](./01_stats)")
st.markdown("[🌳 شجرة العائلة](./02_family_tree)")

st.image("https://i.imgur.com/8z7Z6Jg.png", caption="مثال توضيحي", use_column_width=True)
