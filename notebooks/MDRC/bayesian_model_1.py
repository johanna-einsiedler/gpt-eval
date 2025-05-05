



import numpy as np
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import pytensor.tensor as pt
from scipy.special import expit

# ── 1) Data ─────────────────────────────────────────────────────────────────
time_points = np.array([0, 63, 75, 81, 107, 113, 114, 114, 116, 117])
y_obs       = np.array([0.288,0.393,0.538,0.549,0.544,0.564,0.598,0.471,0.660,0.512])

# pretend the two at t=114 come from two different “test devices”
device_idx = np.array([0,0,0,0,0,0,1,2,0,0])
n_devices  = int(np.unique(device_idx).size)

# collapse to unique state times
unique_times, time_idx = np.unique(time_points, return_inverse=True)
T_state = len(unique_times)

# quick scatter of raw data (including duplicates)
plt.figure(figsize=(6,3))
plt.plot(time_points, y_obs, 'ro')
plt.xlabel("Time"); plt.ylabel("Test score")
plt.title("Raw Observations (including replicates)")
plt.tight_layout()
plt.show()


# ── 2) State-space model with non-centered RW ───────────────────────────────
with pm.Model() as model:
    # Priors
    c0          = pm.Normal('c0', mu=-2.0, sigma=1.0)
    mu          = pm.Normal('mu', mu=0.02, sigma=0.01)
    sigma_omega = pm.HalfCauchy('sigma_omega', beta=0.1)
    g           = pm.HalfNormal('g', sigma=1.0)
    sigma_nu    = pm.HalfCauchy('sigma_nu', beta=0.1, shape=n_devices)
    
    # Non-centered RW increments over unique times
    dt  = np.diff(unique_times)                    # length = T_state-1
    eps = pm.Normal('eps', 0.0, 1.0, shape=T_state-1)
    increments = mu*dt + sigma_omega*pt.sqrt(dt)*eps
    
    # Build latent path
    walk       = pt.concatenate([[c0], increments])          
    capability = pm.Deterministic('capability', pt.cumsum(walk))
    
    # Map each obs to its latent capability
    cap_at_obs = capability[time_idx]
    score_mu   = pm.math.invlogit(g * cap_at_obs)
    
    # Likelihood with device-specific noise
    pm.Normal('y', mu=score_mu, sigma=sigma_nu[device_idx], observed=y_obs)
    
    # Sample
    trace = pm.sample(
        tune=2000, draws=2000, chains=4,
        target_accept=0.95, return_inferencedata=True
    )


# ── 3) Sampling diagnostics ──────────────────────────────────────────────────
# Print summary (means, sd, HDI, ESS, R̂)
print(az.summary(
    trace,
    var_names=['c0','mu','sigma_omega','g','sigma_nu'],
    round_to=2
))

# Plot divergences / R̂ / ESS at a glance
az.plot_trace(trace, var_names=['c0','mu','sigma_omega','g','sigma_nu'])
plt.tight_layout()
plt.show()


# ── 4) Trace + marginal plots with custom labels ────────────────────────────
var_names = ['c0','mu','sigma_omega','g','sigma_nu']
pretty    = {
    'c0':           r'$c_0$ (init capability)',
    'mu':           r'$\mu$ (drift)',
    'sigma_omega':  r'$\sigma_\omega$ (process noise)',
    'g':            r'$g$ (discrimination)',
    'sigma_nu':     r'$\sigma_\nu$ (measurement noise)'
}

axes = az.plot_trace(trace, var_names=var_names, compact=True, figsize=(8,10))
for i, v in enumerate(var_names):
    axes[i,0].set_title(pretty[v])
    axes[i,1].set_ylabel(pretty[v])
plt.tight_layout()
plt.show()


# ── 5) Historical fit summaries ──────────────────────────────────────────────
# Flatten posterior draws
cap_samps = trace.posterior['capability'].stack(all=('chain','draw')).values  # (T_state, N)
g_samps   = trace.posterior['g'].stack(all=('chain','draw')).values            # (N,)

# Latent capability summaries
cap_mean = cap_samps.mean(axis=1)
cap_l, cap_u = np.percentile(cap_samps, [2.5,97.5], axis=1)

# Fitted score summaries
score_samps = expit(cap_samps * g_samps[None,:])
sc_mean = score_samps.mean(axis=1)
sc_l, sc_u = np.percentile(score_samps, [2.5,97.5], axis=1)

