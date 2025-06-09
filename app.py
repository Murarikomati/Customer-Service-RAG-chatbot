# streamlit_app.py
import streamlit as st
from helper import SQLChatBot

st.set_page_config(page_title="SQL ChatBot", layout="wide")

# --- Sidebar: SQL Server Connection ---
st.sidebar.title("🔌 SQL Server Connection")
server = st.sidebar.text_input("Server", placeholder="e.g. DESKTOP-XXXX\\SQLEXPRESS")
database = st.sidebar.text_input("Database", placeholder="e.g. RetailDB_RealTime")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

# Initialize session state
if "bot" not in st.session_state:
    st.session_state.bot = None
if "connected" not in st.session_state:
    st.session_state.connected = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Connect Button ---
if st.sidebar.button("Connect"):
    if all([server, database, username, password]):
        try:
            st.session_state.bot = SQLChatBot(server, database, username, password)
            st.session_state.connected = True
            st.sidebar.success("✅ Connected successfully!")
        except Exception as e:
            st.session_state.connected = False
            st.sidebar.error(f"❌ Connection failed: {e}")
    else:
        st.sidebar.warning("⚠️ Please fill in all fields to connect.")

# --- Optional: Clear Chat Button ---
if st.sidebar.button("Clear Chat History"):
    st.session_state.chat_history = []
    st.success("🧹 Chat history cleared.")

# --- Main Interface ---
st.title("💬 SQL ChatBot for SQL Server")

if not st.session_state.connected:
    st.info("🔌 Please connect to your SQL Server instance from the sidebar to begin.")
    st.stop()

# --- Chat Input ---
st.subheader("Ask a question about your data")
user_question = st.text_input("Your Question", placeholder="e.g. Show me the top 5 selling products")

if st.button("Get Answer") and user_question:
    with st.spinner("💡 Thinking..."):
        try:
            response = st.session_state.bot.get_full_response(user_question)

            # Save response to history
            st.session_state.chat_history.append({
                "question": user_question,
                "query": response["sql"],
                "result": response["result"],
                "explanation": response["explanation"]
            })

        except Exception as err:
            st.error(f"❌ Error: {err}")

# --- Display Chat History ---
if st.session_state.chat_history:
    st.markdown("## 💬 Chat History")
    for i, entry in enumerate(reversed(st.session_state.chat_history), 1):
        st.markdown(f"### 🔹 Question {len(st.session_state.chat_history) - i + 1}: {entry['question']}")
        st.markdown("**✅ SQL Query:**")
        st.code(entry["query"], language="sql")

        st.markdown("**📊 Result:**")
        if isinstance(entry["result"], str):  # likely an error message
            st.error(entry["result"])
        else:
            st.dataframe(entry["result"])

        st.markdown("**🧠 Explanation:**")
        st.write(entry["explanation"])
        st.markdown("---")
