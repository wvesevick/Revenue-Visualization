import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# Function to compute data for a given fiscal year or all years
def get_year_data(year, installations, churn_data, is_all=False):
    # Create DataFrame from manual churn data
    churn_df = pd.DataFrame(list(churn_data.items()), columns=['churn_month', 'mrr'])
    churn_df['churn_month'] = pd.to_datetime(churn_df['churn_month'])
    
    # Group churn by month
    churn_group = churn_df.groupby('churn_month')['mrr'].sum()

    install_months = list(installations.keys())
    churn_months = list(churn_group.index) if not churn_group.empty else []
    all_months = sorted(set(install_months + churn_months))

    if is_all:
        start_date = datetime(2023, 11, 1)  # Start from FY2024
        oct_end = pd.Timestamp('2026-10-01')  # Extend to FY2026
    else:
        start_date = datetime(year - 1, 11, 1)
        oct_end = pd.Timestamp(f'{year}-10-01')

    if not all_months:
        all_months = pd.date_range(start=start_date, end=oct_end, freq='MS').tolist()
    else:
        min_month = min(all_months)
        max_month = max(all_months)
        if max_month < oct_end:
            max_month = oct_end
        if min_month > start_date:
            min_month = start_date
        all_months = pd.date_range(start=min_month, end=max_month, freq='MS').tolist()

    month_labels = [month.strftime('%b %Y') for month in all_months]

    churn = {month: churn_group.get(month, 0) for month in all_months}

    mrr_with_churn = []
    current_mrr = 0
    for month in all_months:
        install = installations.get(month, 0)
        churn_amount = churn.get(month, 0)
        current_mrr += install - churn_amount
        mrr_with_churn.append(current_mrr)           # <<< NO round

    cumulative_with_churn = [sum(mrr_with_churn[:i+1]) for i in range(len(mrr_with_churn))]

    mrr_without_churn = []
    current_mrr_no_churn = 0
    for month in all_months:
        install = installations.get(month, 0)
        current_mrr_no_churn += install
        mrr_without_churn.append(current_mrr_no_churn)   # <<< NO round

    cumulative_without_churn = [sum(mrr_without_churn[:i+1]) for i in range(len(mrr_with_churn))]

    # Keep full decimals for bar data (only rounded for display later)
    installations_monthly = [installations.get(month, 0) for month in all_months]
    churn_monthly = [-churn.get(month, 0) for month in all_months]
    churn_monthly_positive = [churn.get(month, 0) for month in all_months]
    net_change = [install - churn.get(month, 0) for install, month in zip(installations_monthly, all_months)]

    return {
        'month_labels': month_labels,
        'cumulative_with_churn': cumulative_with_churn,
        'cumulative_without_churn': cumulative_without_churn,
        'installations_monthly': installations_monthly,
        'churn_monthly': churn_monthly,
        'churn_monthly_positive': churn_monthly_positive,
        'net_change': net_change,
        'mrr_with_churn': mrr_with_churn,
        'cumulative_with_churn': cumulative_with_churn
    }

# Function to get annotations for a year (only for bar graph)
def get_annotations(data, is_all=False):
    ann = []
    for i, month in enumerate(data['month_labels']):
        install_val = data['installations_monthly'][i]
        if install_val != 0:
            ann.append(dict(
                x=month, y=install_val, text=f'${round(install_val):,}',
                showarrow=True, arrowhead=2, ax=0, ay=-40 if install_val >= 0 else 40,
                xref='x2' if not is_all else 'x2', yref='y2' if not is_all else 'y2'
            ))
        churn_val = data['churn_monthly'][i]
        if churn_val != 0:
            ann.append(dict(
                x=month, y=churn_val, text=f'${round(data["churn_monthly_positive"][i]):,}',
                showarrow=True, arrowhead=2, ax=0, ay=40 if churn_val <= 0 else -40,
                xref='x2' if not is_all else 'x2', yref='y2' if not is_all else 'y2'
            ))
    return ann

# ----------------------------------------------------------------------
# Hardcoded installations for FY2026
installations_2026 = {
    pd.Timestamp('2025-11-01'): 15157.00,
    pd.Timestamp('2025-12-01'): 17565.00,
    pd.Timestamp('2026-01-01'): 22492.00,
    pd.Timestamp('2026-02-01'): 0,
    pd.Timestamp('2026-03-01'): 0,
    pd.Timestamp('2026-04-01'): 0,
    pd.Timestamp('2026-05-01'): 0,
    pd.Timestamp('2026-06-01'): 0,
    pd.Timestamp('2026-07-01'): 0,
    pd.Timestamp('2026-08-01'): 0,
    pd.Timestamp('2026-09-01'): 0,
    pd.Timestamp('2026-10-01'): 0
}

