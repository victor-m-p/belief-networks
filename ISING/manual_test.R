library(pacman)
pacman::p_load(IsingFit, IsingSampler, tidyverse)

# Input list of pairwise couplings
n <- 3
fields <- c(-0.8, 0, -0.8)
pairwise_couplings <- c(0, 1.6, 0)

# Number of elements (infer from the length of the pairwise couplings)
n <- 3 # for example, J_12, J_13, J_23 corresponds to a 3x3 matrix

# Create an empty symmetric matrix with zero diagonal
mat <- matrix(0, nrow = n, ncol = n)

# Fill the upper triangle of the matrix
upper_indices <- upper.tri(mat)
mat[upper_indices] <- pairwise_couplings

# Mirror the upper triangle to the lower triangle
mat <- mat + t(mat)

# generate binary strings (lexicographical)
binary_strings <- expand.grid(rep(list(c(0, 1)), n))
binary_strings <- binary_strings[, n:1]
binary_matrix <- as.matrix(binary_strings)

res <- list()
for (i in 1:nrow(binary_matrix)) {
    binary_string <- binary_matrix[i, ]
    p <- IsingStateProb(
        binary_string,
        mat,
        fields,
        beta = 1
    )
    res[[i]] <- p
}

fields # wait; it just ignores the external fields wtf?
IsingStateProb(
    c(0, 1, 0),
    mat,
    fields,
    beta = 1 # should match us
)

# 000: 0.1725
# 001: 0.0775
# 010: 0.1725
# 011: 0.0775
# 100: 0.0775
# 101: 0.1725
# 110: 0.0775
# 111: 0.1725

# what the fuck.
IsingLikelihood(
    mat,
    fields,
    beta = 1
)
IsingLikelihood(
    mat,
    fields,
    beta = 1
)


#### h function in c++ #####
# double H(NumericMatrix J, IntegerVector s, NumericVector h)
# {
#  double Res = 0;
#  int N = J.nrow();
#  for (int i=0; i<N; i++)
#  {
#    Res -= h[i] * s[i];
#    for (int j=i; j<N; j++)
#    {
#      if (j != i) Res -= J(i,j) * s[i] * s[j];
#    }
#  }
#  return(Res);
# }

# reverse engineer this #
IsingLikelihoodX <- function(graph, thresholds, beta, responses = c(0L, 1L), potential = FALSE) {
    stopifnot(isSymmetric(graph))
    stopifnot(length(responses) == 2)
    if (any(diag(graph) != 0)) {
        diag(graph) <- 0
        warning("Diagonal set to 0")
    }
    N <- nrow(graph)
    Allstates <- do.call(expand.grid, lapply(1:N, function(x) c(responses[1], responses[2])))
    P <- exp(-beta * apply(Allstates, 1, function(s) H(graph, s, thresholds)))
    if (potential) {
        df <- cbind(Potential = P, Allstates)
    } else {
        df <- cbind(Probability = P / sum(P), Allstates)
    }

    return(df)
}
df <- IsingLikelihoodX(graph, fields, beta = 1, responses = c(-1, 1)) ### EEEEHAT
df # WTF WTF WTF this makes it work of course.


N <- 3
Allstates <- do.call(expand.grid, lapply(1:N, function(x) c(0L, 1L)))
Allstates

H <- function(J, s, h) {
    Res <- 0
    N <- nrow(J)
    for (i in 1:N) {
        Res <- Res - h[i] * s[i]
        for (j in i:N) {
            if (j != i) {
                Res <- Res - J[i, j] * s[i] * s[j]
            }
        }
    }
    return(Res)
}

binary_matrix
binary_matrix
hamiltonians <- list()
for (i in 1:nrow(binary_matrix)) {
    binary_string <- binary_matrix[i, ]
    h <- H(mat, binary_string, fields)
    hamiltonians[[i]] <- h
}
hamiltonians

h1 <- H(mat, c(-1, 1, -1), fields)
h1