# Plot history
plt.figure(figsize=(12,4))
# latent
plt.subplot(1,2,1)
plt.plot(unique_times, cap_mean, 'b-')
plt.fill_between(unique_times, cap_l, cap_u, color='b', alpha=0.2)
plt.xlabel("Time"); plt.ylabel("Capability"); plt.title("Historical Capability")
# scores
plt.subplot(1,2,2)
plt.plot(time_points, y_obs, 'ro', label='Obs')
plt.plot(unique_times, sc_mean, 'b-', label='Fit')
plt.fill_between(unique_times, sc_l, sc_u, color='b', alpha=0.2)
plt.xlabel("Time"); plt.ylabel("Test score")
plt.title("Model Fit")
plt.legend(); plt.tight_layout(); plt.show()


# ── 6) Forecast future capability & scores ─────────────────────────────────
H = 50
future_times = np.arange(unique_times[-1]+1, unique_times[-1]+1+H)
fd = np.diff(future_times, prepend=unique_times[-1])

with pm.Model() as fwd:
    # Priors from posterior means
    mu_f = pm.Normal('mu_f',
                     mu=trace.posterior['mu'].mean().item(),
                     sigma=trace.posterior['mu'].std().item())
    so_f = pm.HalfCauchy('sigma_omega_f',
                         beta=trace.posterior['sigma_omega'].mean().item())
    g_f  = pm.HalfNormal('g_f',
                         sigma=trace.posterior['g'].mean().item())
    c_last = pm.Normal('c_last',
                       mu=cap_mean[-1],
                       sigma=trace.posterior['sigma_omega'].mean().item())
    
    # Innovations & walk
    eps_f = pm.Normal('eps_f', 0, 1, shape=H)
    inc_f = mu_f*fd + so_f*pt.sqrt(fd)*eps_f
    walk_f = pt.concatenate([[c_last], inc_f[:-1]])
    cap_f  = pm.Deterministic('cap_f', pt.cumsum(walk_f))
    sc_f   = pm.Deterministic('sc_f', pm.math.invlogit(g_f*cap_f))
    
    fcast = pm.sample(tune=1000, draws=1000, chains=2,
                      target_accept=0.95, return_inferencedata=True)

# Forecast summaries
capf = fcast.posterior['cap_f'].stack(all=('chain','draw')).values
sf   = fcast.posterior['sc_f'].stack(all=('chain','draw')).values

cf_m, cf_l, cf_u = capf.mean(axis=1), *np.percentile(capf, [2.5,97.5], axis=1)
sf_m, sf_l, sf_u = sf.mean(axis=1),   *np.percentile(sf, [2.5,97.5], axis=1)


# ── 7) Plot history + forecast ──────────────────────────────────────────────
plt.figure(figsize=(12,4))
# capability
plt.subplot(1,2,1)
plt.plot(unique_times, cap_mean, 'b-'); plt.fill_between(unique_times, cap_l, cap_u, alpha=0.2)
plt.plot(future_times, cf_m, 'g-');   plt.fill_between(future_times, cf_l, cf_u, color='g', alpha=0.2)
plt.axvline(unique_times[-1], ls='--', color='r')
plt.title("Capability: History & Forecast")
# test score
plt.subplot(1,2,2)
plt.plot(time_points, y_obs,'ro')
plt.plot(unique_times, sc_mean,'b-');   plt.fill_between(unique_times, sc_l, sc_u, alpha=0.2)
plt.plot(future_times, sf_m,'g-');      plt.fill_between(future_times, sf_l, sf_u, color='g', alpha=0.2)
plt.axvline(unique_times[-1], ls='--', color='r')
plt.title("Test Score: History & Forecast")
plt.tight_layout()
plt.show()



#### NOTE You can optionally give each measurement device its own error variance via a vector sigma_nu[device_idx];

import numpy as np
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import pytensor.tensor as pt

#### NOTE You can optionally give each measurement device its own error variance via a vector sigma_nu[device_idx];

# (a) your raw data, two observations at t=114
time_points = np.array([0,  63,  75,  81, 107, 113, 114, 114, 116, 117])
y_obs       = np.array([0.288,0.393,0.538,0.549,0.544,0.564,0.598,0.471,0.660,0.512])

# (b) pretend those two at t=114 come from two different tests:
#     assign a device/test index to each observation
#     here we arbitrarily call them device 0 and device 1
device_idx = np.array([0, 0, 0, 0, 0, 0, 1, 2, 0, 0])  
# (you could have more devices; just encode each obs’s source)
n_devices = len(np.unique(device_idx))

