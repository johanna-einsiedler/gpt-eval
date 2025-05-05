import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.stats import norm

import pymc as pm
import arviz as az
# current_directory = os.getcwd()

path_test_data = '../../data/exam_approach/test_results/claude-3-7-sonnet-20250219/'
path_epoch = '../../data/external/epoch_ai/'

category_scores_df = pd.read_csv('../../results/tables/scores_time_category.csv')
category_scores_df['Publication date'] = pd.to_datetime(category_scores_df['Publication date'])
category_scores_df.head()

category = 'business_and_financial_operations'

df = category_scores_df[category_scores_df['category'] == category]

df = df[~(df['display_name'] == 'Claude 3.5 Haiku')]

df = df[['Publication date', 'mean_score']]
df.plot(x='Publication date', y='mean_score', kind='scatter')
df

# Ensure the 'Publication date' column is in datetime format
df['Publication date'] = pd.to_datetime(df['Publication date'])

# Sort the DataFrame by 'Publication date'
df = df.sort_values(by='Publication date')

# Find the earliest date in the dataset
start_date = df['Publication date'].min()

# Calculate the time step as the number of weeks since the start date
df['time_step'] = ((df['Publication date'] - start_date) / pd.Timedelta(weeks=1)).astype(int)

# Extract the time steps and mean scores as numpy arrays
times = df['time_step'].to_numpy()
test_scores = df['mean_score'].to_numpy()/100  # Normalize scores to [0, 1]

print("Time steps:", times)
print("Test scores:", test_scores)



