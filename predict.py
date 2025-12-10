import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Google Sheets setup using Streamlit secrets ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = st.secrets["google"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(creds)

PREDICTION_SHEET_NAME = "teamprediction"
prediction_sheet = gc.open(PREDICTION_SHEET_NAME).sheet1

# --- Player list ---
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

st.title("🏆 Futsal Team Prediction")

user_name = st.text_input("Enter your name / identifier:")

team_names = ["Godar Goats", "Acharya Attackers", "Soti Soldier",
              "Zenith Zebra", "Baral Bulls", "Joshi Jaguars"]

# Initialize session state ONCE only
if 'initialized' not in st.session_state:
    st.session_state.team_selection = {team: [""] * 6 for team in team_names}
    st.session_state.used_players = set()
    st.session_state.initialized = True

st.subheader("Select Players for Each Team")

# Get current state
team_selection = st.session_state.team_selection
used_players = st.session_state.used_players

for team in team_names:
    st.markdown(f"### {team}")
    for i in range(6):
        # Create unique key for this widget
        player_key = f"{team}_{i}"
        
        # Get current selection for this slot
        current_player = team_selection[team][i]
        
        # Calculate available players (exclude OTHER used players, but include current one)
        other_used_players = used_players - {current_player} if current_player else used_players
        available_players = [p for p in all_players if p not in other_used_players]
        
        # Options always include blank first
        options = [""] + available_players
        
        # Selectbox with current player preserved
        selected_player = st.selectbox(
            f"Player {i+1}",
            options=options,
            index=options.index(current_player) if current_player in options else 0,
            key=player_key
        )
        
        # Update the state
        if selected_player != current_player:
            # Remove old player from used_players
            if current_player and current_player in used_players:
                used_players.remove(current_player)
            
            # Update selection
            team_selection[team][i] = selected_player
            
            # Add new player to used_players if selected
            if selected_player:
                used_players.add(selected_player)

# Status display
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.metric("Players Selected", len(used_players))
with col2:
    st.metric("Players Remaining", len(all_players) - len(used_players))

if st.button("💾 Save Prediction", type="primary"):
    if not user_name:
        st.error("Please enter your name!")
    elif len(used_players) < 30:  # Allow partial saves
        st.warning("Only partial teams selected. Still saving...")
    else:
        save_data = []
        for team, players in team_selection.items():
            # Save only filled players
            team_players = [p for p in players if p]
            save_data.append([user_name, team] + team_players)
        
        for row in save_data:
            prediction_sheet.append_row(row)
        st.success("✅ Prediction saved successfully!")
        st.balloons()