# (c) build the unique‐time array and an index map
unique_times, time_idx = np.unique(time_points, return_inverse=True)
# unique_times = [  0,  63,  75,  81, 107, 113, 114, 116, 117 ]
# time_idx    = [   0,   1,   2,   3,   4,   5,   6,   6,   7,   8 ]
T_state = len(unique_times)

plt.plot(time_points, y_obs, 'ro')
plt.xlabel("Time"); plt.ylabel("Test score"); plt.title("Observed scores")
plt.show()

with pm.Model() as model:
    # Priors on the state‐evolution side
    c0          = pm.Normal('c0', mu=-2.0, sigma=1.0)
    mu          = pm.Normal('mu', mu=0.02, sigma=0.01)
    sigma_omega = pm.HalfCauchy('sigma_omega', beta=0.1)
    g           = pm.HalfNormal('g', sigma=1.0)
    
    # Hierarchical measurement noise: one sigma per device
    sigma_nu = pm.HalfCauchy('sigma_nu', beta=0.1, shape=n_devices)

    # 1) Build the non‐centered random walk over unique times
    dt  = np.diff(unique_times)                 # length = T_state-1
    eps = pm.Normal('eps', 0.0, 1.0, shape=T_state-1)

    increments = mu * dt + sigma_omega * pt.sqrt(dt) * eps
    walk       = pt.concatenate([[c0], increments])   # length T_state
    capability = pm.Deterministic('capability', pt.cumsum(walk))

    # 2) Map each of your 10 observations onto its latent index:
    cap_at_obs = capability[time_idx]

    # 3) Measurement model:
    #    - if all obs share one noise σ, you’d use sigma_nu[0]
    #    - here we pick sigma_nu[device_idx] per obs
    score_mu = pm.math.invlogit(g * cap_at_obs)
    y = pm.Normal(
        'y',
        mu=score_mu,
        sigma=sigma_nu[device_idx],
        observed=y_obs
    )

    trace = pm.sample(
        tune=2000,
        draws=2000,
        chains=4,
        target_accept=0.95,
        return_inferencedata=True,
    )


# pick the vars you want, in order
var_names = ['c0', 'mu', 'sigma_omega', 'g', 'sigma_nu']
# human‐friendly labels
pretty = {
    'c0': r'$c_0\ \text{(init capability)}$',
    'mu': r'$\mu\ \text{(drift)}$',
    'sigma_omega': r'$\sigma_\omega\ \text{(process noise)}$',
    'g': r'$g\ \text{(discrimination)}$',
    'sigma_nu': r'$\sigma_\nu\ \text{(measurement noise)}$',
}

# draw
axes = az.plot_trace(trace, var_names=var_names, compact=True, figsize=(8, 10))

# axes is a 2-D array: rows = variables, cols = [marginal, trace]
for i, var in enumerate(var_names):
    # set the title of the marginal plot
    axes[i, 0].set_title(pretty[var])
    # set the y-axis label of the trace plot
    axes[i, 1].set_ylabel(pretty[var])

plt.tight_layout()
plt.show()


# --- 4) Forecast future capability & scores ---
forecast_horizon = 50
future_times     = np.arange(unique_times[-1] + 1,
                             unique_times[-1] + 1 + forecast_horizon)
future_dt        = np.diff(future_times, prepend=unique_times[-1])

with pm.Model() as fwd:
    # use posterior means as priors
    mu_f          = pm.Normal('mu_f',
                         mu=trace.posterior['mu'].mean().item(),
                         sigma=trace.posterior['mu'].std().item())
    sigma_omega_f = pm.HalfCauchy(
                         'sigma_omega_f',
                         beta=trace.posterior['sigma_omega'].mean().item())
    g_f           = pm.HalfNormal(
                         'g_f',
                         sigma=trace.posterior['g'].mean().item())
    # start from last historical mean
    c_last = pm.Normal(
        'c_last',
        mu=cap_mean[-1],
        sigma=trace.posterior['sigma_omega'].mean().item()
    )
    # innovations
    eps_fut = pm.Normal('eps_fut', 0, 1, shape=forecast_horizon)
    increments = mu_f * future_dt + sigma_omega_f * pt.sqrt(future_dt) * eps_fut
    walk      = pt.concatenate([[c_last], increments[:-1]])
    cap_fut   = pm.Deterministic('cap_fut', pt.cumsum(walk))

    score_fut = pm.Deterministic('score_fut', pm.math.invlogit(g_f * cap_fut))

    forecast_trace = pm.sample(
        tune=1000,
        draws=1000,
        chains=2,
        target_accept=0.95,
        return_inferencedata=True
    )

