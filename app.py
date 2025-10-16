import streamlit as st
from PIL import Image
import time

# --- APP TITLE ---
st.set_page_config(page_title="AI Image → Video Chat Demo", page_icon="🎬", layout="centered")
st.title("🎬 AI Image → Video Animator Chat")
st.write("Upload an image and chat with your AI assistant to describe your animation idea!")

# --- SESSION STATE (for persistent chat memory) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- IMAGE UPLOAD SECTION ---
uploaded_image = st.file_uploader("📸 Upload an image to animate", type=["png", "jpg", "jpeg"])
if uploaded_image:
    img = Image.open(uploaded_image)
    st.image(img, caption="Uploaded Image", use_container_width=True)

# --- DISPLAY PREVIOUS CHAT MESSAGES ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- CHAT INPUT ---
prompt = st.chat_input("💬 Describe your animation idea (e.g., 'Make the cat dance under moonlight')")

# --- CHAT LOGIC ---
if prompt:
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Simulate AI "thinking"
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        # Simple AI response generator (replace this with your model later)
        simulated_reply = f"That’s a fun idea! I’ll animate **{prompt}** with smooth transitions and vibrant effects."
        for chunk in simulated_reply.split():
            full_response += chunk + " "
            time.sleep(0.05)
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

    # Save assistant message to memory
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- SIDEBAR INFO ---
st.sidebar.header("ℹ️ About this Demo")
st.sidebar.markdown("""
This is a sample **AI Image → Video** chat interface built in **Streamlit**.

✅ Upload any image  
✅ Describe how to animate it  
✅ See AI-style chat replies  

> 💡 Later, you can connect this chat to a real AI model (OpenAI, HuggingFace, or your own API).
""")
