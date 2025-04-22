import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter
from datetime import datetime

# إعدادات عامة
sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)

# تحميل الملف من المسار المحدد
import gspread
from google.oauth2.service_account import Credentials

# إعداد الصلاحيات
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

import json


# قراءة بيانات json من Streamlit secrets
info = st.secrets["gcp_service_account"]

creds = Credentials.from_service_account_info(info, scopes=SCOPE)


client = gspread.authorize(creds)

# افتح الشيت باستخدام الـ ID
SHEET_ID = "1KhHhAInhJGV3NO0YDZjgg86O_0KbBl5aRuXfVIpsfkU"
sheet = client.open_by_key(SHEET_ID).sheet1  # أو sheet.get_worksheet(0)

# تحميل البيانات في DataFrame
data = sheet.get_all_records()
df = pd.DataFrame(data)

df.columns = df.columns.str.strip()

# إزالة الأعمدة المكررة
df = df.loc[:, ~df.columns.duplicated()]  # إزالة الأعمدة المكررة فقط

# تنظيف البيانات: إزالة أو استبدال القيم `NaN` في الأعمدة المهمة
df = df.dropna(subset=['Full Name', 'Sex (M/F)', 'Date of Birth', 'Date of Death', 'Alive or dead'])

# استبدال القيم غير الصالحة بـ `NaN` في الأعمدة الأخرى
df = df.apply(lambda x: pd.to_numeric(x, errors='coerce') if x.name != 'Full Name' else x)

# تنظيف التواريخ
for date_col in ['Date of Birth', 'Date of Death']:
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df.loc[~df[date_col].between('1900-01-01', '2025-01-01'), date_col] = pd.NaT

# حساب العمر
today = pd.Timestamp.today()
df['Age'] = df.apply(
    lambda row: (row['Date of Death'] - row['Date of Birth']).days // 365 if pd.notna(row['Date of Death']) and pd.notna(row['Date of Birth'])
    else (today - row['Date of Birth']).days // 365 if pd.notna(row['Date of Birth'])
    else np.nan, axis=1
)

# ---------------- إحصائيات ----------------

# عرض العنوان الأساسي
st.title("إحصائيات الأسرة")

# عرض أول 5 صفوف من البيانات للتأكد من أن البيانات تم تحميلها بشكل صحيح
st.write("أول 5 صفوف من البيانات:")
st.write(df.head())

# عرض نص بسيط لاختبار الصفحة
st.text("تم تحميل البيانات بنجاح!")

# اختبار رسم بياني بسيط للتأكد من أن الرسومات تظهر
def test_plot():
    fig, ax = plt.subplots()
    sns.barplot(x=['A', 'B', 'C'], y=[1, 2, 3], ax=ax)
    st.pyplot(fig)  # عرض الرسم البياني
test_plot()

# 1. توزيع الجنس مع نسبة الذكور إلى الإناث
def gender_distribution():
    counts = df['Sex (M/F)'].value_counts()
    male = counts.get('M', 0)
    female = counts.get('F', 0)
    ratio = round(male / female, 2) if female > 0 else 'N/A'
    fig, ax = plt.subplots()
    sns.barplot(x=counts.index, y=counts.values, palette='coolwarm', ax=ax)
    ax.set_title(f'توزيع الجنس (نسبة الذكور إلى الإناث: {ratio})')
    st.pyplot(fig)

# لتشغيل أي إحصائية:
gender_distribution()