class EnKFModelWithIrregularTimeSteps:
    def __init__(self, ensemble_size=100):
        """
        Initialize the Ensemble Kalman Filter model.
        
        Parameters:
        -----------
        ensemble_size : int
            Number of ensemble members.
        """
        self.ensemble_size = ensemble_size
        self.params = None
        self.ensemble = None
        self.times = None
        self.test_scores = None
        
    def set_parameters(self, params):
        """
        Set model parameters.
        
        Parameters:
        -----------
        params : dict
            Dictionary containing model parameters:
            - mu: Drift term (average rate of technological improvement)
            - sigma_omega: Process noise standard deviation
            - g: Discrimination parameter for logistic function
            - c0: Reference capability level
            - sigma_nu: Measurement noise standard deviation
            - initial_c: Initial capability estimate
            - initial_variance: Initial variance estimate
        """
        self.params = params
        
    def initialize_ensemble(self):
        """Initialize the ensemble with random samples."""
        self.ensemble = np.random.normal(
            self.params['initial_c'], 
            np.sqrt(self.params['initial_variance']), 
            self.ensemble_size
        )
        
    def logistic_function(self, c):
        """
        Apply logistic function to transform capability to test score.
        
        Parameters:
        -----------
        c : float or array
            Capability level(s)
            
        Returns:
        --------
        float or array
            Test score(s) between 0 and 1
        """
        return 1 / (1 + np.exp(-self.params['g'] * (c - self.params['c0'])))
        
    def fit(self, times, test_scores, initial_params=None, optimize=True):
        """
        Fit the model to observed test scores.
        
        Parameters:
        -----------
        times : array-like
            Time points of observations (can be unequally spaced)
        test_scores : array-like
            Observed test scores at corresponding time points
        initial_params : dict, optional
            Initial parameter values for optimization
        optimize : bool
            Whether to optimize parameters or use initial_params directly
            
        Returns:
        --------
        dict
            Estimated parameters and log-likelihood
        """
        self.times = np.array(times)
        self.test_scores = np.array(test_scores)
        
        # Default initial parameters if not provided
        if initial_params is None:
            initial_params = {
                'mu': 0.1,              # Small positive drift
                'sigma_omega': 0.05,    # Small process noise
                'g': 2.0,               # Moderate discrimination
                'c0': 0.0,              # Reference level
                'sigma_nu': 0.05,       # Small measurement noise
                'initial_c': 0.0,       # Start at reference level
                'initial_variance': 0.1 # Moderate initial uncertainty
            }
        
        if optimize:
            # Parameter bounds for optimization (min, max)
            bounds = {
                'mu': (-1.0, 2.0),
                'sigma_omega': (0.001, 1.0),
                'g': (0.1, 10.0),
                'c0': (-2.0, 2.0),
                'sigma_nu': (0.001, 1.0),
                'initial_c': (-5.0, 2.0),
                'initial_variance': (0.001, 1.0)
            }
            
            # Pack parameters for optimization
            param_names = ['mu', 'sigma_omega', 'g', 'c0', 'sigma_nu', 'initial_c', 'initial_variance']
            initial_values = [initial_params[name] for name in param_names]
            param_bounds = [bounds[name] for name in param_names]
            
            # Define negative log-likelihood function for minimization
            def neg_log_likelihood(theta):

                # np.random.seed(12345)
                params_dict = {name: val for name, val in zip(param_names, theta)}
                self.set_parameters(params_dict)
                _, _, log_likelihood = self.run_filter()
                return -log_likelihood
                
            # Optimize parameters
            result = minimize(
                neg_log_likelihood,
                initial_values,
                bounds=param_bounds,
                method='L-BFGS-B'
            )
            
            # Set optimized parameters
            optimized_params = {name: val for name, val in zip(param_names, result.x)}
            self.set_parameters(optimized_params)
            
            # Run filter with optimized parameters
            capability_estimates, uncertainty_estimates, log_likelihood = self.run_filter()
            
            return {
                'parameters': optimized_params,
                'capability_estimates': capability_estimates,
                'uncertainty_estimates': uncertainty_estimates,
                'log_likelihood': log_likelihood,
                'convergence_status': result.success
            }
        else:
            # Use provided parameters without optimization
            self.set_parameters(initial_params)
            capability_estimates, uncertainty_estimates, log_likelihood = self.run_filter()
            
            return {
                'parameters': self.params,
                'capability_estimates': capability_estimates,
                'uncertainty_estimates': uncertainty_estimates,
                'log_likelihood': log_likelihood
            }
            
    def run_filter(self):
        """
        Run the Ensemble Kalman Filter algorithm.
        
        Returns:
        --------
        tuple
            (capability_estimates, uncertainty_estimates, log_likelihood)
        """
        if self.params is None:
            raise ValueError("Parameters must be set before running the filter")
        
        # Initialize ensemble
        self.initialize_ensemble()
        
        # Arrays to store results
        n_steps = len(self.times)
        capability_estimates = np.zeros(n_steps)
        uncertainty_estimates = np.zeros(n_steps)
        log_likelihood = 0.0
        
        # For the first point, just use the initial ensemble
        capability_estimates[0] = np.mean(self.ensemble)
        uncertainty_estimates[0] = np.var(self.ensemble)
        
        # Predicted measurement for first point
        predicted_measurements = self.logistic_function(self.ensemble) + np.random.normal(
            0, self.params['sigma_nu'], self.ensemble_size
        )
        mean_predicted_measurement = np.mean(predicted_measurements)
        measurement_variance = np.var(predicted_measurements) + self.params['sigma_nu']**2
        
        # Likelihood of first observation
        log_likelihood += norm.logpdf(
            self.test_scores[0], 
            mean_predicted_measurement, 
            np.sqrt(measurement_variance)
        )
        
        # For time points 1 to n-1
        for t in range(1, n_steps):
            # Time interval since last observation
            delta_t = self.times[t] - self.times[t-1]
            
            # --- Forecast Step ---
            # Propagate ensemble forward in time with scaled drift and noise
            scaled_mu = self.params['mu'] * delta_t
            scaled_sigma_omega = self.params['sigma_omega'] * np.sqrt(delta_t)
            
            # State transition with time-scaled drift and noise
            self.ensemble = self.ensemble + scaled_mu + np.random.normal(
                0, scaled_sigma_omega, self.ensemble_size
            )
            
            # Forecast statistics
            forecast_mean = np.mean(self.ensemble)
            forecast_variance = np.var(self.ensemble)
            
            # --- Measurement Update Step ---
            # Generate predicted measurements
            predicted_measurements = self.logistic_function(self.ensemble) + np.random.normal(
                0, self.params['sigma_nu'], self.ensemble_size
            )
            mean_predicted_measurement = np.mean(predicted_measurements)
            
            # Calculate covariances
            P_yy = np.var(predicted_measurements) + self.params['sigma_nu']**2
            
            # Cross-covariance between state and measurement
            P_xy = np.mean((self.ensemble - forecast_mean) * (predicted_measurements - mean_predicted_measurement))
            
            # Kalman gain
            kalman_gain = P_xy / P_yy
            
            # Update ensemble members
            innovation = self.test_scores[t] - predicted_measurements
            self.ensemble = self.ensemble + kalman_gain * innovation
            
            # Store estimates
            capability_estimates[t] = np.mean(self.ensemble)
            uncertainty_estimates[t] = np.var(self.ensemble)
            
            # Update log-likelihood
            log_likelihood += norm.logpdf(
                self.test_scores[t], 
                mean_predicted_measurement, 
                np.sqrt(P_yy)
            )
            
        return capability_estimates, uncertainty_estimates, log_likelihood
        
    def forecast(self, forecast_times):
        """
        Forecast future capability and uncertainty.
        
        Parameters:
        -----------
        forecast_times : array-like
            Future time points to forecast
            
        Returns:
        --------
        tuple
            (forecasted_capabilities, forecast_uncertainties)
        """
        if self.ensemble is None:
            raise ValueError("Model must be fitted before forecasting")
            
        # Convert to numpy array if not already
        forecast_times = np.array(forecast_times)
        
        # Last observed time and current ensemble state
        last_time = self.times[-1]
        current_capability = np.mean(self.ensemble)
        current_uncertainty = np.var(self.ensemble)
        
        # Arrays for forecast results
        n_forecast = len(forecast_times)
        forecasted_capabilities = np.zeros(n_forecast)
        forecast_uncertainties = np.zeros(n_forecast)
        
        for i, time in enumerate(forecast_times):
            # Time difference from last observation
            delta_t = time - last_time
            
            # Forecast capability with drift
            forecasted_capabilities[i] = current_capability + self.params['mu'] * delta_t
            
            # Forecast uncertainty (grows linearly with time)
            forecast_uncertainties[i] = current_uncertainty + self.params['sigma_omega']**2 * delta_t
            
        return forecasted_capabilities, forecast_uncertainties
        
        
    def plot_results(self):
        """
        Plot model results with test scores and forecasts.
        
        Top plot shows test scores with fit and forecast.
        Bottom plot shows the estimated and forecasted capabilities.
        """
        if not hasattr(self, 'times') or self.times is None:
            raise ValueError("Model must be fitted before plotting")
            
        fig, axes = plt.subplots(2, 1, figsize=(10, 12))
        
        # Get capability estimates and uncertainties from the filter
        capability_estimates, uncertainty_estimates, _ = self.run_filter()
        
        # Generate forecast times (10 steps ahead)
        last_time = self.times[-1]
        time_step = 1  # Use 1 as default time step
        if len(self.times) > 1:
            # Calculate average time step from data
            time_step = (self.times[-1] - self.times[0]) / (len(self.times) - 1)
        
        forecast_times = np.array([last_time + (i+1)*time_step for i in range(10)])
        forecasted_capabilities, forecast_uncertainties = self.forecast(forecast_times)
        
        # Calculate forecasted test scores using the logistic function
        forecasted_test_scores = self.logistic_function(forecasted_capabilities)
        
        # Plot 1: Test scores - observed, fitted, and forecast
        ax1 = axes[0]
        
        # Plot observed test scores
        ax1.scatter(self.times, self.test_scores, color='blue', label='Observed Test Scores', zorder=3)
        
        # Plot fitted test scores (transform capability estimates)
        fitted_test_scores = self.logistic_function(capability_estimates)
        ax1.plot(self.times, fitted_test_scores, 'r-', label='Fitted Test Scores', zorder=2)
        
        # Plot forecasted test scores
        ax1.plot(forecast_times, forecasted_test_scores, 'r--', label='Forecasted Test Scores')
        
        # Add confidence intervals for the forecasted test scores
        # Using delta method to approximate variance of transformed random variable
        logistic_derivative = lambda x: self.params['g'] * np.exp(-self.params['g']*(x-self.params['c0'])) / (1 + np.exp(-self.params['g']*(x-self.params['c0'])))**2
        forecast_score_variance = [(logistic_derivative(c)**2 * var) for c, var in zip(forecasted_capabilities, forecast_uncertainties)]
        forecast_score_ci = 1.96 * np.sqrt(forecast_score_variance)
        
        ax1.fill_between(
            forecast_times,
            np.clip(forecasted_test_scores - forecast_score_ci, 0, 1),  # Clip to [0,1]
            np.clip(forecasted_test_scores + forecast_score_ci, 0, 1),  # Clip to [0,1]
            color='red', alpha=0.1, label='95% Forecast CI'
        )
        
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Test Score')
        ax1.set_title('Test Scores: Observed, Fitted, and Forecast')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 1.05)  # Test scores are between 0 and 1
        
        # Plot 2: Capabilities - estimated and forecast
        ax2 = axes[1]
        
        # Plot capability estimates
        ax2.plot(self.times, capability_estimates, 'g-', label='Estimated Capability', zorder=2)
        
        # Add confidence intervals for capability estimates
        capability_ci = 1.96 * np.sqrt(uncertainty_estimates)
        ax2.fill_between(
            self.times, 
            capability_estimates - capability_ci,
            capability_estimates + capability_ci,
            color='green', alpha=0.2, label='95% Confidence Interval'
        )
        
        # Plot forecasted capabilities
        ax2.plot(forecast_times, forecasted_capabilities, 'g--', label='Forecasted Capability')
        
        # Add confidence intervals for forecasted capabilities
        forecast_cap_ci = 1.96 * np.sqrt(forecast_uncertainties)
        ax2.fill_between(
            forecast_times,
            forecasted_capabilities - forecast_cap_ci,
            forecasted_capabilities + forecast_cap_ci,
            color='green', alpha=0.1, label='95% Forecast CI'
        )
        
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Capability')
        ax2.set_title('Capability Estimates and Forecast')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig

########
# Plot to data
########

# Initial parameter guesses
initial_params = {
    'mu': 0.005,            # Positive but small drift
    'sigma_omega': 0.05,    # Moderate process noise
    'g': 5.0,               # Moderate discrimination parameter
    'c0': 0.0,              # Reference level (score of 0.5)
    'sigma_nu': 0.07,       # High measurement noise
    'initial_c': -0.5,      # Starting below reference level
    'initial_variance': 0.1 # Initial uncertainty
}
# Create and fit the model
model = EnKFModelWithIrregularTimeSteps(ensemble_size=100)
result = model.fit(times, test_scores, initial_params=initial_params, optimize=True)

result.keys()
result['parameters']
# Print estimated parameters
print("Estimated parameters:")
for key, value in result['parameters'].items():
    print(f"{key}: {value:.4f}")

print(f"Log-likelihood: {result['log_likelihood']:.4f}")

# Plot results - the new plotting function automatically handles forecasting
fig = model.plot_results()

plt.show()
