import pandas as pd
import numpy as np
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import pytensor.tensor as pt

# 1) DATA PREP FOR MULTI-TASK --------------------------------
def prepare_data_multi(df, task_ids, handle_nan='ignore'):

    df2 = df[df['task_id'].isin(task_ids)][['task_id','Publication date','score']].copy()
    if handle_nan == 'zero':
        df2['score'] = df2['score'].fillna(0)
    else:
        df2 = df2.dropna(subset=['score'])
    df2['Publication date'] = pd.to_datetime(df2['Publication date'])
    df2 = df2.sort_values('Publication date')

    # unified time axis (days since first date)
    unique_dates = sorted(df2['Publication date'].unique())
    first = unique_dates[0]
    time_points = np.array([(d-first).days for d in unique_dates])
    date_to_idx = {d:i for i,d in enumerate(unique_dates)}

    # map each obs to time-index and task-index
    time_idx = df2['Publication date'].map(date_to_idx).values
    task_to_idx = {tid:i for i,tid in enumerate(task_ids)}
    task_idx = df2['task_id'].map(task_to_idx).values

    y_obs = df2['score'].values / 100.0
    return time_points, y_obs, time_idx, task_idx, unique_dates

# 2) MODEL FIT FOR MULTI-TASK --------------------------------
def fit_capability_model_multi(time_points, y_obs, time_idx, task_idx,
                               n_samples=2000, n_tune=1000, random_seed=42):
    T = len(time_points)
    K = len(np.unique(task_idx))

    with pm.Model() as model:
        # Priors
        c0 = pm.Normal('c0', mu=-2.0, sigma=1.0)
        mu = pm.Normal('mu', mu=0.02, sigma=0.01)
        sigma_omega = pm.HalfCauchy('sigma_omega', beta=0.1)
        g = pm.HalfNormal('g', sigma=1.0, shape=K)
        sigma_nu = pm.HalfCauchy('sigma_nu', beta=0.1, shape=K)

        # Latent random walk
        caps = [c0]
        for t in range(1, T):
            dt = time_points[t] - time_points[t-1]
            drift = mu * dt
            eps = pm.Normal(f'eps_{t}', mu=0, sigma=sigma_omega * np.sqrt(dt))
            caps.append(caps[-1] + drift + eps)
        c_stack = pm.Deterministic('c', pt.stack(caps))

        # Fitted mean for each observation
        score_mean = pm.Deterministic(
            'score_mean',
            pm.math.invlogit(g[task_idx] * c_stack[time_idx])
        )

        # Observation
        pm.Normal('y', mu=score_mean, sigma=sigma_nu[task_idx], observed=y_obs)

        trace = pm.sample(
            n_samples, tune=n_tune,
            chains=4, cores=1,
            random_seed=random_seed,
            return_inferencedata=True
        )
    return trace