# Hardcoded churn for FY2026
churn_2026 = {
    pd.Timestamp('2025-11-01'): 16279.00,
    pd.Timestamp('2025-12-01'): 9692.00,
    pd.Timestamp('2026-01-01'): 15684.00,
    pd.Timestamp('2026-02-01'): 0,
    pd.Timestamp('2026-03-01'): 0,
    pd.Timestamp('2026-04-01'): 0,
    pd.Timestamp('2026-05-01'): 0,
    pd.Timestamp('2026-06-01'): 0,
    pd.Timestamp('2026-07-01'): 0,
    pd.Timestamp('2026-08-01'): 0,
    pd.Timestamp('2026-09-01'): 0,
    pd.Timestamp('2026-10-01'): 0
}

# Hardcoded installations for FY2025
installations_2025 = {
    pd.Timestamp('2024-11-01'): 0.00,
    pd.Timestamp('2024-12-01'): 0.00,
    pd.Timestamp('2025-01-01'): 0.00,
    pd.Timestamp('2025-02-01'): 0.00,
    pd.Timestamp('2025-03-01'): 0.00,
    pd.Timestamp('2025-04-01'): 0.00,
    pd.Timestamp('2025-05-01'): 0.00,
    pd.Timestamp('2025-06-01'): 0.00,
    pd.Timestamp('2025-07-01'): 0.00,
    pd.Timestamp('2025-08-01'): 0.00,
    pd.Timestamp('2025-09-01'): 0.00,
    pd.Timestamp('2025-10-01'): 0.00
}

# Hardcoded churn for FY2025
churn_2025 = {
    pd.Timestamp('2024-11-01'): 0.00,
    pd.Timestamp('2024-12-01'): 0.00,
    pd.Timestamp('2025-01-01'): 0.00,
    pd.Timestamp('2025-02-01'): 0.00,
    pd.Timestamp('2025-03-01'): 0.00,
    pd.Timestamp('2025-04-01'): 0.00,
    pd.Timestamp('2025-05-01'): 0.00,
    pd.Timestamp('2025-06-01'): 0.00,
    pd.Timestamp('2025-07-01'): 0.00,
    pd.Timestamp('2025-08-01'): 0.00,
    pd.Timestamp('2025-09-01'): 0.00,
    pd.Timestamp('2025-10-01'): 0.00
}

# Installations for FY2024
installations_2024 = {
    pd.Timestamp('2023-11-01'): 0.00,
    pd.Timestamp('2023-12-01'): 0.00,
    pd.Timestamp('2024-01-01'): 0.00,
    pd.Timestamp('2024-02-01'): 0.00,
    pd.Timestamp('2024-03-01'): 0.00,
    pd.Timestamp('2024-04-01'): 0.00,
    pd.Timestamp('2024-05-01'): 0.00,
    pd.Timestamp('2024-06-01'): 0.00,
    pd.Timestamp('2024-07-01'): 0.00,
    pd.Timestamp('2024-08-01'): 0.00,
    pd.Timestamp('2024-09-01'): 0.00,
    pd.Timestamp('2024-10-01'): 0.00
}

# Hardcoded churn for FY2024
churn_2024 = {
    pd.Timestamp('2023-11-01'): 0.00,
    pd.Timestamp('2023-12-01'): 0.00,
    pd.Timestamp('2024-01-01'): 0.00,
    pd.Timestamp('2024-02-01'): 0.00,
    pd.Timestamp('2024-03-01'): 0.00,
    pd.Timestamp('2024-04-01'): 0.00,
    pd.Timestamp('2024-05-01'): 0.00,
    pd.Timestamp('2024-06-01'): 0.00,
    pd.Timestamp('2024-07-01'): 0.00,
    pd.Timestamp('2024-08-01'): 0.00,
    pd.Timestamp('2024-09-01'): 0.00,
    pd.Timestamp('2024-10-01'): 0.00
}

# ----------------------------------------------------------------------
# Combine installations and churn for the "All" tab (now includes FY2026)
installations_all = {**installations_2024, **installations_2025, **installations_2026}
churn_all = {**churn_2024, **churn_2025, **churn_2026}

# Compute data for each year (including FY2026)
data_2026 = get_year_data(2026, installations_2026, churn_2026)
data_2025 = get_year_data(2025, installations_2025, churn_2025)
data_2024 = get_year_data(2024, installations_2024, churn_2024)
data_all = get_year_data(2026, installations_all, churn_all, is_all=True)