# extract forecasts
capf = forecast_trace.posterior['cap_fut'].stack(all=('chain','draw')).values
sf   = forecast_trace.posterior['score_fut'].stack(all=('chain','draw')).values

capf_mean  = capf.mean(axis=1)
capf_l     = np.percentile(capf, 2.5, axis=1)
capf_u     = np.percentile(capf, 97.5, axis=1)

sf_mean    = sf.mean(axis=1)
sf_l       = np.percentile(sf, 2.5, axis=1)
sf_u       = np.percentile(sf, 97.5, axis=1)


# --- 5) Plot history + forecast ---
plt.figure(figsize=(12,5))

# capability
plt.subplot(1,2,1)
plt.plot(unique_times, cap_mean, 'b-', label="Historical")
plt.fill_between(unique_times, cap_l, cap_u, color='b', alpha=0.2)
plt.plot(future_times, capf_mean, 'g-', label="Forecast")
plt.fill_between(future_times, capf_l, capf_u, color='g', alpha=0.2)
plt.axvline(unique_times[-1], color='r', ls='--', label="Forecast start")
plt.xlabel("Time"); plt.ylabel("Capability"); plt.legend()
plt.title("Capability: History & Forecast")

# test scores
plt.subplot(1,2,2)
plt.plot(time_points, y_obs, 'ro', label="Observed")
plt.plot(unique_times, score_mean, 'b-', label="Historical fit")
plt.fill_between(unique_times, score_l, score_u, color='b', alpha=0.2)
plt.plot(future_times, sf_mean, 'g-', label="Forecast")
plt.fill_between(future_times, sf_l, sf_u, color='g', alpha=0.2)
plt.axvline(unique_times[-1], color='r', ls='--')
plt.xlabel("Time"); plt.ylabel("Test score"); plt.legend()
plt.title("Test Score: History & Forecast")

plt.tight_layout()
plt.show()

import numpy as np
from scipy.special import expit

# 1) pull out and flatten posterior draws
cap_ = trace.posterior['capability'].stack(s=('chain','draw')).values  # shape (T_state, N)
g_   = trace.posterior['g'].stack(s=('chain','draw')).values          # shape (N,)

# 2) latent summaries at the unique times
cap_mean  = cap_.mean(axis=1)
cap_l     = np.percentile(cap_, 2.5, axis=1)
cap_u     = np.percentile(cap_, 97.5, axis=1)

# 3) predictive test‐score summaries at the unique times
scores = expit(g_[None,:] * cap_)  # shape (T_state, N)
fit_mean  = scores.mean(axis=1)
fit_l     = np.percentile(scores, 2.5, axis=1)
fit_u     = np.percentile(scores, 97.5, axis=1)

# 4) make the two‐panel figure
plt.figure(figsize=(12,5))

# – Left: latent capability over *unique* times
plt.subplot(1,2,1)
plt.plot(unique_times, cap_mean, 'b-')
plt.fill_between(unique_times, cap_l, cap_u, color='b', alpha=0.2)
plt.xlabel('Time'); plt.ylabel('Capability (latent)')
plt.title('Estimated Technology Capability')

# – Right: all obs (including replicates) + model fit curve
plt.subplot(1,2,2)
plt.plot(time_points, y_obs, 'ro', label='Observed scores')   # plots both points at t=114
plt.plot(unique_times, fit_mean, 'b-', label='Model fit')
plt.fill_between(unique_times, fit_l, fit_u, color='b', alpha=0.2)
plt.xlabel('Time'); plt.ylabel('Test score')
plt.title('Model Fit with Replicates')
plt.legend()

plt.tight_layout()
plt.show()



import numpy as np
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import pytensor.tensor as pt
from scipy.special import expit

# --- 1) Posterior distributions of parameters ---
az.plot_posterior(
    trace,
    var_names=['c0', 'mu', 'sigma_omega', 'g', 'sigma_nu'],
    hdi_prob=0.95,
    kind='hist',
    figsize=(12, 8)
)
plt.suptitle("Posterior Distributions", y=1.02)
plt.tight_layout()
plt.show()


# --- 2) Re-compute history summaries at unique times ---
# pull raw arrays
cap_samples = trace.posterior['capability'].stack(all=('chain','draw')).values  # (T_state, N)
g_samples   = trace.posterior['g'].stack(all=('chain','draw')).values          # (N,)

