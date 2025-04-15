import pandas as pd

# Print first 3 rows
df = pd.read_csv("students.csv")
print(df[:3]) # can also do df.head(3)?
# What are the data types of each colum?
for c in df.columns:
    print(f'Type of {c} is {type(c)}')
# How many rows are there
print(f'Rows: {len(df)}')

# Filter and Query
# Show students w/Gpa > 3.5
# df['gpa']>3.5 - compares each row's gpa to 3.5 , returns Series of booleans
# basically, give me the rows of df where inside condition is true
print(df[df['gpa']>3.5])
# Show students in "Math" major with GPA >= 3.5
print(df[df['gpa']>3.5 & df['major'] == 'Math']) # it's & not and, bc and is for boolean values, & is bitwise for the lists 

# Grouping and Aggregation
# Avg GPA by major
print(df.groupby('major')['gpa'].mean())
# Count of each student in major
print(df['major'].value_counts())

# Add a column "honors", True if GPA >=3.7
df['honors'] = df['gpa']>=3.7

# Merge another data frame
# Merge club info into student DataFrame using Name
df2 = pd.read_csv('clubs.csv')
merged = pd.merge(df, df2, on='name', how='left') # LEFTJOIN, like SQL

# Clean missing data - fill missing club values w/none
merged['club'] = merged['club'].fillna("None")