# Compute annotations for each year
ann_2026 = get_annotations(data_2026)
ann_2025 = get_annotations(data_2025)
ann_2024 = get_annotations(data_2024)
ann_all  = get_annotations(data_all, is_all=True)

# ----------------------------------------------------------------------
# Create subplots (single figure for all tabs)
fig = make_subplots(
    rows=2, cols=2,
    specs=[[{"type": "scatter"}, {"type": "bar"}],
           [{"type": "table", "colspan": 2}, None]],
    subplot_titles=('Cumulative Revenue Projection', 'Monthly Installations and Churn', 'Revenue Data Table'),
    vertical_spacing=0.1,
    horizontal_spacing=0.05
)

# ----------------------------------------------------------------------
# FY2025 traces (visible initially)
fig.add_trace(
    go.Scatter(
        x=data_2025['month_labels'], y=data_2025['cumulative_with_churn'],
        mode='lines+markers', name='With Churn',
        line=dict(color='blue', width=3),
        visible=True
    ),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(
        x=data_2025['month_labels'], y=data_2025['cumulative_without_churn'],
        mode='lines+markers', name='No Churn (Hypothetical)',
        line=dict(color='green', width=3, dash='dash'),
        fill='tonexty', fillcolor='rgba(0, 0, 255, 0.3)',
        visible=True
    ),
    row=1, col=1
)
fig.add_trace(
    go.Bar(
        x=data_2025['month_labels'], y=data_2025['installations_monthly'],
        name='Installations', marker_color='green', width=0.4,
        visible=True
    ),
    row=1, col=2
)
fig.add_trace(
    go.Bar(
        x=data_2025['month_labels'], y=data_2025['churn_monthly'],
        name='Churn', marker_color='red', width=0.4,
        visible=True
    ),
    row=1, col=2
)
fig.add_trace(
    go.Table(
        header=dict(
            values=['Month', 'Installations', 'Churn', 'Net Change', 'MRR with Churn', 'Cumulative Revenue'],
            fill_color='black', font=dict(color='white', size=12),
            align=['left', 'right', 'right', 'right', 'right', 'right']
        ),
        cells=dict(
            values=[
                data_2025['month_labels'],
                [f'${round(val):,}' for val in data_2025['installations_monthly']],
                [f'${round(val):,}' for val in data_2025['churn_monthly_positive']],
                [f'${round(val):,}' for val in data_2025['net_change']],
                [f'${round(val):,}' for val in data_2025['mrr_with_churn']],
                [f'${round(val):,}' for val in data_2025['cumulative_with_churn']]
            ],
            fill_color='black', font=dict(color='white', size=11),
            align=['left', 'right', 'right', 'right', 'right', 'right']
        ),
        visible=True
    ),
    row=2, col=1
)

# FY2024 traces (hidden)
fig.add_trace(
    go.Scatter(
        x=data_2024['month_labels'], y=data_2024['cumulative_with_churn'],
        mode='lines+markers', name='With Churn',
        line=dict(color='blue', width=3),
        visible=False
    ),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(
        x=data_2024['month_labels'], y=data_2024['cumulative_without_churn'],
        mode='lines+markers', name='No Churn (Hypothetical)',
        line=dict(color='green', width=3, dash='dash'),
        fill='tonexty', fillcolor='rgba(0, 0, 255, 0.3)',
        visible=False
    ),
    row=1, col=1
)
fig.add_trace(
    go.Bar(
        x=data_2024['month_labels'], y=data_2024['installations_monthly'],
        name='Installations', marker_color='green', width=0.4,
        visible=False
    ),
    row=1, col=2
)
fig.add_trace(
    go.Bar(
        x=data_2024['month_labels'], y=data_2024['churn_monthly'],
        name='Churn', marker_color='red', width=0.4,
        visible=False
    ),
    row=1, col=2
)
fig.add_trace(
    go.Table(
        header=dict(
            values=['Month', 'Installations', 'Churn', 'Net Change', 'MRR with Churn', 'Cumulative Revenue'],
            fill_color='black', font=dict(color='white', size=12),
            align=['left', 'right', 'right', 'right', 'right', 'right']
        ),
        cells=dict(
            values=[
                data_2024['month_labels'],
                [f'${round(val):,}' for val in data_2024['installations_monthly']],
                [f'${round(val):,}' for val in data_2024['churn_monthly_positive']],
                [f'${round(val):,}' for val in data_2024['net_change']],
                [f'${round(val):,}' for val in data_2024['mrr_with_churn']],
                [f'${round(val):,}' for val in data_2024['cumulative_with_churn']]
            ],
            fill_color='black', font=dict(color='white', size=11),
            align=['left', 'right', 'right', 'right', 'right', 'right']
        ),
        visible=False
    ),
    row=2, col=1
)