def simulate_forecast_from_posterior(trace, time_points, H=100, random_seed=42):
    """
    Draw H‐step‐ahead forecasts from your fitted posterior.
    Returns:
      future_times,
      (c_mean, c_lo, c_hi),
      (y_mean, y_lo, y_hi)
    """
    # 1) Flatten chain+draw → sample
    post = trace.posterior.stack(sample=("chain","draw"))
    
    # 2) Extract & transpose so that axis 0 == samples
    c_arr = post["c"].values            # originally (T, S)
    c_samples = c_arr.T                 # now (S, T)
    
    mu_samples    = post["mu"].values   # (S,)
    sigma_samples = post["sigma_omega"].values  # (S,)
    
    g_arr = post["g"].values            # originally (K, S)
    g_samples = g_arr.T                 # now (S, K)
    
    # 3) Quick sanity print
    print("shapes:", 
          "c",       c_samples.shape,
          "mu",      mu_samples.shape,
          "sigma",   sigma_samples.shape,
          "g",       g_samples.shape)
    
    S, T = c_samples.shape
    K    = g_samples.shape[1]
    
    np.random.seed(random_seed)
    c_fore = np.zeros((S, H))
    y_fore = np.zeros((S, H, K))
    c_last = c_samples[:, -1]
    
    for s in range(S):
        c = c_last[s]
        μ = mu_samples[s]
        σ = sigma_samples[s]
        g = g_samples[s]   # shape (K,)
        
        for h in range(H):
            c = c + μ + np.random.normal(0, σ)
            c_fore[s, h]    = c
            y_fore[s, h, :] = 1/(1 + np.exp(-g*c))
    
    # 4) Summarize to mean + 95% CI
    def summarize(arr):
        return (arr.mean(axis=0),
                np.percentile(arr, 2.5, axis=0),
                np.percentile(arr,97.5, axis=0))
    
    c_mean, c_lo, c_hi = summarize(c_fore)
    y_mean, y_lo, y_hi = summarize(y_fore)
    
    # 5) Build future_times axis
    last_t = time_points[-1]
    future_times = np.arange(last_t+1, last_t+1+H)
    
    return future_times, (c_mean, c_lo, c_hi), (y_mean, y_lo, y_hi)

# 4) PLOTTING UTILITIES --------------------------------------
def plot_raw_data_multi(time_points, y_obs, time_idx, task_idx, task_ids, dates):
    plt.figure(figsize=(10,6))
    markers = ['o','s','^','d','x']
    for i,tid in enumerate(task_ids):
        idx = np.where(task_idx==i)[0]
        plt.scatter(time_points[time_idx[idx]], y_obs[idx],
                    marker=markers[i], s=60, label=f'Task {tid}')
    plt.xticks(time_points, [d.strftime('%Y-%m') for d in dates],
               rotation=45, ha='right')
    plt.title('Raw Test Scores'); plt.xlabel('Date'); plt.ylabel('Score')
    plt.grid(alpha=0.3); plt.legend(); plt.tight_layout(); plt.show()

def plot_in_sample_fit(trace, time_points, y_obs, time_idx, task_idx, task_ids, dates):
    # latent
    c_da   = trace.posterior['c']
    c_mean = c_da.mean(dim=('chain','draw')).values
    c_lo   = c_da.quantile(0.025, dim=('chain','draw')).values
    c_hi   = c_da.quantile(0.975, dim=('chain','draw')).values
    # fitted scores
    sm     = trace.posterior['score_mean']
    y_mean = sm.mean(dim=('chain','draw')).values
    y_lo   = sm.quantile(0.025, dim=('chain','draw')).values
    y_hi   = sm.quantile(0.975, dim=('chain','draw')).values

    fig, (ax1,ax2) = plt.subplots(1,2,figsize=(14,5))
    ax1.plot(time_points, c_mean, 'b-'); ax1.fill_between(time_points, c_lo, c_hi, color='b', alpha=0.2)
    ax1.set_title('Estimated Capability'); ax1.set_xticks(time_points)
    ax1.set_xticklabels([d.strftime('%Y-%m') for d in dates], rotation=45, ha='right')
    ax1.grid(alpha=0.3)

    markers = ['o','s','^','d','x']
    for i,tid in enumerate(task_ids):
        idx = np.where(task_idx==i)[0]
        t_obs = time_points[time_idx[idx]]
        ax2.scatter(t_obs, y_obs[idx], marker=markers[i], s=60, label=f'Obs {tid}')
        ax2.plot(t_obs, y_mean[idx], 'b-')
        ax2.fill_between(t_obs, y_lo[idx], y_hi[idx], color='b', alpha=0.2)

    ax2.set_title('In-Sample Fit'); ax2.set_xticks(time_points)
    ax2.set_xticklabels([d.strftime('%Y-%m') for d in dates], rotation=45, ha='right')
    ax2.grid(alpha=0.3); ax2.legend(); plt.tight_layout(); plt.show()


