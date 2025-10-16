import streamlit as st
import json, time
from PIL import Image
from moviepy.editor import ImageClip, concatenate_videoclips

# optional: local lightweight LLM via Hugging Face if no OpenAI key
from transformers import pipeline

st.set_page_config(page_title="AI Image → Video Planner", page_icon="🎬", layout="centered")
st.title("🎬 AI Image → Video Planner & Animator")

# ---------- Setup ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "animation_json" not in st.session_state:
    st.session_state.animation_json = None

# choose model backend
use_openai = "OPENAI_API_KEY" in st.secrets
if use_openai:
    import openai
    openai.api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.sidebar.info("Running local text-generation model (no API key found)")
    generator = pipeline("text-generation", model="distilgpt2")

# ---------- Image Upload ----------
uploaded = st.file_uploader("📸 Upload an image", type=["png","jpg","jpeg"])
if uploaded:
    img = Image.open(uploaded)
    st.image(img, caption="Uploaded", use_container_width=True)
    img_path = "uploaded.png"
    img.save(img_path)
else:
    img_path = None

# ---------- Show previous chat ----------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ---------- Chat input ----------
prompt = st.chat_input("💬 Describe your animation idea")
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role":"user","content":prompt})

    system_instruction = (
        "You are an animation planner AI. "
        "Given a user's idea, return a valid JSON list of scenes. "
        "Each scene must include: scene_id, image_reference, camera_motion, "
        "transition_type, caption, and duration_seconds. "
        "Return only JSON."
    )

    with st.spinner("🎨 Generating animation JSON..."):
        if use_openai:
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role":"system","content":system_instruction},
                    {"role":"user","content":prompt}
                ],
                temperature=0.7
            )
            text = resp.choices[0].message.content
        else:
            text = generator(system_instruction + "\n" + prompt, max_length=350)[0]["generated_text"]

        try:
            animation_json = json.loads(text)
        except json.JSONDecodeError:
            # try to extract JSON substring
            start, end = text.find("["), text.rfind("]")
            if start!=-1 and end!=-1:
                animation_json = json.loads(text[start:end+1])
            else:
                animation_json = []

    st.session_state.animation_json = animation_json
    with st.chat_message("assistant"):
        if animation_json:
            st.success("Here’s your generated animation plan:")
            st.json(animation_json)
        else:
            st.warning("Could not parse valid JSON output.")

# ---------- Render preview ----------
if st.session_state.animation_json and img_path:
    if st.button("🎞️ Generate Animation Preview"):
        st.info("⏳ Rendering short preview...")
        scenes = st.session_state.animation_json
        clips=[]
        for s in scenes:
            dur = s.get("duration_seconds",2)
            motion = s.get("camera_motion","none")
            clip = ImageClip(img_path,duration=dur)

            if motion=="zoom-in": clip = clip.resize(lambda t:1+0.1*t)
            elif motion=="zoom-out": clip = clip.resize(lambda t:1-0.1*t)
            elif motion=="pan-left": clip = clip.set_position(lambda t:(-40*t,0))
            elif motion=="pan-right": clip = clip.set_position(lambda t:(40*t,0))

            clips.append(clip)

        video = concatenate_videoclips(clips,method="compose")
        out_path="preview.mp4"
        video.write_videofile(out_path,fps=24,codec="libx264",audio=False)
        st.video(out_path)
        st.balloons()

        with open("animation_plan.json","w") as f:
            json.dump(scenes,f,indent=4)
        with open("animation_plan.json","r") as f:
            st.download_button("📄 Download JSON",f,file_name="animation_plan.json")