# FY2026 traces (hidden)
fig.add_trace(
    go.Scatter(
        x=data_2026['month_labels'], y=data_2026['cumulative_with_churn'],
        mode='lines+markers', name='With Churn',
        line=dict(color='blue', width=3),
        visible=False
    ),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(
        x=data_2026['month_labels'], y=data_2026['cumulative_without_churn'],
        mode='lines+markers', name='No Churn (Hypothetical)',
        line=dict(color='green', width=3, dash='dash'),
        fill='tonexty', fillcolor='rgba(0, 0, 255, 0.3)',
        visible=False
    ),
    row=1, col=1
)
fig.add_trace(
    go.Bar(
        x=data_2026['month_labels'], y=data_2026['installations_monthly'],
        name='Installations', marker_color='green', width=0.4,
        visible=False
    ),
    row=1, col=2
)
fig.add_trace(
    go.Bar(
        x=data_2026['month_labels'], y=data_2026['churn_monthly'],
        name='Churn', marker_color='red', width=0.4,
        visible=False
    ),
    row=1, col=2
)
fig.add_trace(
    go.Table(
        header=dict(
            values=['Month', 'Installations', 'Churn', 'Net Change', 'MRR with Churn', 'Cumulative Revenue'],
            fill_color='black', font=dict(color='white', size=12),
            align=['left', 'right', 'right', 'right', 'right', 'right']
        ),
        cells=dict(
            values=[
                data_2026['month_labels'],
                [f'${round(val):,}' for val in data_2026['installations_monthly']],
                [f'${round(val):,}' for val in data_2026['churn_monthly_positive']],
                [f'${round(val):,}' for val in data_2026['net_change']],
                [f'${round(val):,}' for val in data_2026['mrr_with_churn']],
                [f'${round(val):,}' for val in data_2026['cumulative_with_churn']]
            ],
            fill_color='black', font=dict(color='white', size=11),
            align=['left', 'right', 'right', 'right', 'right', 'right']
        ),
        visible=False
    ),
    row=2, col=1
)

# All traces (hidden)
fig.add_trace(
    go.Scatter(
        x=data_all['month_labels'], y=data_all['cumulative_with_churn'],
        mode='lines+markers', name='With Churn',
        line=dict(color='blue', width=3),
        visible=False
    ),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(
        x=data_all['month_labels'], y=data_all['cumulative_without_churn'],
        mode='lines+markers', name='No Churn (Hypothetical)',
        line=dict(color='green', width=3, dash='dash'),
        fill='tonexty', fillcolor='rgba(0, 0, 255, 0.3)',
        visible=False
    ),
    row=1, col=1
)
fig.add_trace(
    go.Bar(
        x=data_all['month_labels'], y=data_all['installations_monthly'],
        name='Installations', marker_color='green', width=0.4,
        visible=False
    ),
    row=1, col=2
)
fig.add_trace(
    go.Bar(
        x=data_all['month_labels'], y=data_all['churn_monthly'],
        name='Churn', marker_color='red', width=0.4,
        visible=False
    ),
    row=1, col=2
)
fig.add_trace(
    go.Table(
        header=dict(
            values=['Month', 'Installations', 'Churn', 'Net Change', 'MRR with Churn', 'Cumulative Revenue'],
            fill_color='black', font=dict(color='white', size=12),
            align=['left', 'right', 'right', 'right', 'right', 'right']
        ),
        cells=dict(
            values=[
                data_all['month_labels'],
                [f'${round(val):,}' for val in data_all['installations_monthly']],
                [f'${round(val):,}' for val in data_all['churn_monthly_positive']],
                [f'${round(val):,}' for val in data_all['net_change']],
                [f'${round(val):,}' for val in data_all['mrr_with_churn']],
                [f'${round(val):,}' for val in data_all['cumulative_with_churn']]
            ],
            fill_color='black', font=dict(color='white', size=11),
            align=['left', 'right', 'right', 'right', 'right', 'right']
        ),
        visible=False
    ),
    row=2, col=1
)

# ----------------------------------------------------------------------
# Fixed annotations (shared by all tabs)
fixed_ann = [ann.to_plotly_json() for ann in fig.layout.annotations]
fixed_ann_all = [ann.to_plotly_json() for ann in fig.layout.annotations]

