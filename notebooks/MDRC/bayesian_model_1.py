import numpy as np
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import pytensor.tensor as pt

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


time_points = np.array([  0,  63,  75,  81, 107, 113, 114, 114, 116, 117])
y_obs        = np.array([0.288,0.393,0.538,0.549,0.544,0.564,0.598,0.471,0.660,0.512])

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