def plot_forecast_simulated(trace, time_points, y_obs, time_idx, task_idx,
                            task_ids, dates, future_times, c_stats, y_stats):

    c_mean, c_lo, c_hi = c_stats
    y_mean_f, y_lo_f, y_hi_f = y_stats

    # 1) Extract in‐sample fit for scores
    sm   = trace.posterior['score_mean']
    y_mean_h = sm.mean(dim=('chain','draw')).values       # (N_obs,)
    y_lo_h   = sm.quantile(0.025, dim=('chain','draw')).values
    y_hi_h   = sm.quantile(0.975, dim=('chain','draw')).values

    # 2) Extract historical latent for left panel
    c_da   = trace.posterior['c']
    ch_mean = c_da.mean(dim=('chain','draw')).values
    ch_lo   = c_da.quantile(0.025, dim=('chain','draw')).values
    ch_hi   = c_da.quantile(0.975, dim=('chain','draw')).values

    fig, (ax1, ax2) = plt.subplots(1,2, figsize=(14,5))

    # ---- Left: capability history + forecast ----
    ax1.plot(time_points,   ch_mean, 'b-')
    ax1.fill_between(time_points,   ch_lo,   ch_hi,   color='b', alpha=0.2)
    ax1.plot(future_times,  c_mean, 'g-')
    ax1.fill_between(future_times,  c_lo,  c_hi,  color='g', alpha=0.2)
    ax1.axvline(time_points[-1], color='r', ls='--', label='Forecast start')
    ax1.set_title('Capability Forecast', fontsize=14)
    ax1.grid(alpha=0.3); ax1.legend()

    # ---- Right: score history + fit + forecast ----
    markers = ['o','s','^','d','x']
    for i, tid in enumerate(task_ids):
        idx = np.where(task_idx==i)[0]
        t_obs = time_points[time_idx[idx]]

        # a) observations
        ax2.scatter(t_obs, y_obs[idx],
                    marker=markers[i], s=60,
                    label=f'Obs {tid}')

        # b) in‐sample fit line + CI
        ax2.plot(t_obs, y_mean_h[idx], 'b-')
        ax2.fill_between(t_obs,
                         y_lo_h[idx],
                         y_hi_h[idx],
                         color='b', alpha=0.2)

        # c) forecast line + CI
        ax2.plot(future_times, y_mean_f[:,i], 'g-')
        ax2.fill_between(future_times,
                         y_lo_f[:,i],
                         y_hi_f[:,i],
                         color='g', alpha=0.2)

    ax2.axvline(time_points[-1], color='r', ls='--')
    ax2.set_title('Score Forecast', fontsize=14)
    ax2.set_xticks(time_points)
    ax2.set_xticklabels([d.strftime('%Y-%m') for d in dates], rotation=45, ha='right')
    ax2.grid(alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    plt.show()


# —————————————
# 3) RUN IT

# load your data
df = pd.read_csv('../../results/tables/df_model_test_scores.csv')

# choose tasks
tasks = [21522, 16246]
tasks = [21522]

# prepare & plot raw
tp, y_obs, t_idx, task_idx, dates = prepare_data_multi(df, tasks)
plot_raw_data_multi(tp, y_obs, t_idx, task_idx, tasks, dates)

# fit
trace = fit_capability_model_multi(tp, y_obs, t_idx, task_idx,
                                    n_samples=1000, n_tune=1000)

# in-sample diagnostics
az.plot_trace(trace); plt.tight_layout(); plt.show()
print(az.summary(trace, var_names=['mu','sigma_omega','g']))

plot_in_sample_fit(trace, tp, y_obs, t_idx, task_idx, tasks, dates)


future_times, c_stats, y_stats = simulate_forecast_from_posterior(
    trace, tp, H=100
)

# plot
plot_forecast_simulated(
    trace, tp, y_obs, t_idx, task_idx, tasks, dates,
    future_times, c_stats, y_stats
)




