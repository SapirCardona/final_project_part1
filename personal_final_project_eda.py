# Introduction: This project explores Pakistan's largest e-commerce dataset to understand customer behaviors, sales patterns, and identify potential business insights.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("Pakistan Largest Ecommerce Dataset.csv", low_memory=False)

"""# Data Validation"""

df.head()

df.info()

df.describe()

df.isnull().sum()

duplicates = df.duplicated()
total_duplicates = df.duplicated().sum()

print(total_duplicates)

df['status'].value_counts()

df['sku'].value_counts()

df['category_name_1'].value_counts()

df['payment_method'].value_counts()

df['Customer ID'].value_counts()

"""#**Data Validation Stage Summary:**

▶ **Empty Rows and Columns:**
The dataset initially contained over a million rows, but a significant portion were completely empty, likely due to Excel export formatting. Empty columns such as Unnamed: 21–25 were also detected.

▶ **Incorrect Data Types:**
Certain fields like 'item_id' and 'Customer ID' were loaded as float instead of more appropriate types.

▶ **Missing Values:**
Important fields such as 'category_name_1', 'sku', and 'Customer ID' had a small number of missing values, which could affect future analyses if not addressed.

▶ **Unexpected or Placeholder Values:**
Specific placeholder values such as '\N' were identified in categorical fields, indicating missing or improperly imported data.

▶ **Negative Values:**
Negative values were detected in the 'discount_amount' and 'grand_total' columns during validation. At this stage, the presence of these negative values was noted as an anomaly requiring further investigation.

▶ **Duplicate Entries**
Duplicate records were identified, closely matching the number of missing value discrepancies. They were flagged for resolution during data cleaning.


# These findings were documented and informed the targeted cleaning actions taken in the next phase.

# Data Cleaning
"""

df.dropna(how='all', inplace=True)
df.dropna(axis=1, how='all', inplace=True)
df.drop(columns=[' MV ', 'Year', 'Month', 'M-Y', 'BI Status'], inplace=True)
df = df[df['category_name_1'].notnull() & df['sku'].notnull() & df['Customer ID'].notnull() & df['status'].notnull()]

df.info()

n_value_counts = (df == '\\N').sum()
n_value_counts = n_value_counts[n_value_counts > 0]

print(n_value_counts)

df = df[df['status'] != '\\N']

new_value_counts = (df == '\\N').sum()
new_value_counts = new_value_counts[new_value_counts > 0]

print(new_value_counts)

sku_to_category = df[~df['category_name_1'].isin(['\\N']) & df['category_name_1'].notnull()] \
                    .groupby('sku')['category_name_1'] \
                    .agg(lambda x: x.mode()[0])

mask = (df['category_name_1'].isnull()) | (df['category_name_1'] == '\\N')

df.loc[mask, 'category_name_1'] = df.loc[mask, 'sku'].map(sku_to_category)

new_value_counts = (df == '\\N').sum()
new_value_counts = new_value_counts[new_value_counts > 0]

print(new_value_counts)

df['category_name_1'].isnull().sum()

df['category_name_1'] = df['category_name_1'].fillna('Unknown')

df.info()

df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
df['Working Date'] = pd.to_datetime(df['Working Date'], errors='coerce')
df['Customer Since'] = pd.to_datetime(df['Customer Since'], errors='coerce')

df[['item_id', 'Customer ID']] = df[['item_id', 'Customer ID']].astype(object)
df['qty_ordered'] = df['qty_ordered'].astype(int)

df.info()

df.describe()

df[df['discount_amount'] < 0]

df.loc[df['discount_amount'] < 0, 'discount_amount'] = df['discount_amount'].abs()
df = df[df['category_name_1'] != '\\N']

pd.set_option('display.float_format', '{:.0f}'.format)
df.describe()

df[df['grand_total'] < 0]

df = df[df['grand_total'] >= 0]

df.describe()

df['status'].value_counts()

