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


# Layout: Three columns
left_col, mid_col, right_col = st.columns([3, 3, 2])

# Left column
with left_col:
    # st.header("Buffet")
    with st.expander("Full Menu", expanded=st.session_state.stance == 'standing'):
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
    max_calories = 4000  
    current_calories = st.session_state.total_calories  # Assuming total_calories is set elsewhere

    # Create the background color shapes for reference ranges based on the new color thresholds
    shapes = [
        # Red range: Below 1800 kcal
        dict(type="rect", x0=0, x1=1, y0=0, y1=1800, fillcolor="red", opacity=0.2, line_width=0),
        
        # Orange range: 1800 to 2200 kcal
        dict(type="rect", x0=0, x1=1, y0=1800, y1=2200, fillcolor="orange", opacity=0.2, line_width=0),
        
        # Green range: 2200 to 2800 kcal
        dict(type="rect", x0=0, x1=1, y0=2200, y1=2800, fillcolor="green", opacity=0.2, line_width=0),
        
        # Orange range: 2800 to 3200 kcal
        dict(type="rect", x0=0, x1=1, y0=2800, y1=3200, fillcolor="orange", opacity=0.2, line_width=0),
        
        # Red range: Above 3200 kcal
        dict(type="rect", x0=0, x1=1, y0=3200, y1=max_calories, fillcolor="red", opacity=0.2, line_width=0)
    ]

    # Data for the vertical bar
    data = go.Bar(
        x=[0.5],  # Position the bar at the center
        y=[current_calories], 
        marker=dict(
            color='red' if current_calories < 1800 else 
                'orange' if current_calories < 2200 else 
                'green' if current_calories < 2800 else 
                'orange' if current_calories < 3200 else 
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

