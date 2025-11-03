import streamlit as st
import pandas as pd
import preprocessor , helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff   

df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')

df = preprocessor.preprocess(df , region_df)

st.sidebar.title('Olympics Analysis')
st.sidebar.image('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSbY76_sWNIgiR-WrTCKpkdQPAdDBLjcAPM8g&s')
user_menu = st.sidebar.radio(
    'Select an Option',
    ('Medal tally','Overall analysis','Country-wise analysis','Athlete wise analysis')
)


if user_menu == 'Medal tally':
    st.sidebar.header('Medal Tally')
    years , country = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox('Select Year',years)
    selected_country = st.sidebar.selectbox('Select Country',country)

    medal_tally = helper.fetch_medal_tally(df , selected_year , selected_country)
    
    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title('Overall Medal Tally')
    if selected_year != 'Overall' and selected_country == 'Overall':    
        st.title('Medal Tally in ' + str(selected_year) + ' Olympics')
    if selected_year == 'Overall' and selected_country != 'Overall':    
        st.title(selected_country + ' Overall Performance')
    if selected_year != 'Overall' and selected_country != 'Overall':    
        st.title(selected_country + ' Performance in ' + str(selected_year) + ' Olympics')

    st.table(medal_tally)


if user_menu == 'Overall analysis':
    st.title('Overall Analysis')
    editions = df['Year'].nunique() - 1
    cities = df['City'].nunique()
    sports = df['Sport'].nunique()
    events = df['Event'].nunique()
    athletes = df['Name'].nunique()
    nations = df['region'].nunique()

    st.header('Top Statistics')
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader('Editions')
        st.title(editions)
    with col2:
        st.subheader('Hosts')
        st.title(cities)
    with col3:
        st.subheader('Sports')
        st.title(sports)
    with col1:
        st.subheader('Events')
        st.title(events)
    with col2:
        st.subheader('Nations')
        st.title(nations)
    with col3:
        st.subheader('Athletes')
        st.title(athletes)

    nations_over_time = helper.data_over_time(df , 'region')

    fig = px.line(nations_over_time , x ='Year' , y =  'region')
    st.header('Participating Nations Over the Years')
    st.plotly_chart(fig)

    events_over_time = helper.data_over_time(df , 'Event')

    fig = px.line(events_over_time , x ='Year' , y =  'Event')
    st.header('Events Over the Years')
    st.plotly_chart(fig)

    athlete_over_time = helper.data_over_time(df , 'Name')

    fig = px.line(athlete_over_time , x ='Year' , y =  'Name')
    st.header('Athletes Over the Years')
    st.plotly_chart(fig)

    st.title('No. of Events over time(Every Sport)')
    fig, ax = plt.subplots(figsize=(20,20))

    x = df.drop_duplicates(['Year','Sport','Event'])
    sns.heatmap(x.pivot_table(index = 'Sport',columns='Year', values='Event', aggfunc='count').fillna(0).astype    ("int") , annot = True)

    st.pyplot(fig)

    st.title("Most Successful Athletes")
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0,'Overall')
    selected_sport = st.selectbox('Select a Sport',sport_list)
    x = helper.most_successful_athletes(df , selected_sport)
    st.table(x)

if user_menu == 'Country-wise analysis':

    st.sidebar.title('Country Wise Analysis')
    country_list = df['region'].dropna().unique().tolist()
    country_list.sort()
    selected_country = st.sidebar.selectbox('Select a Country',country_list)

    country_df = helper.yearwise_medal_tally(df , selected_country)

    fig = px.line(country_df , x = 'Year' , y = 'Medal')
    st.title(selected_country + ' Yearwise Medal Tally')
    st.plotly_chart(fig)

    pt = helper.country_event_heatmap(df , selected_country)
    st.title(selected_country + ' Event Heatmap')
    fig, ax = plt.subplots(figsize=(20,20))
    sns.heatmap(pt , annot = True)
    st.pyplot(fig)

    top10_df = helper.most_successful_countrywise(df , selected_country)
    st.title('Top 10 Athletes of ' + selected_country)
    st.table(top10_df)


if user_menu == 'Athlete wise analysis':
    st.title('Athlete Wise Analysis')

    athlete_df = df.drop_duplicates(subset = ['Name' , 'region'])

    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    # Prepare datasets and labels, filter out any empty series to avoid passing
    # empty iterables to plotly's create_distplot which raises ValueError
    datasets = [x1, x2, x3, x4]
    labels = ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist']

    filtered = [(d, l) for d, l in zip(datasets, labels) if (hasattr(d, 'empty') and not d.empty) or (not hasattr(d, 'empty') and len(d) > 0)]

    if not filtered:
        st.header('Distribution of Age')
        st.warning('No age data available to show the distribution.')
    else:
        hist_data = [item[0].tolist() if hasattr(item[0], 'tolist') else list(item[0]) for item in filtered]
        group_labels = [item[1] for item in filtered]
        fig = ff.create_distplot(hist_data, group_labels, show_hist=False, show_rug=False)
        fig.update_layout(autosize=False, width=1000, height=600)
        st.header('Distribution of Age')
        st.plotly_chart(fig)

    x  = []
    name = []
    famous_sports = ['Basketball' , 'Judo' , 'Football' , 'Tug-Of-War' , 'Athletics' , 'Swimming' , 'Badminton' , 'Sailing' , 'Gymnastics' , 'Artistic Gymnastics' , 'Rowing' , 'Fencing' , 'Shooting' , 'Boxing' ]

    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        gold_ages = temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna()

        # Skip sports with no gold-medalist age data to avoid empty traces
        if gold_ages.empty:
            continue

        x.append(gold_ages.tolist())
        name.append(sport)
    if not x:
        st.header('Age Distribution in Various Sports(For Gold Medalists)')
        st.warning('No gold-medalist age data available for the selected sports.')
    else:
        fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
        fig.update_layout(autosize=False, width=1000, height=600)
        st.header('Age Distribution in Various Sports(For Gold Medalists)')
        st.plotly_chart(fig)


    st.header('Weight vs Height Analysis')
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()   
    sport_list.insert(0,'Overall')

    selected_sport = st.selectbox('Select a Sport',sport_list)
    temp_df = helper.weight_v_height(df , selected_sport)           
    fig , ax = plt.subplots()
    ax = sns.scatterplot(temp_df , x = 'Weight' , y = 'Height' , hue = 'Medal' , style = 'Medal' , s = 60)
    st.pyplot(fig) 

    st.title("Men VS Women Participation Over the Years")
    final = helper.men_vs_women(df)

    fig = px.line(final, x='Year', y=['Male Athletes', 'Female Athletes'])
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)