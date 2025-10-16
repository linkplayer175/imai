import streamlit as st
import json
from PIL import Image

# Try importing moviepy (optional for local previews)
try:
    from moviepy.editor import ImageClip, concatenate_videoclips
    MOVIEPY_AVAILABLE = True
except ModuleNotFoundError:
    MOVIEPY_AVAILABLE = False

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="🎬 AI Animation Planner", layout="centered")
st.title("🎨 AI Image-to-Video Animation Planner")

# ---------------- INITIAL SETUP ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "animation_json" not in st.session_state:
    st.session_state.animation_json = None

# ---------------- IMAGE UPLOAD ----------------
uploaded_file = st.file_uploader("📸 Upload a base image (optional)", type=["jpg", "jpeg", "png"])
if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded image", use_container_width=True)
    img.save("uploaded.png")
    image_path = "uploaded.png"
else:
    image_path = None

# ---------------- CHAT HISTORY DISPLAY ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- CHAT INPUT ----------------
prompt = st.chat_input("💬 Describe your animation idea (e.g. 'a panda dancing in the jungle')")
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("✨ Generating animation scenes..."):
        # Try to use OpenAI API if key is set
        try:
            import openai
            openai.api_key = st.secrets["OPENAI_API_KEY"]

            system_prompt = (
                "You are an animation planner AI. "
                "Given a creative prompt, return a JSON list of animation scenes. "
                "Each scene must include: scene_id, image_reference, camera_motion, "
                "transition_type, caption, and duration_seconds."
            )

            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            text = response.choices[0].message.content

        except Exception as e:
            # fallback (simple static JSON)
            text = json.dumps([
                {
                    "scene_id": "1",
                    "image_reference": "scene1.png",
                    "camera_motion": "zoom-in",
                    "transition_type": "fade",
                    "caption": f"The story of {prompt} begins with a gentle intro.",
                    "duration_seconds": 4
                },
                {
                    "scene_id": "2",
                    "image_reference": "scene2.png",
                    "camera_motion": "pan-right",
                    "transition_type": "slide",
                    "caption": "Action starts as the characters move with rhythm.",
                    "duration_seconds": 5
                },
                {
                    "scene_id": "3",
                    "image_reference": "scene3.png",
                    "camera_motion": "zoom-out",
                    "transition_type": "fade",
                    "caption": "The story ends with laughter and colors fading away.",
                    "duration_seconds": 6
                }
            ])

    # Parse JSON safely
    try:
        animation_json = json.loads(text)
    except json.JSONDecodeError:
        st.error("⚠️ Could not parse valid JSON output.")
        animation_json = []

    st.session_state.animation_json = animation_json

    with st.chat_message("assistant"):
        if animation_json:
            st.success("Here’s your generated animation plan:")
            st.json(animation_json)
        else:
            st.warning("No valid animation scenes generated.")

# ---------------- RENDER ANIMATION PREVIEW ----------------
if st.session_state.animation_json and image_path:
    if MOVIEPY_AVAILABLE:
        if st.button("🎞️ Generate Animation Preview (Local Only)"):
            from moviepy.editor import ImageClip, concatenate_videoclips
            scenes = st.session_state.animation_json
            clips = []
            for s in scenes:
                dur = s.get("duration_seconds", 2)
                clip = ImageClip(image_path, duration=dur)
                clips.append(clip)
            video = concatenate_videoclips(clips)
            video.write_videofile("preview.mp4", fps=24, codec="libx264", audio=False)
            st.video("preview.mp4")
    else:
        st.info("🎞️ MoviePy not available in Streamlit Cloud. Run locally to preview animation.")

# ---------------- DOWNLOAD JSON ----------------
if st.session_state.animation_json:
    with open("animation_plan.json", "w") as f:
        json.dump(st.session_state.animation_json, f, indent=4)
    with open("animation_plan.json", "r") as f:
        st.download_button("📥 Download Animation JSON", f, file_name="animation_plan.json")
