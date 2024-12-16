import numpy as np
import itertools 
import matplotlib.pyplot as plt 
import os 
import pandas as pd 

def node_edge_lst(J, h, labels=None): 
    if not labels: 
        labels = [node+1 for node in range(len(h))]
    comb = list(itertools.combinations(labels, 2))
    df_edgelist = pd.DataFrame(comb, columns = ['n1', 'n2'])
    df_edgelist['weight'] = J
    df_nodes = pd.DataFrame(labels, columns = ['n'])
    df_nodes['size'] = h
    df_nodes = df_nodes.set_index('n')
    dict_nodes = df_nodes.to_dict('index')
    return df_edgelist, dict_nodes


def generate_valid_states(group_sizes, coding_no=0):
    # Generate all valid rows for each group
    group_states = []
    for size in group_sizes:
        # Create all combinations where exactly one element is 1
        group = []
        for i in range(size):
            state = np.full(size, coding_no)
            state[i] = 1
            group.append(state)
        group_states.append(group)

    # Generate all possible combinations using the Cartesian product
    all_combinations = itertools.product(*group_states)

    # Combine the groups for each combination
    allowed_rows = []
    for combination in all_combinations:
        allowed_rows.append(np.concatenate(combination))

    # Convert to NumPy array
    return np.array(allowed_rows)

def plot_probabilities(p_true, p_est, alpha=1, ymax = 1, save=False):
    plt.figure(figsize=(5, 4))
    plt.grid(True, zorder=1)
    plt.scatter(p_true, p_est, color='tab:blue', alpha=alpha, label='Probabilities', zorder=2)
    plt.plot([0, ymax], [0, ymax], color='black', linestyle='--', label='', zorder=3)
    plt.xlabel('True Probabilities')
    plt.ylabel('Inferred Probabilities')
    plt.title('True vs. Inferred Probabilities')
    
    if save: 
        plt.savefig(save, dpi=300)
        plt.close()
    
    else: 
        plt.show()

def plot_params(h_true, J_true, h_est, J_est, alpha=1, save=False): 
    plt.figure(figsize=(5, 4))
    plt.grid(True, zorder=1)
    plt.scatter(h_true, h_est, color='tab:orange', alpha=alpha, label='Local Fields', zorder=2)
    plt.scatter(J_true, J_est, color='tab:blue', alpha=alpha, label='Pairwise Couplings', zorder=2)
    plt.plot([min(min(h_true), min(J_true)), max(max(h_true), max(J_true))],
            [min(min(h_true), min(J_true)), max(max(h_true), max(J_true))],
            color='black', linestyle='--', label='', zorder=3)
    plt.title('True vs. Inferred Parameters')
    plt.xlabel('True Parameters')
    plt.ylabel('Inferred Parameters')
    plt.legend()
    plt.tight_layout()

    if save: 
        plt.savefig(save, dpi=300)
        plt.close()
    else: 
        plt.show();

def write_to_mpf(df, output_folder, output_filename, weights=1.0): 
    columns = df.columns.tolist()
    n_obs = df.shape[0]
    n_nodes = len(columns)
    df['weight'] = weights
    formatted_rows = df.apply(
        lambda row: f"{''.join(map(str, row[columns].astype(int).tolist()))} {row['weight']:.2f}",
        axis=1
    )
    # save 
    output = f"{n_obs}\n{n_nodes}\n" + '\n'.join(formatted_rows)
    with open(os.path.join(output_folder, output_filename), 'w') as f: 
        f.write(output)
        
def load_mpf_params(n_nodes, path): 
    with open(path, 'r') as f:
        mpf_data = f.readline().strip()
    
    n_couplings = n_nodes * (n_nodes - 1) // 2
    mpf_params = np.array(mpf_data.split(), dtype=float)
    mpf_couplings = mpf_params[:n_couplings]
    mpf_fields = mpf_params[n_couplings:]
    return mpf_fields, mpf_couplings

# taken from coniii enumerate
def fast_logsumexp(X, coeffs=None):
    """correlation calculation in Ising equation

    Args:
        X (np.Array): terms inside logs
        coeffs (np.Array, optional): factors in front of exponential. Defaults to None.

    Returns:
        float: sum of exponentials
    """
    Xmx = max(X)
    if coeffs is None:
        y = np.exp(X-Xmx).sum()
    else:
        y = np.exp(X-Xmx).dot(coeffs)

    if y<0:
        return np.log(np.abs(y))+Xmx, -1.
    return np.log(y)+Xmx, 1.

# still create J_combinations is slow for large number of nodes
def p_dist(h, J):
    """return probabilities for 2**h states

    Args:
        h (np.Array): local fields
        J (np.Array): pairwise couplings. 

    Returns:
        np.Array: probabilities for all configurations
    """
    n_nodes = len(h)
    hJ = np.concatenate((h, J))
    h_combinations = np.array(list(itertools.product([1, -1], repeat = n_nodes)))
    J_combinations = np.array([list(itertools.combinations(i, 2)) for i in h_combinations])
    J_combinations = np.add.reduce(J_combinations, 2)
    J_combinations[J_combinations != 0] = 1
    J_combinations[J_combinations == 0] = -1
    condition_arr = np.concatenate((h_combinations, J_combinations), axis = 1)
    flipped_arr = hJ * condition_arr
    summed_arr = np.sum(flipped_arr, axis = 1)
    logsumexp_arr = fast_logsumexp(summed_arr)[0]
    Pout = np.exp(summed_arr - logsumexp_arr)
    return Pout[::-1]

def bin_states(n, sym=True):
    """generate 2**n possible configurations

    Args:
        n (int): number of questions (features)
        sym (bool, optional): symmetric system. Defaults to True.

    Returns:
        np.Array: 2**n configurations 
    """
    v = np.array([list(np.binary_repr(i, width=n)) for i in range(2**n)]).astype(int)
    if sym is False:
        return v
    return v*2-1