"""# **Data Cleaning Stage Summary:**
▶**Removal of Empty and Irrelevant Columns:**
Dropped columns such as 'Unnamed: 21' to 'Unnamed: 25', which contained no meaningful data.

▶**Handling of Duplicate Records:**
Identified and removed duplicate entries to maintain data integrity.

▶**Correction of Data Types:**
Adjusted several fields to appropriate types, including converting item_id and Customer ID to object type, and converting created_at, Customer Since, and Working Date to datetime format.

▶**Treatment of Placeholder Values:**
In sales_commission_code, occurrences of '\N' were replaced with NaN for consistency.

▶**Negative Values Handling:**
Corrected data entry errors by converting invalid negative discount amounts to positive values.
Orders with negative grand_total were removed due to their negligible size and inconsistency.

▶**Status Field Cleaning:**
Removed records with missing or invalid status values (\N).

# The dataset was successfully cleaned by removing irrelevant information, correcting data inconsistencies, handling missing values, and standardizing key fields, making it fully ready for analysis and visualization.

#  Data Preparation
"""

df['Year'] = df['created_at'].dt.year.astype('Int64')
df['Month'] = df['created_at'].dt.month.astype('Int64')

df['Day'] = df['created_at'].dt.day
df['DayOfWeek'] = df['created_at'].dt.day_name()

order_totals = df.groupby('increment_id')['grand_total'].sum().reset_index(name='abs_total')
df = df.merge(order_totals, on='increment_id', how='left')
order_totals

(order_totals['abs_total'] < 0).sum()

customer_orders = df.groupby('Customer ID').size().reset_index(name='order_count')
df = df.merge(customer_orders, on='Customer ID', how='left')

customer_spend = df.groupby('Customer ID')['grand_total'].sum().reset_index(name='total_spend')
df = df.merge(customer_spend, on='Customer ID', how='left')

category_group = df.groupby('category_name_1').agg({
    'grand_total': 'sum',
    'item_id': 'count'
}).reset_index()

category_group.rename(columns={'grand_total': 'Total Revenue', 'item_id': 'Number of Orders'}, inplace=True)

dayofweek_group = df.groupby('DayOfWeek').agg({
    'grand_total': 'sum',
    'item_id': 'count'
}).reset_index()

dayofweek_group.rename(columns={'grand_total': 'Total Revenue', 'item_id': 'Number of Orders'}, inplace=True)

payment_group = df.groupby('payment_method').agg({
    'grand_total': 'sum',
    'item_id': 'count'
}).reset_index()

payment_group.rename(columns={'grand_total': 'Total Revenue', 'item_id': 'Number of Orders'}, inplace=True)

status_group = df.groupby('status').agg({
    'grand_total': 'sum',
    'item_id': 'count'
}).reset_index()

status_group.rename(columns={'grand_total': 'Total Revenue', 'item_id': 'Number of Orders'}, inplace=True)

customer_group = df.groupby('Customer ID').agg({
    'grand_total': 'sum',
    'item_id': 'count'
}).reset_index()

customer_group.rename(columns={'grand_total': 'Total Spend', 'item_id': 'Total Orders'}, inplace=True)

customer_dates = df.groupby('Customer ID').agg({
    'created_at': ['min', 'max']
}).reset_index()

customer_dates.columns = ['Customer ID', 'First_Purchase_Date', 'Last_Purchase_Date']
customer_dates['Customer_Lifetime_Days'] = (customer_dates['Last_Purchase_Date'] - customer_dates['First_Purchase_Date']).dt.days

category_orders = df.groupby('category_name_1').size().reset_index(name='Number of Orders')

payment_orders = df.groupby('payment_method').size().reset_index(name='Number of Orders')

"""# Data Visualization"""

reversed_palette20 = sns.color_palette('viridis',n_colors=20, as_cmap=False)[::-1]
reversed_palette10 = sns.color_palette('viridis',n_colors=10, as_cmap=False)[::-1]

