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
PREDICTION_SHEET_NAME = "teamprediction"
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

# Use session_state so selections persist correctly on rerun
if "team_selection" not in st.session_state:
    st.session_state.team_selection = {team: [""] * 6 for team in team_names}
if "used_players" not in st.session_state:
    st.session_state.used_players = set()

team_selection = st.session_state.team_selection
used_players = st.session_state.used_players

st.subheader("Select Players for Each Team")

for team in team_names:
    st.write(f"### {team}")
    for i in range(6):
        # Remove previously selected player for this slot from used_players,
        # so changing the choice will free that player.
        prev_player = team_selection[team][i]
        if prev_player in used_players:
            used_players.remove(prev_player)

        # Compute available players (not used anywhere

