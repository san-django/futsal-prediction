import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Google Sheets setup using Streamlit secrets ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials from Streamlit secrets
creds_dict = st.secrets["google"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(creds)

# Name of the sheet in Google Sheets
PREDICTION_SHEET_NAME = "team prediction"
prediction_sheet = gc.open(PREDICTION_SHEET_NAME).sheet1

# --- Player list embedded ---
all_players = [
    "SANGAM SHRESTHA", "SACHIN SEN", "SUJAN BK", "SUMAN CHHETRI", "SWORNIM TIMILSINA",
    "PRASHANNA PAUDEL", "SUJAL PARAJULI", "SHUBHAM SINGH", "SHRIJAN BHUSAL", "ROJIT SHRESTHA (F)", "AAYUSH ROKA  (F)",
    "ANUJ THAPA (F)", "SANKALPA SHARMA", "TANISHK THAPA", "SUJIT GURUNG", "SUJAN BHATTA",
    "VIVEK GAUTAM", "UDHAY THAKUR", "SUSHAN PANDEY", "SAKAR SUBEDI", "SHYAM MAHATO",
    "SHUSHANT ADHIKARI", "TASHI SHERPA (F)", "SABIN DAHAL", "SAJAN ROKAYA",
    "SANDIL KATUWAL", "SANJAYA ADHIKARI", "UNIQUE REGMI", "SUMAN SHARMA",
    "ANUPAM BISTA (F)", "SAMEER ACHARYA", "SAMIR GODAR", "SANTOSH JOSHI",
    "SUJAL SOTI", "SUDIP BARAL", "ZENITH SARU"
]

# --- Streamlit UI ---
st.title("🏆 Futsal Team Prediction")

user_name = st.text_input("Enter your name / identifier:")

team_names = ["Godar Goats", "Acharya Attackers", "Soti Soldier",
              "Zenith Zebra", "Baral Bulls", "Joshi Jaguars"]

team_selection = {team: [] for team in team_names}
used_players = set()

st.subheader("Select Players for Each Team")

for team in team_names:
    st.write(f"### {team}")
    for i in range(6):
        available_players = [p for p in all_players if p not in used_players]
        if not available_players:
            st.warning("No more players available!")
            break
        choice = st.selectbox(
            f"Player {i+1} for {team}", options=available_players, key=f"{team}_{i}"
        )
        if choice not in team_selection[team]:
            team_selection[team].append(choice)
            used_players.add(choice)

if st.button("Save Prediction"):
    if not user_name:
        st.error("Please enter your name!")
    else:
        save_data = []
        for team, players in team_selection.items():
            save_data.append([user_name, team] + players)
        for row in save_data:
            prediction_sheet.append_row(row)
        st.success("Prediction saved successfully!")
