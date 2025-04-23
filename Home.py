import streamlit as st

st.set_page_config(page_title="الصفحة الرئيسية", page_icon="🌳")

st.title("🌿 شجرة العائلة")
st.markdown("مرحبًا بك في تطبيق شجرة العائلة 👋")

st.markdown("""
هذا التطبيق يعرض:
- 📊 إحصائيات العائلة (عدد الأفراد، الفروع، التوزيع)
- 🌳 عرض تفاعلي لشجرة العائلة بطريقة Sunburst

اختر الصفحة من القائمة الجانبية للبدء 👈
""")

st.image("https://i.imgur.com/8z7Z6Jg.png", caption="مثال توضيحي", use_column_width=True)
