import streamlit as st
import pandas as pd
import numpy as np
import cv2
import os
import json
import random
from PIL import Image
from utils.preprocessing import preprocess_image
from utils.features import extract_features
from utils.recommendation import get_similar_images

# Load user and restaurant data
user_df = pd.read_csv("userprofile.csv")

# Set page config for a wider layout
st.set_page_config(page_title="Fashion Recommender", layout="wide")

# Placeholder for bookmarks
BOOKMARK_FILE = "bookmarked_outfit.json"
if not os.path.exists(BOOKMARK_FILE):
    with open(BOOKMARK_FILE, "w") as f:
        json.dump({}, f)

def load_bookmarks():
    with open(BOOKMARK_FILE, "r") as f:
        return json.load(f)

def save_bookmarks(bookmarks):
    with open(BOOKMARK_FILE, "w") as f:
        json.dump(bookmarks, f)
        
# App state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "show_profile" not in st.session_state:
    st.session_state.show_profile = False
if "show_user_profile" not in st.session_state:
    st.session_state.show_user_profile = False
if "show_outfits" not in st.session_state:
    st.session_state.show_outfit = False  
if "selected_index" not in st.session_state:
    st.session_state.selected_index = None
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = set()    
    
query_vector = None                  
    
# Custom welcome screen with pink background
if not st.session_state.logged_in:
    # Add CSS to set background color for the welcome page
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #fdf6f0;
        }
        </style>
        """,
        unsafe_allow_html=True
    ) 
    
    col1, col2 = st.columns([1.5, 2])

    with col1:
        st.markdown("""
        <style>
            .centered-button .stButton > button {
                display: block;
                margin: 0 auto;
                padding: 1rem 2.5rem;
                font-size: 1.3rem;
                border-radius: 10px;
                background-color: #222;
                color: white;
                border: none;
            }
        </style>

        <div style='text-align: center; padding: 4rem;'>
            <h1 style='font-size: 3rem;'>Welcome to the Fashion Recommender</h1>
            <p style='font-size: 1.2rem;'>Find your style by uploading an image or browsing our trendy outfits.</p>
            <br>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("## 🔐 User Login")
        username_input = st.text_input("Enter your User ID")
        password_input = st.text_input("Enter Password", type="password")
        
        login_col1, login_col2 = st.columns(2)
        with login_col1:
            if st.button("Login"):
                if username_input in user_df['userID'].values:
                    st.session_state.logged_in = True
                    st.session_state.username = username_input
                    st.session_state.show_profile = False
                    st.session_state.show_restaurants = False
                    st.success(f"Welcome back, {username_input}!")
                else:
                    st.error("Username not found.")
        
        with login_col2:
            if st.button("Continue as Guest"):
                st.session_state.logged_in = True
                st.session_state.username = "Guest"
                st.session_state.show_profile = False
                st.session_state.show_restaurants = False               
                
    with col2:
        
        # Display cycling images
        image_paths = "images/image"
        #mage_folder = "images\image"
        if os.path.exists(image_paths):
            # Find all cuisine folders
            image_folders = [f for f in os.listdir(image_paths) if os.path.isdir(os.path.join(image_paths, f))]
            
            if image_folders:
                # Create a 2x2 grid for images
                grid1, grid2 = st.columns(2)
                
                # Display first row of images
                with grid1:
                    # Select a random cuisine and image from that cuisine
                    outfit = random.choice(image_folders)
                    outfit_path = os.path.join(image_paths, outfit)
                    image_files = [f for f in os.listdir(outfit_path) if f.endswith(('.jpg', '.png', '.jpeg'))]
                    if image_files:
                        img_path = os.path.join(outfit_path, random.choice(image_files))
                        st.image(Image.open(img_path), width=250)
                
                with grid2:
                    # Select another random cuisine and image
                    outfit = random.choice(image_folders)
                    outfit_path = os.path.join(image_paths, outfit)
                    image_files = [f for f in os.listdir(outfit_path) if f.endswith(('.jpg', '.png', '.jpeg'))]
                    if image_files:
                        img_path = os.path.join(outfit_path, random.choice(image_files))
                        st.image(Image.open(img_path), width=250)
                
                # Display second row of images
                with grid1:
                    # Select a random cuisine and image
                    outfit = random.choice(image_folders)
                    outfit_path = os.path.join(image_paths, outfit)
                    image_files = [f for f in os.listdir(outfit_path) if f.endswith(('.jpg', '.png', '.jpeg'))]
                    if image_files:
                        img_path = os.path.join(outfit_path, random.choice(image_files))
                        st.image(Image.open(img_path), width=250)
                
                with grid2:
                    # Select another random cuisine and image
                    outfit = random.choice(image_folders)
                    outfit_path = os.path.join(image_paths, outfit)
                    image_files = [f for f in os.listdir(outfit_path) if f.endswith(('.jpg', '.png', '.jpeg'))]
                    if image_files:
                        img_path = os.path.join(outfit_path, random.choice(image_files))
                        st.image(Image.open(img_path), width=250)
        
