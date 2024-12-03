library(pacman)
pacman::p_load(tidyverse, qgraph, psych)

# https://reisrgabriel.com/blog/2021-08-10-psych-network/
load_libraries()
df <- bfi[, 1:25]
traits <- rep(c(
    'Agreeableness', 
    'Conscientiousness', 
    'Extraversion', 
    'Neuroticism', 
    'Openness'), 
    each=5)

# simple correlations 
network <- qgraph(
    cor_auto(df),
    graph='cor',
    layout='spring',
    theme='colorblind',
    groups=traits
    )

# estimate partial correlations
network <- qgraph(
    cor_auto(df),
    layout='spring',
    graph='pcor',
    theme='colorblind',
    groups=traits
)

# EBICglasso
# okay so maybe not sparse enough; which arguments can I provide then? 
network <- qgraph(
    cor_auto(df),
    layout='spring',
    graph='glasso',
    sampleSize=nrow(df),
    theme='colorblind',
    groups=traits)

# okay so I have couplings now? 
# but what about local fields? 

## try the ggmFit thing ##
CovMat <- cov(bfi[, 1:25], use="pairwise.complete.obs")
EBICgraph <- qgraph(
    CovMat, 
    graph="glasso",
    sampleSize=nrow(bfi),
    tuning=0.5,
    layout="spring",
    title="BIC",
    details=TRUE)
fitNet <- ggmFit(EBICgraph, CovMat, nrow(bfi))
fitNet$fitMeasures


anes_data <- read_csv('ANES/data/anes_data.csv')
anes_baseline <- anes_data |> 
    filter(year == 2016)

# the coding here is actually terrible # 
