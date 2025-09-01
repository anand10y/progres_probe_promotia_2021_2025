import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.title("📊 Statistica Progres Bacalaureat pe Probe")

# ======= Încărcare fișier =======
uploaded_file = st.file_uploader("Încarcă fișierul Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # ======= Curățare și redenumire coloane =======
    df.columns = df.columns.astype(str).str.strip().str.replace("\n", " ", regex=True)
    mapare = {
        "Nume": "Nume",
        "Clasa": "Clasa",
        "Proba": "Proba",
        "Evaluare": "Evaluare",
        "Simulare": "Simulare",
        "Bacalaureat": "Bacalaureat"
    }
    df = df.rename(columns=lambda x: x.strip())
    df = df.rename(columns=mapare)

    # Adaugă coloane lipsă dacă nu există
    for col in ["Nume", "Clasa", "Proba", "Evaluare", "Simulare", "Bacalaureat"]:
        if col not in df.columns:
            df[col] = None

    # Conversie coloane numerice
    for col in ["Evaluare", "Simulare", "Bacalaureat"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # ======= Selector clasă =======
    clase_disponibile = sorted(df["Clasa"].dropna().unique())
    clasa_selectata = st.selectbox("Alege clasa", ["Toate clasele"] + clase_disponibile)
    if clasa_selectata != "Toate clasele":
        df = df[df["Clasa"] == clasa_selectata]

    # ======= Selector probă =======
    probe_disponibile = sorted(df["Proba"].dropna().unique())
    proba_selectata = st.selectbox("Alege proba", ["Toate probele"] + probe_disponibile)
    if proba_selectata != "Toate probele":
        df = df[df["Proba"] == proba_selectata]

    st.subheader("📋 Date brute")
    st.dataframe(df)

    # ======= Statistici de progres =======
    df["Progres Evaluare→Simulare"] = df["Simulare"] - df["Evaluare"]
    df["Progres Simulare→Bac"] = df["Bacalaureat"] - df["Simulare"]
    df["Progres Total"] = df["Bacalaureat"] - df["Evaluare"]

    st.subheader("📈 Statistici generale")
    st.write("Media Evaluare:", round(df["Evaluare"].mean(skipna=True), 2))
    st.write("Media Simulare:", round(df["Simulare"].mean(skipna=True), 2))
    st.write("Media Bacalaureat:", round(df["Bacalaureat"].mean(skipna=True), 2))
    st.write("Progres mediu total:", round(df["Progres Total"].mean(skipna=True), 2))

    # ======= Grafic per elev =======
    st.subheader("📊 Evoluție pe elev")
    if not df.empty:
        elev_selectat = st.selectbox("Alege un elev", df["Nume"].dropna().unique())
        elev_data = df[df["Nume"] == elev_selectat].iloc[0]

        fig, ax = plt.subplots()
        etape = ["Evaluare", "Simulare", "Bacalaureat"]
        valori = [
            elev_data.get("Evaluare", None),
            elev_data.get("Simulare", None),
            elev_data.get("Bacalaureat", None),
        ]
        ax.plot(etape, valori, marker="o")
        ax.set_title(f"Evoluția elevului {elev_selectat} - Proba: {elev_data.get('Proba', 'N/A')}")
        st.pyplot(fig)

    # ======= Grafic cu toate note pentru fiecare elev =======
    st.subheader("📊 Note elevi pe clasă și probă")
    if not df.empty:
        df_sorted = df.sort_values("Nume")
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        index = range(len(df_sorted))
        width = 0.25

        ax3.bar([i - width for i in index], df_sorted["Evaluare"], width=width, label="Evaluare")
        ax3.bar(index, df_sorted["Simulare"], width=width, label="Simulare")
        ax3.bar([i + width for i in index], df_sorted["Bacalaureat"], width=width, label="Bacalaureat")

        ax3.set_xticks(index)
        ax3.set_xticklabels(df_sorted["Nume"], rotation=45, ha="right")
        ax3.set_ylabel("Note")
        ax3.set_title(f"Note elevi - Clasa: {clasa_selectata}, Proba: {proba_selectata}")
        ax3.legend()
        st.pyplot(fig3)

    # ======= Grafic medii pe clase =======
    st.subheader("📊 Medii pe clase (pe probă)")
    medii = df.groupby("Clasa")[["Evaluare", "Simulare", "Bacalaureat"]].mean()
    if not medii.empty:
        fig2, ax2 = plt.subplots()
        medii.T.plot(ax=ax2, marker="o")
        ax2.set_title(f"Medii pe clase - Proba: {proba_selectata}")
        ax2.set_ylabel("Nota medie")
        st.pyplot(fig2)
