library(pacman)
pacman::p_load(IsingFit, IsingSampler, tidyverse)

# https://rdrr.io/cran/IsingFit/man/isingfit.html
N <- 6 # n nodes
nSample <- 1000 # n obs

# first they randomly generate 0 or 1 for each edge.
# they set 80% of edges to 0 and 20% to 1.
# then they generate random weights between 0.5-2 for each edge
graph <- matrix(sample(0:1, N^2, TRUE, prob = c(0.8, 0.2)), N, N) * runif(N^2, 0.5, 2) # Jij

# element-wise maximum of original and transpose
# basically you could have J_{13}=0.5 and J_{31}=0 and that would then be set to 0.5
# which really means that 80% is not actually set to 0
# I have not worked out the formula, but it will be lower
graph <- pmax(graph, t(graph)) # Jij
diag(graph) <- 0 # Jij

# so here the threshold is determined by the sum of the weights of the edges
# this is really weird to me; why do they do that?
# I mean; why would the external field be negative rowsums?
threshold <- -rowSums(graph) / 2 # hi

# this is what we need to test, basicaly
# difficult because we are not getting any probability file here.
data <- IsingSampler(
    nSample,
    graph,
    threshold,
    beta = 1, # default
)

# generate result as well
res <- IsingFit(data, family = "binomial", plot = FALSE)

# just check whether probabilities work as expected
N <- 3
graph <- matrix(sample(0:1, N^2, TRUE, prob = c(0.8, 0.2)), N, N) * runif(N^2, 0.5, 2) # Jij
graph <- pmax(graph, t(graph))
graph
diag(graph) <- 0
threshold <- -rowSums(graph) / 2
IsingStateProb(
    c(0, 1, 1),
    graph,
    threshold,
    beta = 1
) # 0.078
IsingStateProb(
    c(1, 1, 1),
    graph,
    threshold,
    beta = 1
) # 0.17
threshold
graph
# save data for .mpf
threshold
graph

data <- IsingSampler(
    10,
    graph,
    threshold,
    beta = 1
)
data

# so doing pretty good here ...
# is there some weird scaling?
threshold
res$threshold
graph
res$weiadj

# save inferred params to csv
d <- read_csv("ISING/sim_data/nodes_5_obs_500.csv")
d <- as.matrix(d) # should not matter, I believe.
res <- IsingFit(
    d,
    family = "binomial", # only supported
    gamma = 0.25, # default (but maybe 0.5 is good)
    plot = FALSE
)
J <- res$weiadj
h <- res$threshold
J


# get J in lexicographical order (matching mpf)
J_upper <- c()
for (col in 1:(ncol(J) - 1)) {
    J_upper <- c(J_upper, J[col, (col + 1):ncol(J)])
}
combined <- c(J_upper, h)
combined
output_string <- paste(combined, collapse = " ")

write(output_string, file = "ISING/sim_data/nodes_5_obs_500_IsingFit.dat")
