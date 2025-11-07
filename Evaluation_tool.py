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
if "EXPLORATION_COUNT" not in st.session_state:
    st.session_state.EXPLORATION_COUNT = 0
if "RATING_COUNT" not in st.session_state:
    st.session_state.RATING_COUNT = 0

st.set_page_config(layout="centered")

# === INTRO PHASE ===
if st.session_state.phase == "intro":
    st.title("Flower Count Tile Evaluation")
    st.markdown(
        "Upload JPG images, view a few examples, and then rate each tile from 0–5 based on how many flowers you see."
    )

    uploaded_files = st.file_uploader(
        "Upload all tile images (select all JPGs from your folder)",
        type=["jpg"],
        accept_multiple_files=True
    )

    exploration_count_input = st.number_input(
        "Number of example tiles to explore:",
        min_value=1, max_value=50, value=5
    )

    rating_count_input = st.number_input(
        "Number of tiles to rate:",
        min_value=1, value=200
    )

    if st.button("Start Exploration Phase"):
        if uploaded_files and len(uploaded_files) >= exploration_count_input + rating_count_input:
            uploaded_files = list(uploaded_files)
            random.shuffle(uploaded_files)
            st.session_state.selected_tiles = uploaded_files
            st.session_state.EXPLORATION_COUNT = exploration_count_input
            st.session_state.RATING_COUNT = rating_count_input
            st.session_state.phase = "explore"
            st.session_state.explore_index = 0
            st.rerun()
        else:
            st.error("Please upload enough images for both exploration and rating.")

# === EXPLORATION PHASE ===
elif st.session_state.phase == "explore":
    st.header("Exploration Phase")
    idx = st.session_state.explore_index
    # Smaller image to avoid scrolling
    st.image(st.session_state.selected_tiles[idx], width=400)
    st.caption(f"Example tile {idx + 1} of {st.session_state.EXPLORATION_COUNT}")

    if st.button("Next"):
        st.session_state.explore_index += 1
        if st.session_state.explore_index >= st.session_state.EXPLORATION_COUNT:
            st.session_state.phase = "rate"
            st.session_state.rating_index = 0
            st.session_state.ratings = [
                {"filename": f.name, "score": None}
                for f in st.session_state.selected_tiles[
                    st.session_state.EXPLORATION_COUNT:
                    st.session_state.EXPLORATION_COUNT + st.session_state.RATING_COUNT
                ]
            ]
        st.rerun()

# === RATING PHASE ===
elif st.session_state.phase == "rate":
    idx = st.session_state.rating_index
    total = st.session_state.RATING_COUNT
    current_file = st.session_state.selected_tiles[
        st.session_state.EXPLORATION_COUNT + idx
    ]

    st.header("Rating Phase")

    # Show smaller image (fixed height) to fit on one screen, keep zoom icon
    st.image(current_file, width=400)  # Adjust width to fit vertically

    # Progress text below image
    st.caption(f"Photo {idx + 1} of {total}")

    # Numeric input for score
    current_score = st.session_state.ratings[idx]["score"]
    score = st.number_input(
        "How many flowers do you see? (0–5)",
        min_value=0, max_value=5,
        value=current_score if current_score is not None else 0,
        key=f"score_input_{idx}"
    )

    # Navigation buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Previous", disabled=(idx == 0)):
            st.session_state.ratings[idx]["score"] = score
            st.session_state.rating_index -= 1
            st.rerun()
    with col2:
        if st.button("Save and Next"):
            st.session_state.ratings[idx]["score"] = score
            if idx + 1 < total:
                st.session_state.rating_index += 1
            else:
                st.session_state.phase = "done"
            st.rerun()

# === COMPLETION PHASE ===
elif st.session_state.phase == "done":
    st.success("All ratings completed")
    df = pd.DataFrame(st.session_state.ratings)
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