# summaries for latent capability
cap_mean  = cap_samples.mean(axis=1)
cap_l     = np.percentile(cap_samples, 2.5, axis=1)
cap_u     = np.percentile(cap_samples, 97.5, axis=1)

# summaries for fitted scores
score_samps = expit(cap_samples * g_samples[None, :])
score_mean  = score_samps.mean(axis=1)
score_l     = np.percentile(score_samps, 2.5, axis=1)
score_u     = np.percentile(score_samps, 97.5, axis=1)


# --- 3) Plot history with credible bands ---
plt.figure(figsize=(12,5))

# latent capability
plt.subplot(1,2,1)
plt.plot(unique_times, cap_mean, 'b-')
plt.fill_between(unique_times, cap_l, cap_u, color='b', alpha=0.2)
plt.xlabel("Time")
plt.ylabel("Capability (latent)")
plt.title("Estimated Capability (historical)")

# test-score fit
plt.subplot(1,2,2)
plt.plot(time_points, y_obs, 'ro', label="Observed")
plt.plot(unique_times, score_mean, 'b-', label="Fit")
plt.fill_between(unique_times, score_l, score_u, color='b', alpha=0.2)
plt.xlabel("Time")
plt.ylabel("Test score")
plt.title("Model Fit to Data")
plt.legend()

plt.tight_layout()
plt.show()


# --- 4) Forecast future capability & scores ---
forecast_horizon = 50
future_times     = np.arange(unique_times[-1] + 1,
                             unique_times[-1] + 1 + forecast_horizon)
future_dt        = np.diff(future_times, prepend=unique_times[-1])

with pm.Model() as fwd:
    # use posterior means as priors
    mu_f          = pm.Normal('mu_f',
                         mu=trace.posterior['mu'].mean().item(),
                         sigma=trace.posterior['mu'].std().item())
    sigma_omega_f = pm.HalfCauchy(
                         'sigma_omega_f',
                         beta=trace.posterior['sigma_omega'].mean().item())
    g_f           = pm.HalfNormal(
                         'g_f',
                         sigma=trace.posterior['g'].mean().item())
    # start from last historical mean
    c_last = pm.Normal(
        'c_last',
        mu=cap_mean[-1],
        sigma=trace.posterior['sigma_omega'].mean().item()
    )
    # innovations
    eps_fut = pm.Normal('eps_fut', 0, 1, shape=forecast_horizon)
    increments = mu_f * future_dt + sigma_omega_f * pt.sqrt(future_dt) * eps_fut
    walk      = pt.concatenate([[c_last], increments[:-1]])
    cap_fut   = pm.Deterministic('cap_fut', pt.cumsum(walk))

    score_fut = pm.Deterministic('score_fut', pm.math.invlogit(g_f * cap_fut))

    forecast_trace = pm.sample(
        tune=1000,
        draws=1000,
        chains=2,
        target_accept=0.95,
        return_inferencedata=True
    )

# extract forecasts
capf = forecast_trace.posterior['cap_fut'].stack(all=('chain','draw')).values
sf   = forecast_trace.posterior['score_fut'].stack(all=('chain','draw')).values

capf_mean  = capf.mean(axis=1)
capf_l     = np.percentile(capf, 2.5, axis=1)
capf_u     = np.percentile(capf, 97.5, axis=1)

sf_mean    = sf.mean(axis=1)
sf_l       = np.percentile(sf, 2.5, axis=1)
sf_u       = np.percentile(sf, 97.5, axis=1)


# --- 5) Plot history + forecast ---
plt.figure(figsize=(12,5))

# capability
plt.subplot(1,2,1)
plt.plot(unique_times, cap_mean, 'b-', label="Historical")
plt.fill_between(unique_times, cap_l, cap_u, color='b', alpha=0.2)
plt.plot(future_times, capf_mean, 'g-', label="Forecast")
plt.fill_between(future_times, capf_l, capf_u, color='g', alpha=0.2)
plt.axvline(unique_times[-1], color='r', ls='--', label="Forecast start")
plt.xlabel("Time"); plt.ylabel("Capability"); plt.legend()
plt.title("Capability: History & Forecast")

# test scores
plt.subplot(1,2,2)
plt.plot(time_points, y_obs, 'ro', label="Observed")
plt.plot(unique_times, score_mean, 'b-', label="Historical fit")
plt.fill_between(unique_times, score_l, score_u, color='b', alpha=0.2)
plt.plot(future_times, sf_mean, 'g-', label="Forecast")
plt.fill_between(future_times, sf_l, sf_u, color='g', alpha=0.2)
plt.axvline(unique_times[-1], color='r', ls='--')
plt.xlabel("Time"); plt.ylabel("Test score"); plt.legend()
plt.title("Test Score: History & Forecast")

