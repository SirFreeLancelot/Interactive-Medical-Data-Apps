import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import time

st.set_page_config(layout="wide")

# Initialize session state for total calorie count
if 'total_calories' not in st.session_state:
    st.session_state.total_calories = 0
if 'calorie_table' not in st.session_state:
    st.session_state.calorie_table = pd.read_csv('calories.csv')
if 'tray' not in st.session_state:
    st.session_state.tray = pd.DataFrame(columns=['Food', 'Servings', 'Calories'])
if 'tray_calories' not in st.session_state:
    st.session_state.tray_calories = 0
if 'eaten_meals' not in st.session_state:
    st.session_state.eaten_meals = pd.DataFrame(columns=['Food', 'Servings', 'Calories'])
if 'stance' not in st.session_state:
    st.session_state.stance = "standing"
if 'age' not in st.session_state:
    st.session_state.age = 18
if 'sex' not in st.session_state:
    st.session_state.sex = "Male"
if 'height' not in st.session_state:
    st.session_state.height = 170
if 'weight' not in st.session_state:
    st.session_state.weight = 70
if 'activity_level' not in st.session_state:
    st.session_state.activity_level = "Moderately Active"
if 'rda' not in st.session_state:
    st.session_state.rda = 0


activity_level_map = {
                "Sedentary": 1.2,
                "Lightly Active": 1.375,
                "Moderately Active": 1.55,
                "Very Active": 1.725,
                "Extra Active": 1.9
            }


def calculate_bmr(age, sex, height, weight, activity_level):
    if age < 1:
        return None
    elif 1 <= age <= 3:
        return 1010  # Children 1-3 years
    elif 4 <= age <= 6:
        return 1360  # Children 4-6 years
    elif 7 <= age <= 9:
        return 1700  # Children 7-9 years
    elif 10 <= age <= 12:
        if sex == "Male":
            return 2220  # Boys 10-12 years
        elif sex == "Female":
            return 2060  # Girls 10-12 years
    elif 13 <= age <= 15:
        if sex == "Male":
            return 2860  # Boys 13-15 years
        elif sex == "Female":
            return 2400  # Girls 13-15 years
    elif 16 <= age <= 18:
        if sex == "Male":
            return 3320  # Boys 16-18 years
        elif sex == "Female":
            return 2500  # Girls 16-18 years
    else:  
        bmr = (10 * weight) + (6.25 * height) - (5 * age)
        if sex == "Male":
            bmr += 5
        elif sex == "Female":
            bmr -= 161
        multiplier = activity_level_map[activity_level]
        return round(bmr * multiplier)


# Layout: Three columns
left_col, mid_col, right_col = st.columns([3, 3, 2])

# Left column
with left_col:
    # st.header("Buffet")

    with st.expander("Profile"):

        col_1, col_2, col_3 = st.columns([1, 1, 1])

        with col_1:
            age = st.number_input("Age", min_value=1, max_value=100, value=18)
            st.session_state.age = age
            weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=70)
            st.session_state.weight = weight
        with col_2:
            sex = st.selectbox("Sex", ["Male", "Female"])
            st.session_state.sex = sex
            activity_level = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"], index=2)
            st.session_state.activity_level = activity_level
        with col_3:
            height = st.number_input("Height (cm)", min_value=100, max_value=300, value=170)
            st.session_state.height = height
            bmr = calculate_bmr(st.session_state.age, st.session_state.sex, st.session_state.height, st.session_state.weight, st.session_state.activity_level)                
            st.text_input("RDA (kcal)", value=bmr, disabled=True)
            st.session_state.rda = bmr
            
        
    

    with st.expander("Full Menu", expanded=st.session_state.stance == 'standing'):
        st.write("Reference: https://www.ijfcm.org/html-article/18750")
        st.write(st.session_state.calorie_table)
    
    if st.session_state.stance == 'collecting':
        df = st.session_state.calorie_table
        search_food = st.text_input("Search for food")
        filtered_df = df[df["Food"].str.contains(search_food, case=False)]
        selected_food = st.selectbox("Select food", filtered_df["Food"])

        add_button, remove_button, clear = st.columns(3)
        with add_button:
            add = st.button("Add to tray")
        with remove_button:
            remove = st.button("Remove from tray")
        with clear:
            clear_tray = st.button("Clear Tray")
        
        if clear_tray: 
            st.session_state.tray = pd.DataFrame(columns=['Food', 'Servings', 'Calories'])
            st.session_state.tray_calories = 0
        if add:
            if selected_food in st.session_state.tray["Food"].values:
                st.session_state.tray.loc[st.session_state.tray["Food"] == selected_food, "Servings"] += 1
            else:
                st.session_state.tray = pd.concat([st.session_state.tray, pd.DataFrame([{"Food": selected_food, "Servings": 1, "Calories": filtered_df[filtered_df["Food"] == selected_food]["Calories"].values[0]}])], ignore_index=True)
        if remove:
            if selected_food in st.session_state.tray["Food"].values:
                st.session_state.tray.loc[st.session_state.tray["Food"] == selected_food, "Servings"] -= 1
                if st.session_state.tray.loc[st.session_state.tray["Food"] == selected_food, "Servings"].values[0] <= 0:
                    st.session_state.tray = st.session_state.tray[st.session_state.tray["Food"] != selected_food]

        tray_calories = 0
        for index, row in st.session_state.tray.iterrows():
            tray_calories += row["Calories"] * row["Servings"]
        st.session_state.tray_calories = tray_calories

        with st.expander("Tray"):
            st.write(f"Tray Calories: {tray_calories} kcal")
            st.write(st.session_state.tray)

    if not st.session_state.eaten_meals.empty:
        with st.expander("Eaten Meals"):
            st.write(st.session_state.eaten_meals)

