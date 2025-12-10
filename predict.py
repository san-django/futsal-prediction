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

# Initialize session state for persistence
if "team_selection" not in st.session_state:
    st.session_state.team_selection = {team: [""] * 6 for team in team_names}
if "used_players" not in st.session_state:
    st.session_state.used_players = set()

team_selection = st.session_state.team_selection
used_players = st.session_state.used_players

st.subheader("Select Players for Each Team (No Duplicates Allowed)")

# Main selection interface
for team in team_names:
    with st.expander(f"### {team}", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        for i in range(6):
            col = [col1, col2, col3][i % 3]
            with col:
                # Get current player for this slot
                current_player = team_selection[team][i]
                
                # Calculate available players (exclude currently used ones)
                available_players = [p for p in all_players if p not in used_players]
                
                # Options: blank first, then available players
                options = [""] + available_players
                
                # Find index for current selection
                selected_index = 0
                if current_player and current_player in options:
                    selected_index = options.index(current_player)
                
                # Dropdown widget
                new_choice = st.selectbox(
                    f"Player {i+1}",
                    options=options,
                    index=selected_index,
                    key=f"{team}_player_{i}"
                )
                
                # Update state when selection changes
                if new_choice != current_player:
                    # Remove old player from used_players if it was used
                    if current_player and current_player in used_players:
                        used_players.remove(current_player)
                    
                    # Update current selection
                    team_selection[team][i] = new_choice
                    
                    # Add new player to used_players if selected
                    if new_choice:
                        used_players.add(new_choice)

# Show current status
st.markdown("---")
col_status1, col_status2 = st.columns(2)

with col_status1:
    st.metric("Players Selected", len(used_players))
    st.metric("Teams Complete", sum(1 for players in team_selection.values() if all(p for p in players)))

with col_status2:
    remaining = len(all_players) - len(used_players)
    st.metric("Players Remaining", remaining)
    if remaining < 0:
        st.error("⚠️ Too many players selected! Check for duplicates.")

if st.button("💾 Save Prediction", type="primary"):
    if not user_name:
        st.error("❌ Please enter your name!")
    elif len(used_players) != 36:  # Exactly 36 players needed (6x6)
        st.error(f"❌ Please select exactly 36 unique players! ({len(used_players)} selected)")
    else:
        save_data = []
        for team, players in team_selection.items():
            # Filter out empty slots for saving
            team_players = [p for p in players if p]
            save_data.append([user_name, team] + team_players)
        
        try:
            for row in save_data:
                prediction_sheet.append_row(row)
            st.success("✅ Prediction saved successfully!")
            st.balloons()
            # Optional: reset after save
            # st.session_state.team_selection = {team: [""] * 6 for team in team_names}
            # st.session_state.used_players = set()
            # st.rerun()
        except Exception as e:
            st.error(f"❌ Save failed: {str(e)}")