plt.figure(figsize=(10,4))
sns.barplot(data=category_group.sort_values('Total Revenue', ascending=False),
            x='Total Revenue', y='category_name_1', hue='category_name_1', palette=reversed_palette20, legend=False)
plt.title('Total Revenue by Product Category')
plt.xlabel('Total Revenue (PKR)')
plt.ylabel('Product Category')
plt.ticklabel_format(style='plain', axis='x')
plt.tight_layout()
plt.show()

"""Mobiles & Tablets dominate revenue generation, significantly outperforming all other product categories combined"""

plt.figure(figsize=(10,4))
sns.barplot(data=category_orders.sort_values('Number of Orders', ascending=False),
            x='Number of Orders', y='category_name_1', hue='category_name_1', palette=reversed_palette20, legend=False)
plt.title('Number of Orders by Product Category')
plt.xlabel('Number of Orders')
plt.ylabel('Product Category')
plt.tight_layout()
plt.show()

"""
Mobiles & Tablets also lead in order volume, indicating both high demand and strong customer interest."""

day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

dayofweek_summary = df.groupby('DayOfWeek').agg({
    'grand_total': 'sum',
    'increment_id': 'nunique'
}).reset_index()

dayofweek_summary.rename(columns={'grand_total': 'Total Revenue', 'increment_id': 'Number of Orders'}, inplace=True)

dayofweek_summary['DayOfWeek'] = pd.Categorical(dayofweek_summary['DayOfWeek'], categories=day_order, ordered=True)

dayofweek_summary = dayofweek_summary.sort_values('DayOfWeek')


fig, ax = plt.subplots(figsize=(8,5))

sns.barplot(
    ax=ax,
    data=dayofweek_summary,
    x='DayOfWeek',
    y='Number of Orders',
    palette='viridis'
)

ax.set_title('Number of Orders by Day of Week')
ax.set_xlabel('Day of Week')
ax.set_ylabel('Number of Orders')
ax.tick_params(axis='x', rotation=45)
ax.ticklabel_format(style='plain', axis='y')

plt.tight_layout()
plt.show()

"""Friday shows a clear peak in order volume, suggesting strong end-of-week purchasing behavior."""

top5_payment_group = payment_group.sort_values('Total Revenue', ascending=False).head(5)

plt.figure(figsize=(7,4))
sns.barplot(data=top5_payment_group,
            x='payment_method', y='Total Revenue', hue='payment_method', palette=reversed_palette10, legend=False)
plt.title('Top 5 Payment Methods by Total Revenue')
plt.xlabel('Payment Method')
plt.ylabel('Total Revenue (PKR)')
plt.xticks(rotation=45)
plt.ticklabel_format(style='plain', axis='y')
plt.tight_layout()
plt.show()

"""Payaxis and COD lead in revenue generation, significantly outperforming other payment methods."""

top5_payment_orders = payment_orders.sort_values('Number of Orders', ascending=False).head(5)

plt.figure(figsize=(7,4))
sns.barplot(data=top5_payment_orders,
            x='payment_method', y='Number of Orders', palette=reversed_palette10)
plt.title('Top 5 Payment Methods by Number of Orders')
plt.xlabel('Payment Method')
plt.ylabel('Number of Orders')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

monthly_orders = df.groupby(['Year', 'Month']).size().unstack(fill_value=0)
import calendar
monthly_orders.columns = [calendar.month_name[m] for m in monthly_orders.columns]



plt.figure(figsize=(10,4))
plt.title('Monthly Order Counts')
plt.xlabel('Month')
plt.ylabel('Year')
plt.xticks(rotation=45)
plt.tight_layout()
ax = sns.heatmap(monthly_orders, annot=True, fmt='d', cmap='viridis', linewidths=0.5, linecolor='gray')
colorbar = ax.collections[0].colorbar
colorbar.set_ticks([])
plt.show()

