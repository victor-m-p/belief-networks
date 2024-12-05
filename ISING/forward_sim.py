# generate basic mpf data 
from fun import *
import os 
import json

# write to mpf
def write_to_mpf(df, output_folder, output_filename, weights=1.0): 
    columns = [f"Q{i+1}" for i in range(df.shape[1])]
    df['weight'] = weights
    formatted_rows = df.apply(
        lambda row: f"{''.join(map(str, row[columns].astype(int).tolist()))} {row['weight']:.2f}",
        axis=1
    )
    # save 
    output = f"{n_obs}\n{n_nodes}\n" + '\n'.join(formatted_rows)
    with open(os.path.join(output_folder, output_filename), 'w') as f: 
        f.write(output)
        
def normal_params(n_nodes, sd=0.5): 
    n_couplings = n_nodes * (n_nodes - 1) // 2
    fields = np.random.normal(0, sd, n_nodes)
    couplings = np.random.normal(0, sd, n_couplings)
    return fields, couplings

# closer to IsingFit 
def ising_params(n_nodes, p_missing=0.5): 
    # first generate couplings (here uniform)
    n_couplings = n_nodes * (n_nodes - 1) // 2
    couplings = np.random.uniform(0.5, 2, n_couplings)
    
    # set some couplings to 0
    mask = np.random.rand(len(couplings)) < p_missing
    couplings[mask] = 0
    
    # now local fields by column (or similarly row) sums
    pairs = list(itertools.combinations(range(1, n_nodes + 1), 2))
    node_sums = {n: 0 for n in range(1, n_nodes + 1)}
    for coupling, (i, j) in zip(couplings, pairs):
        node_sums[i] += coupling
        node_sums[j] += coupling
    fields = np.array([node_sums[node] for node in sorted(node_sums)])
    
    # needs to be negative row sums divided by 2 
    fields = -fields / 2
    return fields, couplings

# setup  
output_folder = 'sim_data'
n_nodes = 5
n_couplings = n_nodes * (n_nodes - 1) // 2 
n_obs = 1000
states = bin_states(n_nodes)

# generate params
normal_h, normal_J = normal_params(n_nodes)
ising_h, ising_J = ising_params(n_nodes)

# generate data 
normal_p = p_dist(normal_h, normal_J)
ising_p = p_dist(ising_h, ising_J)

def generate_obs(states, n_observations, p): 
    observations = np.random.choice(len(p), size=n_observations, p=p)
    mapping = states[observations]
    columns = [f"Q{i+1}" for i in range(states.shape[1])]
    df = pd.DataFrame(mapping, columns=columns)
    df = df.replace(-1, 0)
    return df

normal_obs = generate_obs(states, n_obs, normal_p)
ising_obs = generate_obs(states, n_obs, ising_p)

# save data 
overall_path = f'nodes_{n_nodes}_obs_{n_obs}'
normal_obs.to_csv(os.path.join(output_folder, f'{overall_path}_normal.csv'), index=False)
ising_obs.to_csv(os.path.join(output_folder, f'{overall_path}_ising.csv'), index=False)

# write data to mpf
write_to_mpf(
    normal_obs,
    output_folder,
    output_filename = f'nodes_{n_nodes}_obs_{n_obs}_normal.txt',
)

write_to_mpf(
    ising_obs,
    output_folder,
    output_filename = f'nodes_{n_nodes}_obs_{n_obs}_ising.txt',
)

# save parameters & true p
data = {
    'probabilities': normal_p.tolist(),
    'local_fields': normal_h.tolist(),
    'pairwise_couplings': normal_J.tolist()
}
save_path = os.path.join(output_folder, f'{overall_path}_normal.json')
with open(save_path, 'w') as f: 
    json.dump(data, f)
    
data = {
    'probabilities': ising_p.tolist(),
    'local_fields': ising_h.tolist(),
    'pairwise_couplings': ising_J.tolist()
}
save_path = os.path.join(output_folder, f'{overall_path}_ising.json')
with open(save_path, 'w') as f: 
    json.dump(data, f)