else:
    # Header section with title and user profile button
    header_col1, header_col2 = st.columns([3, 1])
    
    with header_col1:
        st.title("Discover Your Fashion")
        st.markdown("Upload an image or browse to get recommendations for your outfits.")
    
    with header_col2:
        if st.session_state.username != "Guest":
            # User profile button with icon and username
            user_button_style = """
            <style>
            .user-button {
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: #e6f2ff;
                border-radius: 8px;
                padding: 10px;
                margin-top: 20px;
                cursor: pointer;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }
            .user-button:hover {
                background-color: #e0e2e6;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .user-icon {
                font-size: 24px;
                margin-right: 8px;
            }
            .user-name {
                font-weight: bold;
            }
            </style>
            """
            st.markdown(user_button_style, unsafe_allow_html=True)
            
            user_button_html = f"""
            <div class="user-button" onclick="document.getElementById('user-profile-button').click()">
                <div class="user-icon">👤</div>
                <div class="user-name">{st.session_state.username}</div>
            </div>
            """
            st.markdown(user_button_html, unsafe_allow_html=True)
            
            # Hidden button that will be clicked by the JavaScript
            if st.button("View Profile", key="user-profile-button", help="View your profile details"):
                st.session_state.show_user_profile = not st.session_state.show_user_profile
                st.session_state.show_outfits = False
    
    st.info(f"👋 Logged in as {st.session_state.username}")            
    
    # Set up sidebar
    st.sidebar.markdown("## Options")
    
    # Logout button at the top
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.show_profile = False
        st.session_state.show_user_profile = False
        st.session_state.show_restaurants = False
        
    # Add bookmarks count in sidebar for non-guest users
    if st.session_state.username != "Guest":
        # Add a separator
        st.sidebar.markdown("---")
        
        # Show only bookmark count in sidebar
        bookmarks = load_bookmarks()
        user_bookmarks = bookmarks.get(st.session_state.username, [])
        
        if user_bookmarks:
            st.sidebar.markdown(f"### 🔖 {len(user_bookmarks)} Bookmarked Restaurants")
            if st.sidebar.button("View My Bookmarks"):
                st.session_state.show_user_profile = True
                st.session_state.show_restaurants = False
        else:
            st.sidebar.markdown("### 🔖 No Bookmarks Yet")
        
        st.sidebar.markdown("---")    
        
    # ---------------- HEADER ----------------
    st.sidebar.image(os.path.join("logo", "logo.png"), width=120)
    st.sidebar.title("🔍 Explore Fashion")
    category_filter = st.sidebar.selectbox("Filter by Category", ["All", "Tops", "Jeans", "Dresses", "Shoes", "Accessories"])
    search_query = st.sidebar.text_input("Search")
    group_score = st.sidebar.slider("Ratings", 0.0, 1.0, 0.5)
    colour_filter = st.sidebar.selectbox("Filter by Colour", ["All", "Red", "Blue", "Black", "Pink", "Yellow"])
    age_filter = st.sidebar.selectbox("Filter by Gender", ["All", "Women", "Men", "Boys", "Girls", "Kids"])
    
    # Main content area - User Profile View
    if st.session_state.username != "Guest" and st.session_state.show_user_profile:
        user_data = user_df[user_df['userID'] == st.session_state.username].iloc[0]
        
        # Create tabs for different sections of the user profile
        profile_tab, bookmarks_tab, visited_tab = st.tabs(["📋 Profile", "🔖 Bookmarks", "🗺️ Recently viewed outfits"])
        
        # Profile Tab
        with profile_tab:
            st.header(f"👤 {st.session_state.username}'s Profile")
            
            # Create columns for a more organized profile display
            col1, = st.columns(1)
            
            # Personal information in first column
            with col1:
                st.subheader("Personal Information")
                if 'birth_year' in user_data:
                    st.markdown(f"**Birth Year:** {user_data['birth_year']}")
                if 'marital_status' in user_data:
                    st.markdown(f"**Marital Status:** {user_data['marital_status']}")
                if 'interest' in user_data:
                    st.markdown(f"**Interest:** {user_data['interest']}")
                if 'personality' in user_data:
                    st.markdown(f"**Personality:** {user_data['personality']}")
                if 'dress_preference' in user_data:
                    st.markdown(f"**Dress Preference:** {user_data['dress_preference']}")
                if 'accessories' in user_data:
                    st.markdown(f"**Preferred Accessories:** {user_data['accessories']}")
                if 'colour' in user_data:
                    st.markdown(f"**Preferred Colour:** {user_data['colour']}")
                   
        # Bookmarks Tab
        with bookmarks_tab:
            st.header("🔖 Your Bookmarked Outfits")
            
            bookmarks = load_bookmarks()
            user_bookmarks = bookmarks.get(st.session_state.username, [])
            
            if not user_bookmarks:
                st.info("You haven't bookmarked any outfit yet.")
            else:
                # Display bookmarks in a grid
                bookmark_cols = st.columns(3)
                
                for i, name in enumerate(user_bookmarks):
                    with bookmark_cols[i % 3]:
                        st.markdown(f"### {name}")
                        # Try to find the outfit in the dataframe
                        outfit = restaurant_df[restaurant_df['name'] == name]
                        if not outfit.empty:
                            #row = restaurant.iloc[0]
                            st.markdown(f"**Cuisine:** {row['Rcuisine_x']}")
                            st.markdown(f"**Avg Rating:** {row['avg_rating']}/5")
                            st.markdown(f"**Group Friendly:** {row['group_friendly_score']:.2f}")
                            st.markdown(f"**Distance:** {row['distance_km']} km")
                            
                            # Option to remove bookmark
                            if st.button(f"❌ Remove", key=f"remove_{name}"):
                                user_bookmarks.remove(name)
                                bookmarks[st.session_state.username] = user_bookmarks
                                save_bookmarks(bookmarks)
                                st.success(f"Removed {name} from bookmarks!")
                                st.experimental_rerun()
                        else:
                            st.markdown(f"*Outfit details not available*")
                        
                        st.markdown("---")            
    
    # ---------------- LOAD IMAGE FEATURES ----------------
    df = pd.read_pickle("models/image_features.pkl")
    image_paths = list(df["image_path"])

    # ---------------- FILTERS ----------------
    if category_filter != "All":
        image_paths = [p for p in image_paths if category_filter.lower() in p.lower()]
    if search_query:
        image_paths = [p for p in image_paths if search_query.lower() in os.path.basename(p).lower()]  
        
    # ---------------- UPLOAD IMAGE ----------------
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", width=200)
        bytes_data = uploaded_file.read()
        img_arr = np.frombuffer(bytes_data, np.uint8)
        img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
        query_vector = extract_features(preprocess_image(img))

