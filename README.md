[![Build Status](https://travis-ci.org/sgrepo/petri-dish.svg?branch=master)](https://travis-ci.org/sgrepo/petri-dish)

# Petri Dish

## Introduction
Petri dish is designed to build an experiment timeline with stages and treatment groups, and track the evolution of the experimentation subjects throughout the experiment. 


## Getting Started

In practice, Petri dish allows you to get experimentation subjects data from postgres, apply filters and assign treatment groups to each one and then track their progress through the experimentation stages through a google sheets spreadsheet. Here is how you set it up:

 1. Instatiate connections (**subject_source** and **subject_sink**) using your credentials and the [connector wrappers](https://github.com/sgrepo/petri-dish/blob/master/petri_dish/connectors.py).
 2. Instantiate a [distributor](https://github.com/sgrepo/petri-dish/blob/master/petri_dish/distributors.py). Distributors define the treatment group assignment logic. More info below.
 3. Define the experiment stages and filters.
 4. Instantiate a Dish, with those connections, a distributor, stages and
    filters.
 5. Set up a cron job that regularly runs the dish instance `run()`
    method.
 6. check the spreadsheet that updates with that regularity.

## Example
[ add in gifs and screenshots of the process of creating an experiment]

## Next improvements

##### - built in daemon capabilities to replace dependency from cron job setup 
##### - support for automated actions (e.g: emails) to subjects based on stage and possibly metrics or others
##### - increased coverage
##### - support for surveys
 
## More Info

### Treatment group assignment
A good distribution of experimentation subjects  (in terms of characteristics or properties) across the treatment groups is essential for any type of experiment. 

Whenever we expect a large amount of subjects per treatment group, this isn't a particular event and **[random assignment](https://github.com/sgrepo/petri-dish/blob/8678f259ed48c240d3e1dbf7f800c8181f9bdbb6/petri_dish/distributors.py#L32)** should be enough to expect the law of large numbers to do the job. 

However, if the expected amount of subjects per group is low, there are ways we can **[direct the assignments](https://github.com/sgrepo/petri-dish/blob/8678f259ed48c240d3e1dbf7f800c8181f9bdbb6/petri_dish/distributors.py#L45)** of subjects to groups in order to maximize the diversity across treatment groups.

We've added tools to handle that as part of this framework. Links above ^.