plt.tight_layout()
plt.show()








########
# Below without possible replication
########

# 1) Your data (two obs at t=114)
time_points = np.array([0,  63,  75,  81, 107, 113, 114, 114, 116, 117])
y_obs       = np.array([0.288,0.393,0.538,0.549,0.544,0.564,0.598,0.471,0.660,0.512])

# 2) Collapse to unique times + build index
unique_times, time_idx = np.unique(time_points, return_inverse=True)
# unique_times = [  0,  63,  75,  81, 107, 113, 114, 116, 117 ]
# time_idx    = [   0,   1,   2,   3,   4,   5,   6,   6,   7,   8 ]
T_state = len(unique_times)

# Quick check
plt.plot(time_points, y_obs, 'ro')
plt.xlabel("Time"); plt.ylabel("Test score"); plt.title("Observed scores")
plt.show()

with pm.Model() as model:
    # Priors
    c0          = pm.Normal('c0', mu=-2.0, sigma=1.0)     # initial capability
    mu          = pm.Normal('mu', mu=0.02, sigma=0.01)    # drift
    sigma_omega = pm.HalfCauchy('sigma_omega', beta=0.1)  # process noise scale
    g           = pm.HalfNormal('g', sigma=1.0)           # logistic steepness
    sigma_nu    = pm.HalfCauchy('sigma_nu', beta=0.1)     # measurement noise

    # Build non-centered random walk on the unique times
    dt = np.diff(unique_times)           # length = T_state−1
    eps = pm.Normal('eps', 0.0, 1.0, shape=T_state-1)

    # increments = drift * dt + sigma_omega * sqrt(dt) * standard_normal
    increments = mu * dt + sigma_omega * pt.sqrt(dt) * eps

    # Prepend the initial "step" = c0, then cumsum to get all states
    walk = pt.concatenate([[c0], increments])   # length T_state
    capability = pm.Deterministic('capability', pt.cumsum(walk))

    # Map each observation back onto its latent state
    score_mean = pm.math.invlogit(g * capability[time_idx])

    # Likelihood (handles two obs at t=114 automatically)
    y = pm.Normal('y', mu=score_mean, sigma=sigma_nu, observed=y_obs)

    # Sample with a safer target_accept
    trace = pm.sample(tune=2000, draws=2000, chains=4, target_accept=0.95,
                      return_inferencedata=True)

# Summarize & plot as before:
print(az.summary(trace, var_names=['c0','mu','sigma_omega','g','sigma_nu']))
az.plot_trace(trace)
plt.show()


# Extract capability estimates and credible intervals
capability_traces = trace.posterior['capability_latent'].values
capability_mean = capability_traces.mean(axis=(0, 1))
capability_lower = np.percentile(capability_traces, 2.5, axis=(0, 1))
capability_upper = np.percentile(capability_traces, 97.5, axis=(0, 1))

# Extract predicted scores and credible intervals
score_mean = trace.posterior['score_mean'].mean(dim=('chain', 'draw')).values
score_lower = np.percentile(trace.posterior['score_mean'].values, 2.5, axis=(0, 1))
score_upper = np.percentile(trace.posterior['score_mean'].values, 97.5, axis=(0, 1))

# Plot estimated capability trajectory
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(time_points, capability_mean, 'b-', label='Estimated capability')
plt.fill_between(time_points, capability_lower, capability_upper, color='b', alpha=0.2, label='95% CI')
plt.xlabel('Time')
plt.ylabel('Capability (latent)')
plt.title('Estimated Technology Capability')
plt.legend()

# Plot test scores and model fit
plt.subplot(1, 2, 2)
plt.plot(time_points, y_obs, 'ro', label='Observed scores')
plt.plot(time_points, score_mean, 'b-', label='Model fit')
plt.fill_between(time_points, score_lower, score_upper, color='b', alpha=0.2, label='95% CI')
plt.xlabel('Time')
plt.ylabel('Test score')
plt.title('Model Fit to Test Scores')
plt.legend()
plt.tight_layout()
plt.show()

# Forecast future capabilities
# Define how many time points to forecast into the future
forecast_horizon = 50
future_times = np.arange(time_points[-1] + 1, time_points[-1] + 1 + forecast_horizon)
future_dt = np.diff(future_times, prepend=time_points[-1])




