import pandas as pd
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import pytensor.tensor as pt
from datetime import datetime
import numpy as np

# For reproducibility
np.random.seed(42)

df = pd.read_csv('../../results/tables/df_model_test_scores.csv')

df[['Publication date', 'score']][df['task_id'] == 21522]
df[['Publication date', 'score']][df['task_id'] == 16246]

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import pytensor.tensor as pt
from datetime import datetime

def prepare_data(df, task_id, handle_nan='ignore'):
    """
    Prepare data for the model from a dataframe.
    
    Parameters:
    -----------
    df : pandas DataFrame
        DataFrame containing the data
    task_id : int
        ID of the task to analyze
    handle_nan : str, optional
        How to handle NaN values: 'ignore' (remove them) or 'zero' (replace with 0)
        
    Returns:
    --------
    time_points : numpy array
        Array of time points in days since the first observation
    y_obs : numpy array
        Array of observed test scores
    dates : list
        List of publication dates
    """
    # Filter data for the specific task
    task_df = df[df['task_id'] == task_id][['Publication date', 'score']].copy()
    
    # Handle NaN values
    if handle_nan == 'zero':
        task_df['score'] = task_df['score'].fillna(0)
    elif handle_nan == 'ignore':
        task_df = task_df.dropna(subset=['score'])
    
    # Convert publication dates to datetime
    task_df['Publication date'] = pd.to_datetime(task_df['Publication date'])
    
    # Sort by date
    task_df = task_df.sort_values('Publication date')
    
    # Calculate days since first observation
    first_date = task_df['Publication date'].min()
    task_df['days'] = (task_df['Publication date'] - first_date).dt.days
    
    # Extract data
    time_points = task_df['days'].values
    y_obs = task_df['score'].values / 100.0  # Normalize scores to [0,1]
    dates = task_df['Publication date'].tolist()
    
    return time_points, y_obs, dates

def fit_capability_model(time_points, y_obs, n_samples=2000, n_tune=1000, n_chains=4, random_seed=42):
    """
    Fit the Bayesian state space model for technology capability.
    
    Parameters:
    -----------
    time_points : numpy array
        Array of time points
    y_obs : numpy array
        Array of observed test scores
    n_samples : int, optional
        Number of samples to draw
    n_tune : int, optional
        Number of tuning steps
    n_chains : int, optional
        Number of chains
    random_seed : int, optional
        Random seed for reproducibility
        
    Returns:
    --------
    trace : InferenceData
        Trace of the model
    """
    # Set random seed for reproducibility
    np.random.seed(random_seed)
    
    T = len(time_points)
    
    with pm.Model() as model:
        # Prior for initial capability (c_0)
        # We expect initial capability to be negative as test scores may start below 0.5
        c_0 = pm.Normal('c_0', mu=-2.0, sigma=1.0)
        
        # Prior for drift parameter (average rate of technological improvement)
        mu = pm.Normal('mu', mu=0.02, sigma=0.01)  # Small positive drift
        
        # Prior for process noise (uncertainty in capability evolution)
        sigma_omega = pm.HalfCauchy('sigma_omega', beta=0.1)
        
        # Prior for discrimination parameter (test sensitivity)
        g = pm.HalfNormal('g', sigma=1.0)
        
        # Prior for measurement noise
        sigma_nu = pm.HalfCauchy('sigma_nu', beta=0.1)
        
        # Initialize capabilities list with initial capability
        capabilities = [c_0]
        
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
        trace = pm.sample(n_samples, tune=n_tune, chains=n_chains, cores=1, random_seed=random_seed, return_inferencedata=True)
    
    return trace

def forecast_capability(trace, time_points, forecast_horizon=100, random_seed=42):
    """
    Forecast future capabilities based on the fitted model.
    
    Parameters:
    -----------
    trace : InferenceData
        Trace of the fitted model
    time_points : numpy array
        Array of time points used for fitting
    forecast_horizon : int, optional
        Number of days to forecast
    random_seed : int, optional
        Random seed for reproducibility
        
    Returns:
    --------
    forecast_trace : InferenceData
        Trace of the forecast model
    future_times : numpy array
        Array of future time points
    """
    # Set random seed for reproducibility
    np.random.seed(random_seed)
    
    # Extract capability estimates
    capability_traces = trace.posterior['capability_latent'].values
    capability_mean = capability_traces.mean(axis=(0, 1))
    
    # Define future time points
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
        forecast_trace = pm.sample(1000, tune=500, chains=2, cores=1, random_seed=random_seed, return_inferencedata=True)
    
    return forecast_trace, future_times

