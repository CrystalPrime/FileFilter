import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.title("Dosya Filtreleme HUB")

# Kullanıcıdan dosya türünü seçme
file_type = st.selectbox("Yükleyeceğiniz dosya türünü seçin", ["CSV", "Excel"])

# Kullanıcıdan dosya yükleme
if file_type == "CSV":
    uploaded_file = st.file_uploader("Bir CSV dosyası yükleyin", type="csv")
elif file_type == "Excel":
    uploaded_file = st.file_uploader("Bir Excel dosyası yükleyin", type="xlsx")

if uploaded_file is not None:
    if file_type == "CSV":
        df = pd.read_csv(uploaded_file, sep=";")
    elif file_type == "Excel":
        df = pd.read_excel(uploaded_file)

    st.write("Yüklenen Veri Tablosu:")
    st.dataframe(df)
    
    st.write("Veri İstatistikleri:")
    st.write(df.describe())

    st.write("Veri Filtreleme:")
    #streamlit run \\kz_fileserver\KIZILAYKART\SUY\JMC_KOORDİNATÖR_YARDIMCILIĞI\Çalışma_Grupları\Ürün ve Bilgi Yönetimi\Ekip İçi Paylaşılanlar\Batuhan\app.py
    # Sütunları seçmek için çoklu seçim kutusu
    columns_to_filter = st.multiselect("Filtrelemek istediğiniz sütunları seçin", df.columns)
    
    filtered_df = df.copy()
    
    # Seçilen sütunlar için interaktif filtreler oluştur
    for column in columns_to_filter:
        if df[column].dtype == 'object':
            # Eğer sütun türü string ise, benzersiz değerleri seç
            unique_values = df[column].unique()
            selected_values = st.multiselect(f"{column} sütunu için filtreleme yapın", unique_values)
            if selected_values:
                filtered_df = filtered_df[filtered_df[column].isin(selected_values)]
        elif df[column].dtype in ['int64', 'float64']:
            # Eğer sütun türü sayısal ise, aralık filtresi kullan
            min_value = df[column].min()
            max_value = df[column].max()
            selected_range = st.slider(f"{column} sütunu için aralığı seçin", min_value, max_value, (min_value, max_value))
            filtered_df = filtered_df[(filtered_df[column] >= selected_range[0]) & (filtered_df[column] <= selected_range[1])]

    st.write("Filtrelenmiş Veri Tablosu:")
    st.dataframe(filtered_df)
    
    # Grafik oluşturma
    st.write("Grafik Oluşturma:")
    graph_type = st.selectbox("Grafik türünü seçin", ["Histogram", "Bar Plot", "Scatter Plot"])
    selected_column_for_plot = st.selectbox("Grafik için bir sütun seçin", filtered_df.columns)
    
    if graph_type == "Histogram" and filtered_df[selected_column_for_plot].dtype in ['int64', 'float64']:
        fig, ax = plt.subplots()
        filtered_df[selected_column_for_plot].hist(ax=ax, bins=20)
        ax.set_title(f"Histogram of {selected_column_for_plot}")
        ax.set_xlabel(selected_column_for_plot)
        ax.set_ylabel("Frequency")
        st.pyplot(fig)
        
    elif graph_type == "Bar Plot" and filtered_df[selected_column_for_plot].dtype == 'object':
        fig, ax = plt.subplots()
        filtered_df[selected_column_for_plot].value_counts().plot(kind='bar', ax=ax)
        ax.set_title(f"Bar Plot of {selected_column_for_plot}")
        ax.set_xlabel(selected_column_for_plot)
        ax.set_ylabel("Frequency")
        st.pyplot(fig)
        
    elif graph_type == "Scatter Plot":
        numeric_columns = filtered_df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_columns) >= 2:
            x_axis = st.selectbox("X ekseni için bir sütun seçin", numeric_columns)
            y_axis = st.selectbox("Y ekseni için bir sütun seçin", numeric_columns)
            if x_axis and y_axis:
                fig, ax = plt.subplots()
                ax.scatter(filtered_df[x_axis], filtered_df[y_axis])
                ax.set_title(f"Scatter Plot of {x_axis} vs {y_axis}")
                ax.set_xlabel(x_axis)
                ax.set_ylabel(y_axis)
                st.pyplot(fig)
                
    st.write("Filtrelenmiş Verileri İndirme:")
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Filtrelenmiş verileri CSV olarak indir",
        data=csv,
        file_name='filtered_data.csv',
        mime='text/csv',
    )
    
    xlsx_io = io.BytesIO()
    with pd.ExcelWriter(xlsx_io, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False)

    xlsx_io.seek(0)
    st.download_button(
        label="Filtrelenmiş verileri Excel olarak indir",
        data=xlsx_io,
        file_name='filtered_data.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )