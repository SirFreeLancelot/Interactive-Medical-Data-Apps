import streamlit as st
import pandas as pd
import plotly.graph_objs as go

st.set_page_config(layout="wide")

# Title of the app
st.title("Blood Glucose Level Tracker")

# Input fields for date, time, and blood glucose level
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    date = st.date_input("Select Date", max_value=pd.to_datetime('today').date())
with col2:
    time = st.time_input("Select Time")
with col3:
    glucose = st.number_input("Enter Blood Glucose Level", min_value=0, max_value=500)

# Store the data in a DataFrame (simulating saving it over time)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['DateTime', 'Glucose Level'])

with col4:
    # Center the button horizontally and vertically
    st.markdown("<div style='text-align: center; display: flex; align-items: center; justify-content: center'>", unsafe_allow_html=True)
    # Add data to the session state DataFrame
    if st.button('Submit', type='primary'):
        # Combine date and time
        datetime = pd.to_datetime(f"{date} {time}")
        # Check if the data already exists
        if datetime in st.session_state.data['DateTime'].values:
            # Update the existing data
            st.session_state.data.loc[st.session_state.data['DateTime'] == datetime, 'Glucose Level'] = glucose
        else:
            # Append the new data
            new_data = pd.DataFrame({'DateTime': [datetime], 'Glucose Level': [glucose]})
            st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
        # Sort the data by time
        st.session_state.data = st.session_state.data.sort_values(by='DateTime')
    st.markdown("</div>", unsafe_allow_html=True)

with col5:
    # Center the button horizontally and vertically
    st.markdown("<div style='text-align: center; display: flex; align-items: center; justify-content: center'>", unsafe_allow_html=True)
    # Button to delete the data for the selected date and time
    if st.button('Delete', type='secondary'):
        datetime = pd.to_datetime(f"{date} {time}")
        # Check if the data already exists
        if datetime in st.session_state.data['DateTime'].values:
            # Delete the existing data
            st.session_state.data = st.session_state.data[st.session_state.data['DateTime'] != datetime]

# Plot the data if available
if not st.session_state.data.empty:
    # Create a plotly figure
    fig = go.Figure()

    # Add the line for glucose level
    fig.add_trace(go.Scatter(
        x=st.session_state.data['DateTime'],
        y=st.session_state.data['Glucose Level'],
        mode='lines+markers',
        name='Blood Glucose Level',
        line=dict(color='white', width=4),
        marker=dict(size=10, color='white'),
        hovertemplate='Time: %{x}<br>Glucose Level: %{y}'
    ))

    # Add colored zones for glucose ranges
    if len(st.session_state.data) > 1:
        dt_range = max(st.session_state.data['DateTime']) - min(st.session_state.data['DateTime'])
        if dt_range.days == 0:
            x0 = min(st.session_state.data['DateTime']) - pd.Timedelta(hours=dt_range.seconds//36000, minutes=(dt_range.seconds//600))
            x1 = max(st.session_state.data['DateTime']) + pd.Timedelta(hours=dt_range.seconds//36000, minutes=(dt_range.seconds//600))
        else:
            x0 = min(st.session_state.data['DateTime']) - pd.Timedelta(days=dt_range.days/10)
            x1 = max(st.session_state.data['DateTime']) + pd.Timedelta(days=dt_range.days/10)
    else:
        x0 = st.session_state.data['DateTime'].iloc[0] - pd.Timedelta(minutes=1)
        x1 = st.session_state.data['DateTime'].iloc[0] + pd.Timedelta(minutes=1)
        
    # fig.add_shape(type="rect", x0=x0, x1=x1, y0=0, y1=70, fillcolor="red", opacity=0.5, line_width=0)
    fig.add_shape(type="rect", x0=x0, x1=x1, y0=70, y1=140, fillcolor="green", opacity=0.5, line_width=0)
    fig.add_shape(type="rect", x0=x0, x1=x1, y0=140, y1=200, fillcolor="yellow", opacity=0.5, line_width=0)
    fig.add_shape(type="rect", x0=x0, x1=x1, y0=200, y1=500, fillcolor="red", opacity=0.5, line_width=0)
    
    # Update layout for proper scaling and axis labels
    fig.update_layout(
        title="Blood Glucose Levels Over Time",
        xaxis_title="Date/Time (YYYY-MM-DD HH:MM)",
        yaxis_title="Glucose Level (mg/dL)",
        xaxis=dict(type="date", tickformat="%Y-%m-%d %H:%M", showgrid=True),
        yaxis=dict(range=[0, 500]),
        height=600
    )

    # Display the figure in Streamlit
    st.plotly_chart(fig)

# Option to display the DataFrame (optional)
if st.checkbox("Show Data Table"):
    st.write(st.session_state.data)