def plot_raw_data(time_points, y_obs, dates=None):
    """
    Plot the raw data.
    
    Parameters:
    -----------
    time_points : numpy array
        Array of time points
    y_obs : numpy array
        Array of observed test scores
    dates : list, optional
        List of dates corresponding to time points
    """
    plt.figure(figsize=(10, 6))
    plt.plot(time_points, y_obs, 'ro', markersize=8, label='Observed test scores')
    
    # Add date labels if provided
    if dates is not None:
        date_labels = [d.strftime('%Y-%m') for d in dates]
        plt.xticks(time_points, date_labels, rotation=45, ha='right')
    else:
        plt.xlabel('Time (days)')
    
    plt.ylabel('Test score')
    plt.title('Observed Test Scores')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_trace_and_summary(trace):
    """
    Plot the trace and summary statistics.
    
    Parameters:
    -----------
    trace : InferenceData
        Trace of the fitted model
    """
    # Display summary statistics
    summary = az.summary(trace)
    print("Summary Statistics:")
    print(summary)
    
    # Plot trace
    az.plot_trace(trace)
    plt.tight_layout()
    plt.show()

def plot_model_fit(time_points, y_obs, trace, dates=None):
    """
    Plot the model fit to the data.
    
    Parameters:
    -----------
    time_points : numpy array
        Array of time points
    y_obs : numpy array
        Array of observed test scores
    trace : InferenceData
        Trace of the fitted model
    dates : list, optional
        List of dates corresponding to time points
    """
    # Extract capability estimates and credible intervals
    capability_traces = trace.posterior['capability_latent'].values
    capability_mean = capability_traces.mean(axis=(0, 1))
    capability_lower = np.percentile(capability_traces, 2.5, axis=(0, 1))
    capability_upper = np.percentile(capability_traces, 97.5, axis=(0, 1))
    
    # Extract predicted scores and credible intervals
    score_mean = trace.posterior['score_mean'].mean(dim=('chain', 'draw')).values
    score_lower = np.percentile(trace.posterior['score_mean'].values, 2.5, axis=(0, 1))
    score_upper = np.percentile(trace.posterior['score_mean'].values, 97.5, axis=(0, 1))
    
    # Plot estimated capability trajectory and model fit
    plt.figure(figsize=(14, 6))
    
    # Plot capability
    plt.subplot(1, 2, 1)
    plt.plot(time_points, capability_mean, 'b-', linewidth=2, label='Estimated capability')
    plt.fill_between(time_points, capability_lower, capability_upper, color='b', alpha=0.2, label='95% CI')
    
    # Add date labels if provided
    if dates is not None:
        date_labels = [d.strftime('%Y-%m') for d in dates]
        plt.xticks(time_points, date_labels, rotation=45, ha='right')
    else:
        plt.xlabel('Time (days)')
        
    plt.ylabel('Capability (latent)')
    plt.title('Estimated Technology Capability')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Plot test scores
    plt.subplot(1, 2, 2)
    plt.plot(time_points, y_obs, 'ro', markersize=8, label='Observed scores')
    plt.plot(time_points, score_mean, 'b-', linewidth=2, label='Model fit')
    plt.fill_between(time_points, score_lower, score_upper, color='b', alpha=0.2, label='95% CI')
    
    # Add date labels if provided
    if dates is not None:
        date_labels = [d.strftime('%Y-%m') for d in dates]
        plt.xticks(time_points, date_labels, rotation=45, ha='right')
    else:
        plt.xlabel('Time (days)')
    
    plt.ylabel('Test score')
    plt.title('Model Fit to Test Scores')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.tight_layout()
    plt.show()