import numpy as np
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import pandas as pd
from scipy.special import expit
import pytensor.tensor as pt  # Use pytensor instead of pm.math for set_subtensor

# For reproducibility
np.random.seed(42)

times = [ 0,  63,  75,  81, 107, 113, 114, 114, 116, 117]
test_scores = [0.28840782, 0.39331269, 0.53783931, 0.54890993, 0.54407241, 0.56407241, 0.59765907,
 0.47089476, 0.65987823, 0.51249848]

T = len(times)

y_obs = np.array(test_scores)
time_points = np.array(times)


# find the unique times and an index mapping
unique_times, time_idx = np.unique(time_points, return_inverse=True)
# unique_times = [0, 63, 75, …, 114, 116, 117]
# time_idx = [0, 1, 2, …, 5, 6, 6, 7, 8, 9]
T_state = len(unique_times)

plt.plot(time_points, y_obs, 'ro', label='Observed test scores')
plt.xlabel('Time')
plt.ylabel('Test score')
plt.title('Observed test scores')
plt.legend()
plt.tight_layout()
plt.show()

# Now implementing the Bayesian state space model with PyMC
with pm.Model() as model:
    # Prior for initial capability (c_0)
    # We expect initial capability to be negative as test scores start below 0.5
    c_0 = pm.Normal('c_0', mu=-2.0, sigma=1.0)
    
    # Prior for drift parameter (average rate of technological improvement)
    mu = pm.Normal('mu', mu=0.02, sigma=0.01)  # Small positive drift
    
    # Prior for process noise (uncertainty in capability evolution)
    sigma_omega = pm.HalfCauchy('sigma_omega', beta=0.1)
    
    # Prior for discrimination parameter (test sensitivity)
    g = pm.HalfNormal('g', sigma=1.0)
    
    # Prior for measurement noise
    sigma_nu = pm.HalfCauchy('sigma_nu', beta=0.1)
    
    # Instead of using a direct capability approach with set_subtensor, use a scan approach
    capabilities = [c_0]  # Start with initial capability
    
    # Model capability evolution over time as a manual random walk with drift
    for t in range(1, T):
        # Time difference between current and previous point
        dt = time_points[t] - time_points[t-1]
        
        # Expected increment based on drift
        drift = mu * dt
        
        # Process noise scaled by sqrt of time difference
        noise_scale = sigma_omega * np.sqrt(dt)
        
        # Add new capability based on previous one
        new_capability = capabilities[-1] + drift + pm.Normal(f'process_noise_{t}', 0, noise_scale)
        capabilities.append(new_capability)
    
    # Stack all capabilities into a tensor
    capability_latent = pm.Deterministic('capability_latent', pt.stack(capabilities))
    
    # Define the measurement model using logistic function
    # The mean of observed test scores based on capability
    score_mean = pm.Deterministic('score_mean', pm.math.invlogit(g * capability_latent))
    
    # Observed test scores with measurement noise
    y = pm.Normal('y', mu=score_mean, sigma=sigma_nu, observed=y_obs)
    
    # Sample from the posterior
    trace = pm.sample(2000, tune=1000, chains=4, cores=1, return_inferencedata=True)

# Examine the results
summary = az.summary(trace)
print(summary)

# Plot the trace
az.plot_trace(trace)
plt.tight_layout()
plt.show()

# Extract capability estimates and credible intervals
capability_traces = trace.posterior['capability_latent'].values
capability_mean = capability_traces.mean(axis=(0, 1))
capability_lower = np.percentile(capability_traces, 2.5, axis=(0, 1))
capability_upper = np.percentile(capability_traces, 97.5, axis=(0, 1))

# Extract predicted scores and credible intervals
score_mean = trace.posterior['score_mean'].mean(dim=('chain', 'draw')).values
score_lower = np.percentile(trace.posterior['score_mean'].values, 2.5, axis=(0, 1))
score_upper = np.percentile(trace.posterior['score_mean'].values, 97.5, axis=(0, 1))

# Plot estimated capability trajectory
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(time_points, capability_mean, 'b-', label='Estimated capability')
plt.fill_between(time_points, capability_lower, capability_upper, color='b', alpha=0.2, label='95% CI')
plt.xlabel('Time')
plt.ylabel('Capability (latent)')
plt.title('Estimated Technology Capability')
plt.legend()

# Plot test scores and model fit
plt.subplot(1, 2, 2)
plt.plot(time_points, y_obs, 'ro', label='Observed scores')
plt.plot(time_points, score_mean, 'b-', label='Model fit')
plt.fill_between(time_points, score_lower, score_upper, color='b', alpha=0.2, label='95% CI')
plt.xlabel('Time')
plt.ylabel('Test score')
plt.title('Model Fit to Test Scores')
plt.legend()
plt.tight_layout()
plt.show()

