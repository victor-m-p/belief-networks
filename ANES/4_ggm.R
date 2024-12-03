library(pacman)
pacman::p_load(tidyverse, qgraph, psych)

# https://reisrgabriel.com/blog/2021-08-10-psych-network/
load_libraries()
df <- bfi[, 1:25]

# load our data
anes_data <- read_csv('ANES/data/anes_data.csv')
anes_baseline <- anes_data |> 
    filter(year == 2016) |>
    select(ID, question, value)

# split data out
df_wide <- anes_baseline |> 
    pivot_wider(
        names_from = question,
        values_from = value
    )

# now drop ID 
df_wide <- df_wide |> 
    select(-ID)

# check simple correlations
# okay, sort-of makes sense. 
network <- qgraph(
    cor_auto(df_wide),
    graph='cor',
    layout='spring',
    theme='colorblind'
    )

# partial correlations
# also makes sense; strongly abortion and gay. 
network <- qgraph(
    cor_auto(df_wide),
    layout='spring',
    graph='pcor',
    theme='colorblind'
    )

# I must be doing something wrong here.  
network <- qgraph(
    cor_auto(df_wide),
    layout='spring',
    graph='glasso',
    sampleSize=nrow(df),
    gamma=0.5,
    theme='colorblind')