def plot_forecast(time_points, y_obs, trace, forecast_trace, future_times, dates=None):
    """
    Plot the historical data and forecast.
    
    Parameters:
    -----------
    time_points : numpy array
        Array of time points
    y_obs : numpy array
        Array of observed test scores
    trace : InferenceData
        Trace of the fitted model
    forecast_trace : InferenceData
        Trace of the forecast model
    future_times : numpy array
        Array of future time points
    dates : list, optional
        List of dates corresponding to time points
    """
    # Extract historical capability estimates and credible intervals
    capability_traces = trace.posterior['capability_latent'].values
    capability_mean = capability_traces.mean(axis=(0, 1))
    capability_lower = np.percentile(capability_traces, 2.5, axis=(0, 1))
    capability_upper = np.percentile(capability_traces, 97.5, axis=(0, 1))
    
    # Extract historical score estimates and credible intervals
    score_mean = trace.posterior['score_mean'].mean(dim=('chain', 'draw')).values
    score_lower = np.percentile(trace.posterior['score_mean'].values, 2.5, axis=(0, 1))
    score_upper = np.percentile(trace.posterior['score_mean'].values, 97.5, axis=(0, 1))
    
    # Extract forecast capability estimates and credible intervals
    future_capability_traces = forecast_trace.posterior['future_capability_latent'].values
    future_capability_mean = future_capability_traces.mean(axis=(0, 1))
    future_capability_lower = np.percentile(future_capability_traces, 2.5, axis=(0, 1))
    future_capability_upper = np.percentile(future_capability_traces, 97.5, axis=(0, 1))
    
    # Extract forecast score estimates and credible intervals
    future_scores_mean = forecast_trace.posterior['future_scores'].mean(dim=('chain', 'draw')).values
    future_scores_lower = np.percentile(forecast_trace.posterior['future_scores'].values, 2.5, axis=(0, 1))
    future_scores_upper = np.percentile(forecast_trace.posterior['future_scores'].values, 97.5, axis=(0, 1))
    
    # Plot combined history and forecast
    plt.figure(figsize=(14, 6))
    
    # Plot capability
    plt.subplot(1, 2, 1)
    # Historical
    plt.plot(time_points, capability_mean, 'b-', linewidth=2, label='Historical capability')
    plt.fill_between(time_points, capability_lower, capability_upper, color='b', alpha=0.2)
    # Forecast
    plt.plot(future_times, future_capability_mean, 'g-', linewidth=2, label='Forecast capability')
    plt.fill_between(future_times, future_capability_lower, future_capability_upper, color='g', alpha=0.2)
    plt.axvline(x=time_points[-1], color='r', linestyle='--', label='Forecast start')
    
    # Add date ticks - simplified for clarity with large time spans
    if dates is not None:
        # Create future dates
        first_date = dates[0]
        all_dates = dates + [first_date + pd.Timedelta(days=int(t - time_points[0])) for t in future_times]
        
        # Select a subset of dates for ticks to avoid overcrowding
        all_times = np.concatenate([time_points, future_times])
        tick_indices = np.linspace(0, len(all_times)-1, min(10, len(all_times))).astype(int)
        tick_times = all_times[tick_indices]
        tick_dates = [all_dates[i].strftime('%Y-%m') for i in tick_indices]
        
        plt.xticks(tick_times, tick_dates, rotation=45, ha='right')
    else:
        plt.xlabel('Time (days)')
    
    plt.ylabel('Capability (latent)')
    plt.title('Technology Capability Forecast')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Plot test scores
    plt.subplot(1, 2, 2)
    # Historical
    plt.plot(time_points, y_obs, 'ro', markersize=8, label='Observed scores')
    plt.plot(time_points, score_mean, 'b-', linewidth=2, label='Historical fit')
    plt.fill_between(time_points, score_lower, score_upper, color='b', alpha=0.2)
    # Forecast
    plt.plot(future_times, future_scores_mean, 'g-', linewidth=2, label='Forecast scores')
    plt.fill_between(future_times, future_scores_lower, future_scores_upper, color='g', alpha=0.2)
    plt.axvline(x=time_points[-1], color='r', linestyle='--', label='Forecast start')
    
    # Add date ticks - simplified for clarity with large time spans
    if dates is not None:
        plt.xticks(tick_times, tick_dates, rotation=45, ha='right')
    else:
        plt.xlabel('Time (days)')
    
    plt.ylabel('Test score')
    plt.title('Test Score Forecast')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.tight_layout()
    plt.show()

