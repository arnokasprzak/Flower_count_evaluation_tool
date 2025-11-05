import streamlit as st
import os
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
    st.title("Flower count tile evaluation")
    st.markdown("""
    Welcome!  
    You will first see a number of **random example tiles**.  
    After that, you’ll be asked to **rate a number of tiles** from **0 to 5** based on how many flowers you see.
    """)

    tile_dir_input = st.text_input("Enter the path to the tile folder:", value=r"C:\Users\akasprzak\OneDrive - ILVO\BELIS\Interactive_validation_tool\Subplot_tiles")
    exploration_count_input = st.number_input("Number of example tiles to explore:", min_value=1, max_value=50, value=5)
    rating_count_input = st.number_input("Number of tiles to rate:", min_value=1, max_value=100, value=20)

    if st.button("Start Exploration Phase"):
        try:
            all_tiles = [f for f in os.listdir(tile_dir_input) if f.endswith(".jpg")]
            random.shuffle(all_tiles)

            st.session_state.TILE_DIR = tile_dir_input
            st.session_state.EXPLORATION_COUNT = exploration_count_input
            st.session_state.RATING_COUNT = rating_count_input
            st.session_state.selected_tiles = all_tiles

            st.session_state.phase = "explore"
            st.session_state.explore_index = 0
            st.rerun()
        except Exception as e:
            st.error(f"Error loading tiles: {e}")

# === PHASE 1: EXPLORATION ===
elif st.session_state.phase == "explore":
    st.header("Exploration Phase")
    idx = st.session_state.explore_index
    st.image(os.path.join(st.session_state.TILE_DIR, st.session_state.selected_tiles[idx]), use_container_width=True)
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

    st.image(os.path.join(st.session_state.TILE_DIR, current_file), use_container_width=True)
    score = st.slider("How many flowers do you see?", 0, 5, 0)

    if st.button("Save rating and next"):
        st.session_state.ratings.append({"filename": current_file, "score": score})
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