# Middle column: 
with mid_col:
    st.header("All-Day All-You-Can-Eat Buffet")

    if st.session_state.stance == 'standing':
        st.image("garfield.jpg", use_column_width=True)
        collect = st.button("Grab a tray and start making a meal")
        if collect:
            st.session_state.stance = 'collecting'
            st.rerun()

    if st.session_state.stance == 'collecting':
        st.image("garfield-buffet.gif", use_column_width=True)
        if not st.session_state.tray.empty:
            eat = st.button("Sit and enjoy the meal")
            if eat:
                st.session_state.stance = 'eating'
                st.rerun()

    if st.session_state.stance == 'eating':
        st.image('garfield-eating.gif', use_column_width=True)
        time.sleep(5)
        st.session_state.stance = "standing"
        st.session_state.total_calories += st.session_state.tray_calories
        st.session_state.eaten_meals = pd.concat([st.session_state.eaten_meals, st.session_state.tray], ignore_index=True)
        st.session_state.tray = pd.DataFrame(columns=["Food", "Servings", "Calories"])
        st.session_state.tray_calories = 0
        st.rerun()


# Right column: Vertical calorie meter using Plotly
with right_col:
    # st.header("Calorie Meter")
    
    # Example daily calorie limit
    rda = st.session_state.rda
    max_calories = rda + 1000  
    current_calories = st.session_state.total_calories  # Assuming total_calories is set elsewhere

    # Create the background color shapes for reference ranges based on the new color thresholds
    shapes = [
        # Red range: Below 1800 kcal
        dict(type="rect", x0=0, x1=1, y0=0, y1=rda-500, fillcolor="red", opacity=0.2, line_width=0),
        
        # Orange range: 1800 to 2200 kcal
        dict(type="rect", x0=0, x1=1, y0=rda-500, y1=rda-250, fillcolor="orange", opacity=0.2, line_width=0),
        
        # Green range: 2200 to 2800 kcal
        dict(type="rect", x0=0, x1=1, y0=rda-250, y1=rda+250, fillcolor="green", opacity=0.2, line_width=0),
        
        # Orange range: 2800 to 3200 kcal
        dict(type="rect", x0=0, x1=1, y0=rda+250, y1=rda+500, fillcolor="orange", opacity=0.2, line_width=0),
        
        # Red range: Above 3200 kcal
        dict(type="rect", x0=0, x1=1, y0=rda+500, y1=max_calories, fillcolor="red", opacity=0.2, line_width=0)

    ]

    # Add a white line at y=rda
    shapes.append(dict(type="line", x0=0, x1=1, y0=rda, y1=rda, line=dict(color="yellow", width=2)))

    # Data for the vertical bar
    data = go.Bar(
        x=[0.5],  # Position the bar at the center
        y=[current_calories], 
        marker=dict(
            color='red' if current_calories < rda-500 else 
                'orange' if current_calories < rda-250 else 
                'green' if current_calories < rda+250 else 
                'orange' if current_calories < rda+500 else 
                'red',  # Dynamic coloring based on the calories
            line=dict(color='white', width=2)  # Black outline around the bar
        ),
        orientation='v',  # Vertical bar
        width=0.5  # Make the bar thinner to match the background
    )

    # Set up layout for the bar chart
    layout = go.Layout(
        yaxis=dict(
            range=[0, max_calories], 
            title="Calories (kcal)", 
            showgrid=True, 
            gridcolor='lightgray',  # Soft grid lines
            zeroline=True, 
            zerolinecolor='black'  # Highlight the zero line for better clarity
        ),
        xaxis=dict(
            showticklabels=False,
            range=[0, 1],  # Keep the x-axis to range from 0 to 1 (for the bar)
        ),
        height=500,  # Adjust height of the bar
        width=200,   # Adjust width of the chart
        margin=dict(l=40, r=40, t=40, b=40),
        plot_bgcolor='black',  # White background for better contrast
        shapes=shapes,  # Add the background color shapes here
        showlegend=False,
        hovermode='closest'
    )

    # Create the figure with the bar chart
    fig = go.Figure(data=[data], layout=layout)

    # Adding calorie count text above the bar
    fig.add_trace(go.Scatter(
        x=[0.5],  # Position text in the center of the bar
        y=[current_calories],
        text=[f"{current_calories} kcal"], 
        mode='text', 
        textposition='top center',
        showlegend=False
    ))

    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Display exact calorie count
    col3, col4 = st.columns([2, 1])
    with col3:
        st.write(f"Total Calories: {current_calories} kcal")
    with col4:
        reset = st.button("Reset")
        if reset:
            st.session_state.total_calories = 0
            st.session_state.eaten_meals = pd.DataFrame(columns=['Food', 'Servings', 'Calories'])
            st.rerun()

