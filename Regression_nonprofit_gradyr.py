# Regression Code

# Convert Medical_school to categorical IDs
df["med_sch_id"] = df["School"].astype("category").cat.codes

# Convert grad_year to a categorical variable and create dummies
df['GRD_YR'] = pd.to_numeric(df['GRD_YR'])
grad_year_dummies = pd.get_dummies(df['GRD_YR'], drop_first=False, dtype=int)
df = df.join(grad_year_dummies)

# Drop the '2004' dummy from predictors to make it the reference category
grad_year_dummies = grad_year_dummies.drop(columns=[2004])
df = df.drop(columns=[2004])


# Set up model
import regpyhdfe
from regpyhdfe import Regpyhdfe

# List of predictor columns with 2004 as reference
predictors = ["year" for year in range(2000, 2004)] + ["year" for year in range(2005, 2013)]

model = Regpyhdfe(df=df, # put the name of your dataframe here
                  target="nonprofit", # outcome variable
                  predictors=predictors, # exposure variable
                  absorb_ids=['med_sch_id'],  # Fixed effects
                  cluster_ids=['med_sch_id']) # Cluster std errors

# Fit the model - WILL NEED TO TYPE C in the box that pops up when you run this line
result = model.fit()

# Print results
print(result.summary())


# Plotting code
import matplotlib.pyplot as plt
import seaborn as sns

# Extract coefficients and standard errors
years = [str(year) for year in range(2000, 2014)]
coefficients = [result.params.get("year", None) for year in years]
std_errors = [result.bse.get("year", None) for year in years]

# Create DataFrame for easy plotting
event_study_df = pd.DataFrame({
    'Year': years,
    'Coefficient': coefficients,
    'Std_Error': std_errors
})

# Create a plot
plt.figure(figsize=(8, 6))

# Plot the coefficients
plt.scatter(event_study_df['Year'], event_study_df['Coefficient'], color='blue', label='Coefficients')

# Plot the standard errors as error bars
plt.errorbar(event_study_df['Year'], event_study_df['Coefficient'], yerr=event_study_df['Std_Error'], fmt='o', color='blue', capsize=5)

# Add a vertical line at 2004
plt.axvline(x='2004', color='r', linestyle='--')

plt.axhline(y=0, color='black', linewidth=1)

# Add a dot for 2004 at 0 to mark the reference category
plt.scatter('2004', 0, color='blue', zorder=5)

# Adding labels and title
plt.xlabel('Medical School Graduation Year')
plt.ylabel('Coefficient')
plt.title('Outcome: Working in a Nonprofit)

# Show plot
plt.xticks(rotation=45)
plt.grid(True)
plt.show()

