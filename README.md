# Execution Steps

1. Setup the environment: SQLite Database and non time-dependent tables.

`python \code\setup_env.py`

2. Write the daily staging tables

`python \code\main.py 2025-09-04`

3. Run the Activation logic in the [Activation Plan Notebook](activation_plan.ipynb), with the relevant datestamp recorded in the `date` variable.