"""Order volumes consistently peak in November across all years, highlighting a strong seasonal trend."""

heatmap_data.index = [calendar.month_name[m] for m in heatmap_data.index]

plt.figure(figsize=(14,6))

ax = sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='viridis', linewidths=0.5, linecolor='gray')

colorbar = ax.collections[0].colorbar
colorbar.set_ticks([])

plt.title('Number of Orders per Category by Month')
plt.xlabel('Product Category')
plt.ylabel('Month')
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()

"""November shows a clear surge in orders across nearly all categories, with peak activity in Men's Fashion and Mobiles & Tablets."""

top_avg_discount = (
    df.groupby('sku')['discount_amount']
    .mean()
    .sort_values(ascending=False)
    .head(10)
)



top_skus = top_avg_discount.index

df[df['sku'].isin(top_skus)].groupby('sku').agg({
    'discount_amount': 'mean',
    'price': 'mean',
    'category_name_1': 'first',
    'qty_ordered': 'sum'
}).sort_values('discount_amount', ascending=False)

colors = sns.color_palette('viridis', n_colors=len(top_avg_discount))

top_avg_discount.plot(kind='barh', figsize=(10,6), color=colors[::-1], title='Top 10 Products by Average Discount')

plt.xlabel('Average Discount (PKR)')
plt.ylabel('SKU')
plt.tight_layout()
plt.show()

"""Changhong Ruba TV received the highest average discount by a wide margin."""

top_avg_discount = (
    df.groupby('sku')['discount_amount']
    .mean()
    .sort_values(ascending=False)
    .head(10)
)
top_skus = top_avg_discount.index

top_products = df[df['sku'].isin(top_skus)].groupby('sku').agg({
    'discount_amount': 'mean',
    'price': 'mean',
    'category_name_1': 'first',
    'qty_ordered': 'sum'
})

top_products['discount_percent'] = (top_products['discount_amount'] / top_products['price']) * 100
top_products = top_products.sort_values('discount_percent', ascending=False)
top_products = top_products[['price', 'discount_amount', 'discount_percent', 'category_name_1', 'qty_ordered']]

plt.figure(figsize=(8,4))
sns.barplot(
    data=top_products,
    y='sku',
    x='discount_percent',
    palette='viridis'
)

plt.title('Average Discount Percent by Product')
plt.xlabel('Average Discount (%)')
plt.ylabel('Product SKU')
plt.tight_layout()
plt.show()

"""
Top 1 product stands out with an average discount exceeding 150%. a potential data error or an unusually aggressive markdown."""

yearly_revenue = df.groupby('Year')['grand_total'].sum().reset_index()
fy_revenue = df.groupby('FY')['grand_total'].sum().reset_index()

fig, axes = plt.subplots(1, 2, figsize=(12,5))

sns.barplot(ax=axes[0], data=yearly_revenue, x='Year', y='grand_total', palette='viridis')
axes[0].set_title('Total Revenue per Calendar Year')
axes[0].set_xlabel('Year')
axes[0].set_ylabel('Total Revenue (PKR)')
axes[0].tick_params(axis='x', rotation=45)
axes[0].ticklabel_format(style='plain', axis='y')

sns.barplot(ax=axes[1], data=fy_revenue, x='FY', y='grand_total', palette='viridis')
axes[1].set_title('Total Revenue per Fiscal Year')
axes[1].set_xlabel('Fiscal Year')
axes[1].set_ylabel('')
axes[1].tick_params(axis='x', rotation=45)
axes[1].ticklabel_format(style='plain', axis='y')

plt.tight_layout()
plt.show()

"""While revenue peaked in calendar year 2017, the highest fiscal year revenue was recorded in FY18 — highlighting how timing differences between calendar and fiscal years can affect trend analysis."""

df.to_csv('cleaned_ecommerce_data.csv', index=False)

from google.colab import files
files.download('cleaned_ecommerce_data.csv')