def print_forecast_results(forecast_trace, future_times, first_date):
    """
    Print key forecast results.
    
    Parameters:
    -----------
    forecast_trace : InferenceData
        Trace of the forecast model
    future_times : numpy array
        Array of future time points
    first_date : datetime
        First date in the dataset (to calculate future dates)
    """
    # Extract forecast parameters
    mu_mean = forecast_trace.posterior['mu_forecast'].mean().item()
    g_mean = forecast_trace.posterior['g_forecast'].mean().item()
    sigma_omega_mean = forecast_trace.posterior['sigma_omega_forecast'].mean().item()
    
    # Extract future scores
    future_scores_mean = forecast_trace.posterior['future_scores'].mean(dim=('chain', 'draw')).values
    future_scores_lower = np.percentile(forecast_trace.posterior['future_scores'].values, 2.5, axis=(0, 1))
    future_scores_upper = np.percentile(forecast_trace.posterior['future_scores'].values, 97.5, axis=(0, 1))
    
    # Print key forecast parameters
    print("\nForecast Parameters:")
    print(f"Average Drift Rate (μ): {mu_mean:.6f}")
    print(f"Discrimination Parameter (g): {g_mean:.6f}")
    print(f"Process Noise (σ_ω): {sigma_omega_mean:.6f}")
    
    # Print forecast for specific time points
    print("\nForecast at Selected Time Points:")
    print("Days\tDate\t\tMean Score\t95% CI")
    print("----\t----\t\t----------\t-----")
    
    # Select points to display (e.g., 30, 60, 90 days into the future)
    forecast_days = [30, 60, 90]
    for days in forecast_days:
        if days < len(future_times):
            idx = days
            future_date = first_date + pd.Timedelta(days=int(future_times[idx]))
            date_str = future_date.strftime('%Y-%m-%d')
            mean_score = future_scores_mean[idx] * 100  # Convert back to percentage
            lower = future_scores_lower[idx] * 100
            upper = future_scores_upper[idx] * 100
            print(f"{int(future_times[idx])}\t{date_str}\t{mean_score:.2f}%\t({lower:.2f}%, {upper:.2f}%)")
    
    # Print when the model predicts the score will reach certain thresholds
    thresholds = [0.7, 0.8, 0.9, 0.95]
    print("\nPredicted Time to Reach Score Thresholds:")
    print("Threshold\tApprox. Days\tApprox. Date")
    print("---------\t-----------\t------------")
    
    for threshold in thresholds:
        # Find the first time the mean forecast exceeds the threshold
        exceeds_indices = np.where(future_scores_mean >= threshold)[0]
        if len(exceeds_indices) > 0:
            first_exceed_idx = exceeds_indices[0]
            days_to_threshold = future_times[first_exceed_idx]
            date_to_threshold = first_date + pd.Timedelta(days=int(days_to_threshold))
            date_str = date_to_threshold.strftime('%Y-%m-%d')
            print(f"{threshold*100:.0f}%\t\t{int(days_to_threshold)}\t\t{date_str}")
        else:
            print(f"{threshold*100:.0f}%\t\tNot reached within forecast horizon")

# Example usage
def run_analysis(df, task_id, handle_nan='ignore', forecast_horizon=100):
    """
    Run the complete analysis pipeline.
    
    Parameters:
    -----------
    df : pandas DataFrame
        DataFrame containing the data
    task_id : int
        ID of the task to analyze
    handle_nan : str, optional
        How to handle NaN values: 'ignore' (remove them) or 'zero' (replace with 0)
    forecast_horizon : int, optional
        Number of days to forecast
    """
    # Prepare data
    time_points, y_obs, dates = prepare_data(df, task_id, handle_nan)
    
    # Plot raw data
    plot_raw_data(time_points, y_obs, dates)
    
    # Fit model
    trace = fit_capability_model(time_points, y_obs)
    
    # Plot trace and summary
    plot_trace_and_summary(trace)
    
    # Plot model fit
    plot_model_fit(time_points, y_obs, trace, dates)
    
    # Generate forecast
    forecast_trace, future_times = forecast_capability(trace, time_points, forecast_horizon)
    
    # Plot forecast
    plot_forecast(time_points, y_obs, trace, forecast_trace, future_times, dates)
    
    # Print forecast results
    print_forecast_results(forecast_trace, future_times, dates[0])
    
    return trace, forecast_trace, time_points, y_obs, future_times, dates

# Example of how to use this with your dataframe:



# Run analysis for a specific task, ignoring NaN values
trace, forecast_trace, time_points, y_obs, future_times, dates = run_analysis(
    df, 
    task_id=16246, 
    handle_nan='ignore',  # or 'zero' to replace NaNs with 0
    forecast_horizon=50  
)




forecast_trace, future_times = forecast_capability(trace, time_points, 100)

# Plot forecast
plot_forecast(time_points, y_obs, trace, forecast_trace, future_times, dates)


######
# Simple implementation that works. 
######

times = [ 0,  63,  75,  81, 107, 113, 114, 116, 117]
test_scores = [0.28840782, 0.39331269, 0.53783931, 0.54890993, 0.54407241, 0.59765907,
 0.47089476, 0.65987823, 0.51249848]




T = len(times)

y_obs = np.array(test_scores)
time_points = np.array(times)


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