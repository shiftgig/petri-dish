# Petri Dish

## Introduction
Petri dish is an experimentation framework designed to be 


## Usage
 1. Instatiate connections (**subject_source** and **subject_sink**) using your credentials and the [connector wrappers](https://github.com/sgrepo/petri-dish/blob/master/petri_dish/connectors.py).
 2. Instantiate a [distributor](https://github.com/sgrepo/petri-dish/blob/master/petri_dish/distributors.py). Distributors define the treatment group assignment logic. More info here (add link).
 3. Define the experiment stages and filters.
 4. Instantiate a Dish, with those connections, a distributor, stages and
    filters.
 5. Set up a cron job that regularly runs the dish instance `run()`
    method.
 6. check the spreadsheet that updates with that regularity.

## Example
