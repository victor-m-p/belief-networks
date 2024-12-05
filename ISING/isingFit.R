##### run their pipeline #####
d <- read_csv("ISING/sim_data/nodes_5_obs_1000_normal.csv")
d <- as.matrix(d) # should not matter, I believe.
res <- IsingFit(
    d,
    family = "binomial", # only supported
    gamma = 0.25, # default (but maybe 0.5 is good)
    plot = FALSE
)
J <- res$weiadj
h <- res$threshold

# get J in lexicographical order (matching mpf)
J_upper <- c()
for (col in 1:(ncol(J) - 1)) {
    J_upper <- c(J_upper, J[col, (col + 1):ncol(J)])
}
combined <- c(J_upper, h)
output_string <- paste(combined, collapse = " ")
write(output_string, file = "ISING/sim_data/nodes_5_obs_1000_normal_IsingFit.dat")

###### just doing the second one here as well ######
d <- read_csv("ISING/sim_data/nodes_5_obs_1000_ising.csv")
d <- as.matrix(d) # should not matter, I believe.
res <- IsingFit(
    d,
    family = "binomial", # only supported
    gamma = 0.25, # default (but maybe 0.5 is good)
    plot = FALSE
)
J <- res$weiadj
h <- res$threshold

# get J in lexicographical order (matching mpf)
J_upper <- c()
for (col in 1:(ncol(J) - 1)) {
    J_upper <- c(J_upper, J[col, (col + 1):ncol(J)])
}
combined <- c(J_upper, h)
output_string <- paste(combined, collapse = " ")

write(output_string, file = "ISING/sim_data/nodes_5_obs_1000_ising_IsingFit.dat")