# Initial annotation (FY2025)
fig.update_layout(annotations=[
    dict(
        text='FY2025',
        x=0, y=1.15, xref='paper', yref='paper',
        showarrow=False, font=dict(size=14, color='white'),
        xanchor='left', yanchor='top'
    )
] + fixed_ann + ann_2025)

# ----------------------------------------------------------------------
# Layout & dropdown (now 4 buttons)
fig.update_layout(
    template='plotly_dark',
    title=dict(
        text='Revenue Projection',
        font=dict(size=24, color='white'),
        x=0.5,
        xanchor='center'
    ),
    showlegend=True,
    legend=dict(x=0.01, y=0.99, bgcolor='rgba(0,0,0,0.5)', font=dict(size=14)),
    height=1200,
    barmode='group',
    updatemenus=[
        dict(
            type='dropdown',
            buttons=[
                # FY2025
                dict(label='FY2025',
                     method='update',
                     args=[
                         {'visible': [True, True, True, True, True,
                                      False, False, False, False, False,
                                      False, False, False, False, False,
                                      False, False, False, False, False]},
                         {
                             'annotations': [
                                 dict(text='FY2025', x=0, y=1.15, xref='paper', yref='paper',
                                      showarrow=False, font=dict(size=14, color='white'),
                                      xanchor='left', yanchor='top')
                             ] + fixed_ann + ann_2025,
                             'xaxis.categoryarray': data_2025['month_labels'],
                             'xaxis2.categoryarray': data_2025['month_labels']
                         }
                     ]),
                # FY2024
                dict(label='FY2024',
                     method='update',
                     args=[
                         {'visible': [False, False, False, False, False,
                                      True, True, True, True, True,
                                      False, False, False, False, False,
                                      False, False, False, False, False]},
                         {
                             'annotations': [
                                 dict(text='FY2024', x=0, y=1.15, xref='paper', yref='paper',
                                      showarrow=False, font=dict(size=14, color='white'),
                                      xanchor='left', yanchor='top')
                             ] + fixed_ann + ann_2024,
                             'xaxis.categoryarray': data_2024['month_labels'],
                             'xaxis2.categoryarray': data_2024['month_labels']
                         }
                     ]),
                # FY2026 (new)
                dict(label='FY2026',
                     method='update',
                     args=[
                         {'visible': [False, False, False, False, False,
                                      False, False, False, False, False,
                                      True, True, True, True, True,
                                      False, False, False, False, False]},
                         {
                             'annotations': [
                                 dict(text='FY2026', x=0, y=1.15, xref='paper', yref='paper',
                                      showarrow=False, font=dict(size=14, color='white'),
                                      xanchor='left', yanchor='top')
                             ] + fixed_ann + ann_2026,
                             'xaxis.categoryarray': data_2026['month_labels'],
                             'xaxis2.categoryarray': data_2026['month_labels']
                         }
                     ]),
                # All
                dict(label='All (FY2024-FY2026)',
                     method='update',
                     args=[
                         {'visible': [False]*15 + [True]*5},
                         {
                             'annotations': [
                                 dict(text='All (FY2024-FY2026)', x=0, y=1.15, xref='paper', yref='paper',
                                      showarrow=False, font=dict(size=14, color='white'),
                                      xanchor='left', yanchor='top')
                             ] + fixed_ann_all + ann_all,
                             'xaxis.categoryarray': data_all['month_labels'],
                             'xaxis2.categoryarray': data_all['month_labels'],
                             'title': {'text': 'Revenue Projection: The Wedge Effect - All (FY2024-FY2026)'}
                         }
                     ])
            ],
            direction='down',
            x=0.1,
            xanchor='left',
            y=1.15,
            yanchor='top'
        )
    ]
)

# ----------------------------------------------------------------------
# Axes formatting
fig.update_yaxes(
    title_text='Cumulative Revenue ($)',
    tickprefix='$', tickformat=',.0f',
    title_font=dict(size=18),
    tickfont=dict(size=14),
    row=1, col=1
)

fig.update_yaxes(
    title_text='Monthly Change ($)',
    tickprefix='$', tickformat=',.0f',
    title_font=dict(size=18),
    tickfont=dict(size=14),
    row=1, col=2
)
fig.update_xaxes(
    tickangle=45,
    title_font=dict(size=18),
    tickfont=dict(size=14),
    row=1, col=2
)
fig.update_xaxes(type='category', row=1, col=1)
fig.update_xaxes(type='category', row=1, col=2)

# ----------------------------------------------------------------------
# Display and save
fig.show()
fig.write_html('mrr_churn_updated_with_2026.html')
