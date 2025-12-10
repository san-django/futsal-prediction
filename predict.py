import json
import os
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load Excel file with player list

print("Current working directory: ", os.getcwd())
# changes the working directory to path where the project.py is ##
# os.chdir('C:/Users/SANJAYA/python/futsal')
excel_filename = r"player.xlsx"
df = pd.read_excel(excel_filename)
players = df.iloc[:, 0].dropna().astype(str).tolist()

teams = ["Godar Goats", "Acharya Attackers", "Soti Soldiers",
         "Zenith Zebras", "Baral Bulls", "Joshi Jaguars"]

# Initialize session state
if "team_selections" not in st.session_state:
    st.session_state.team_selections = {team: [None]*6 for team in teams}

st.title("🏆 Futsal Team Prediction")

# ✅ Text input for participant name
player_name = st.text_input("Enter your name / identifier:")

# Google Sheets setup

# Load credentials from Streamlit secrets
creds_dict = st.secrets["google_service_account"]
creds_json = json.dumps(creds_dict)
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(creds_json),
    ['https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive']
)
gc = gspread.authorize(creds)

# Function to get available players


def get_available_players(team, idx):
    current_selection = st.session_state.team_selections[team][idx]
    selected_other_slots = []
    for t in teams:
        for i, p in enumerate(st.session_state.team_selections[t]):
            if t != team or i != idx:
                if p:
                    selected_other_slots.append(p)
    available = [p for p in players if p not in selected_other_slots]
    if current_selection and current_selection not in available:
        available.append(current_selection)
    return [""] + sorted(available)


# Dropdowns for each team
for team in teams:
    st.subheader(team)
    cols = st.columns(2)
    for i in range(6):
        col = cols[i % 2]
        options = get_available_players(team, i)
        current_selection = st.session_state.team_selections[team][i]
        index = 0 if current_selection is None else options.index(
            current_selection)
        selection = col.selectbox(
            f"Player {i+1}", options, index=index, key=f"{team}_{i}")
        st.session_state.team_selections[team][i] = selection if selection != "" else None

# Display current selections
st.markdown("### 🏅 Current Team Selection")
for t in teams:
    st.markdown(f"**{t}**")
    for i, p in enumerate(st.session_state.team_selections[t], start=1):
        st.markdown(f"{i}. {p if p else '---'}")
    st.markdown("---")

# Save function to Google Sheet


def save_to_sheet():
    if not player_name:
        st.error("⚠️ Please enter your name / identifier before saving.")
        return

    data = []
    for t in teams:
        for i, p in enumerate(st.session_state.team_selections[t], start=1):
            data.append([player_name, t, i, p if p else ""])

    # Append each row to Google Sheet
    for row in data:
        sheet.append_row(row)

    st.success("✅ Your predictions have been saved to Google Sheet!")


st.button("💾 Submit Prediction", on_click=save_to_sheet)