# ---------------- SELECT IMAGE FROM DATASET ----------------
    if st.session_state.selected_index is not None:
        selected_image_path = image_paths[st.session_state.selected_index]
        st.image(selected_image_path, caption="Selected Image", width=200)
        img = cv2.imread(selected_image_path)
        query_vector = extract_features(preprocess_image(img))

# ---------------- SHOW RECOMMENDATIONS ----------------
    if query_vector is not None:
        with st.spinner("Finding similar outfits..."):
            results = get_similar_images(query_vector, df)
        st.subheader("🎯 Similar Recommendations")
        rec_cols = st.columns(5)
        for i, (_, row) in enumerate(results.iterrows()):
            with rec_cols[i % 5]:
                st.image(row["image_path"], use_container_width=True)
                if st.button("🔖 Bookmark", key=f"bm_{i}"):
                    st.session_state.bookmarks.add(row["image_path"])

# ---------------- BROWSE DATASET IMAGES ----------------
    st.subheader("Browse the Collection")
    images_per_page = 8
    total_pages = (len(image_paths) - 1) // images_per_page + 1
    page = st.number_input("Page", 1, total_pages, step=1)

    start = (page - 1) * images_per_page
    end = start + images_per_page

    cols = st.columns(4)
    for i, path in enumerate(image_paths[start:end]):
        col = cols[i % 4]
        with col:
            if os.path.exists(path):
                if st.button("Select", key=f"select_{start+i}"):
                    st.session_state.selected_index = start + i
                st.image(path, use_column_width=True)



# ---------------- HIDE WARNINGS ----------------
    st.markdown("""
        <style>
        .st-emotion-cache-1wmy9hl, .stAlert {display: none;}
        </style>
    """, unsafe_allow_html=True)