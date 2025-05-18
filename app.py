# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# Set page config
st.set_page_config(page_title="Nominal Pengurangan", layout="centered")
st.title("Aplikasi Nominal Pengurangan")

# Input tanggal dan file
selected_date = st.date_input("Pilih tanggal", format="DD/MM/YYYY")
uploaded_file = st.file_uploader("Upload file Excel Tiket Summary", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df['CETAK BOARDING PASS'] = pd.to_datetime(df['CETAK BOARDING PASS'], errors='coerce')
    df['ASAL'] = df['ASAL'].str.upper()

    # Daftar cabang tetap
    cabang_list = ["MERAK", "BAKAUHENI", "KETAPANG", "GILIMANUK", "CIWANDAN", "PANJANG"]

    # Filter berdasarkan tanggal inputan antara jam 00.00 s.d. sebelum 08.00
    start_dt = datetime.combine(selected_date, datetime.min.time())
    end_dt = datetime.combine(selected_date, datetime.min.time()).replace(hour=8)
    df_filtered = df[(df['CETAK BOARDING PASS'] >= start_dt) & (df['CETAK BOARDING PASS'] < end_dt)]

    # Hitung total tarif per cabang sesuai urutan
    results = []
    total_all = 0
    for cabang in cabang_list:
        total_tarif = df_filtered.loc[df_filtered['ASAL'] == cabang, 'TARIF'].sum()
        total_all += total_tarif
        formatted_tarif = str(int(total_tarif)) if total_tarif else "0"
        results.append({"ASAL": cabang.capitalize(), "Nominal Pengurangan": formatted_tarif})

    # Tambah 3 baris kosong
    for _ in range(3):
        results.append({"ASAL": "", "Nominal Pengurangan": ""})

    # Tambah baris total keseluruhan
    formatted_total_all = str(int(total_all))
    results.append({"ASAL": "Total", "Nominal Pengurangan": formatted_total_all})

    # Tampilkan hasil
    result_df = pd.DataFrame(results)
    result_df["Nominal Pengurangan"] = pd.to_numeric(result_df["Nominal Pengurangan"], errors="coerce")
    st.subheader(f"Rekap Nominal Pengurangan dari Jam 00:00 - 08:00 Tanggal {selected_date.strftime('%d %B %Y')}")
    st.table(result_df)

    # Tombol untuk mengunduh hasil ke Excel (semua baris termasuk total)
    download_df = pd.DataFrame(results)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        download_df.to_excel(writer, index=False)
    st.download_button(
        label="Download Hasil ke Excel",
        data=output.getvalue(),
        file_name="rekap_tarif.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Silakan unggah file Excel dan pilih tanggal untuk melihat hasil.")