# Forecast future capabilities
# Define how many time points to forecast into the future
forecast_horizon = 50
future_times = np.arange(time_points[-1] + 1, time_points[-1] + 1 + forecast_horizon)
future_dt = np.diff(future_times, prepend=time_points[-1])

with pm.Model() as forecast_model:
    # Use posterior means as starting points for parameter priors
    mu_forecast = pm.Normal('mu_forecast', mu=trace.posterior['mu'].mean().item(), 
                           sigma=0.01)
    sigma_omega_forecast = pm.HalfCauchy('sigma_omega_forecast', 
                                        beta=trace.posterior['sigma_omega'].mean().item())
    g_forecast = pm.HalfNormal('g_forecast', sigma=trace.posterior['g'].mean().item())
    
    # Start with the last estimated capability
    c_last = pm.Normal('c_last', mu=capability_mean[-1], sigma=0.1)
    
    # Initialize future capabilities list
    future_capabilities = [c_last]
    
    # Model future capability evolution
    for t in range(1, forecast_horizon):
        # Time difference is 1 in the future projection
        new_capability = future_capabilities[-1] + mu_forecast * future_dt[t] + \
                         pm.Normal(f'future_noise_{t}', 0, sigma_omega_forecast * np.sqrt(future_dt[t]))
        future_capabilities.append(new_capability)
    
    # Stack all future capabilities into a tensor
    future_capability_latent = pm.Deterministic('future_capability_latent', pt.stack(future_capabilities))
    
    # Future test scores
    future_scores = pm.Deterministic('future_scores', pm.math.invlogit(g_forecast * future_capability_latent))
    
    # Sample from the forecast
    forecast_trace = pm.sample(1000, tune=500, chains=2, cores=1, return_inferencedata=True)

# Extract forecast results
future_capability_traces = forecast_trace.posterior['future_capability_latent'].values
future_capability_mean = future_capability_traces.mean(axis=(0, 1))
future_capability_lower = np.percentile(future_capability_traces, 2.5, axis=(0, 1))
future_capability_upper = np.percentile(future_capability_traces, 97.5, axis=(0, 1))

future_scores_mean = forecast_trace.posterior['future_scores'].mean(dim=('chain', 'draw')).values
future_scores_lower = np.percentile(forecast_trace.posterior['future_scores'].values, 2.5, axis=(0, 1))
future_scores_upper = np.percentile(forecast_trace.posterior['future_scores'].values, 97.5, axis=(0, 1))

# Plot combined history and forecast
plt.figure(figsize=(12, 5))

# Plot capability
plt.subplot(1, 2, 1)
# Historical
plt.plot(time_points, capability_mean, 'b-', label='Historical capability')
plt.fill_between(time_points, capability_lower, capability_upper, color='b', alpha=0.2)
# Forecast
plt.plot(future_times, future_capability_mean, 'g-', label='Forecast capability')
plt.fill_between(future_times, future_capability_lower, future_capability_upper, color='g', alpha=0.2)
plt.axvline(x=time_points[-1], color='r', linestyle='--', label='Forecast start')
plt.xlabel('Time')
plt.ylabel('Capability (latent)')
plt.title('Technology Capability Forecast')
plt.legend()

# Plot test scores
plt.subplot(1, 2, 2)
# Historical
plt.plot(time_points, y_obs, 'ro', label='Observed scores')
plt.plot(time_points, score_mean, 'b-', label='Historical fit')
plt.fill_between(time_points, score_lower, score_upper, color='b', alpha=0.2)
# Forecast
plt.plot(future_times, future_scores_mean, 'g-', label='Forecast scores')
plt.fill_between(future_times, future_scores_lower, future_scores_upper, color='g', alpha=0.2)
plt.axvline(x=time_points[-1], color='r', linestyle='--', label='Forecast start')
plt.xlabel('Time')
plt.ylabel('Test score')
plt.title('Test Score Forecast')
plt.legend()

plt.tight_layout()
plt.show()

import arviz as az

# Include the default diagnostics columns, especially r_hat and ess_*
df = az.summary(
    trace,
    var_names=['c_0','mu','sigma_omega','g','sigma_nu'],  # core scalar parameters
    round_to=2
)
print(df[['mean','sd','ess_bulk','ess_tail','r_hat']])
