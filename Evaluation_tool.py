import streamlit as st
import random
import pandas as pd
from io import StringIO

# === SESSION STATE INITIALIZATION ===
if "phase" not in st.session_state:
    st.session_state.phase = "intro"
if "ratings" not in st.session_state:
    st.session_state.ratings = []
if "rating_index" not in st.session_state:
    st.session_state.rating_index = 0
if "selected_tiles" not in st.session_state:
    st.session_state.selected_tiles = []

# === INTRO SCREEN ===
if st.session_state.phase == "intro":
    st.title("Flower Count Tile Evaluation")
    st.markdown("""
    Welcome!  
    Please upload all JPG images from your folder.  
    You will first see a number of **random example tiles**.  
    After that, you’ll be asked to **rate a number of tiles** from **0 to 5** based on how many flowers you see.
    """)

    uploaded_files = st.file_uploader(
        "Upload all tile images (select all JPGs from your folder)",
        type=["jpg"],
        accept_multiple_files=True
    )

    exploration_count_input = st.number_input("Number of example tiles to explore:", min_value=1, max_value=50, value=5)
    rating_count_input = st.number_input("Number of tiles to rate:", min_value=1, max_value=100, value=20)

    if st.button("Start Exploration Phase"):
        if uploaded_files and len(uploaded_files) >= exploration_count_input + rating_count_input:
            random.shuffle(uploaded_files)
            st.session_state.selected_tiles = uploaded_files
            st.session_state.EXPLORATION_COUNT = exploration_count_input
            st.session_state.RATING_COUNT = rating_count_input
            st.session_state.phase = "explore"
            st.session_state.explore_index = 0
            st.rerun()
        else:
            st.error("Please upload enough images for exploration and rating.")

# === PHASE 1: EXPLORATION ===
elif st.session_state.phase == "explore":
    st.header("Exploration Phase")
    idx = st.session_state.explore_index
    st.image(st.session_state.selected_tiles[idx], use_container_width=True)
    st.caption(f"Example tile {idx + 1} of {st.session_state.EXPLORATION_COUNT}")

    if st.button("Next"):
        st.session_state.explore_index += 1
        if st.session_state.explore_index >= st.session_state.EXPLORATION_COUNT:
            st.session_state.phase = "rate"
            st.session_state.rating_index = 0
        st.rerun()

# === PHASE 2: RATING ===
elif st.session_state.phase == "rate":
    idx = st.session_state.rating_index
    st.header(f"Rating {idx + 1} of {st.session_state.RATING_COUNT}")
    current_file = st.session_state.selected_tiles[st.session_state.EXPLORATION_COUNT + idx]

    st.image(current_file, use_container_width=True)
    score = st.slider("How many flowers do you see?", 0, 5, 0)

    if st.button("Save rating and next"):
        st.session_state.ratings.append({"filename": current_file.name, "score": score})
        st.session_state.rating_index += 1

        if st.session_state.rating_index >= st.session_state.RATING_COUNT:
            st.session_state.phase = "done"
        st.rerun()

# === FINAL PHASE: DOWNLOAD CSV ===
elif st.session_state.phase == "done":
    st.success("All ratings completed")

    df = pd.DataFrame(st.session_state.ratings)

    # Create downloadable CSV (no preview)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    st.markdown("You can now download your results below:")
    st.download_button(
        label="Download results as CSV",
        data=csv_buffer.getvalue(),
        file_name="flower_ratings.csv",
        mime="text/csv"
    )

    if st.button("Start over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()