import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.stats import norm
# current_directory = os.getcwd()

path_test_data = '../../data/exam_approach/test_results/claude-3-7-sonnet-20250219/'
path_epoch = '../../data/external/epoch_ai/'

category_scores_df = pd.read_csv('../../results/tables/scores_time_category.csv')
category_scores_df['Publication date'] = pd.to_datetime(category_scores_df['Publication date'])
category_scores_df.head()

category = 'business_and_financial_operations'
category = 'management'
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
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.optimize import minimize

class EKFModelWithIrregularTimeSteps:
    """
    Extended Kalman Filter model for latent capability evolution.
    """
    def __init__(self):
        self.params = None
        self.times = None
        self.test_scores = None

    def set_parameters(self, params):
        self.params = params

    def logistic(self, c):
        """Logistic observation function."""
        return 1 / (1 + np.exp(-self.params['g'] * c))

    def logistic_derivative(self, c):
        """Derivative of logistic w.r.t. capability c."""
        s = self.logistic(c)
        return self.params['g'] * s * (1 - s)

    def fit(self, times, test_scores, initial_params=None, optimize=True):
        self.times = np.array(times)
        self.test_scores = np.array(test_scores)
        if initial_params is None:
            initial_params = {
                'mu': 0.1,
                'sigma_omega': 0.05,
                'g': 2.0,
                'sigma_nu': 0.05,
                'initial_c': 0.0,
                'initial_variance': 0.1
            }
        if optimize:
            bounds = {
                'mu': (-1.0, 2.0),
                'sigma_omega': (0.001, 1.0),
                'g': (0.1, 10.0),
                'sigma_nu': (0.001, 1.0),
                'initial_c': (-5.0, 2.0),
                'initial_variance': (0.001, 1.0)
            }
            names = ['mu', 'sigma_omega', 'g', 'sigma_nu', 'initial_c', 'initial_variance']
            x0 = [initial_params[n] for n in names]
            bnds = [bounds[n] for n in names]

            def nll(theta):
                p = {n: v for n, v in zip(names, theta)}
                self.set_parameters(p)
                _, _, ll = self.run_filter()
                return -ll

            res = minimize(nll, x0, bounds=bnds, method='L-BFGS-B')
            opt = {n: v for n, v in zip(names, res.x)}
            self.set_parameters(opt)
            ces, ues, ll = self.run_filter()
            return {
                'parameters': opt,
                'capability_estimates': ces,
                'uncertainty_estimates': ues,
                'log_likelihood': ll,
                'convergence_status': res.success
            }
        else:
            self.set_parameters(initial_params)
            ces, ues, ll = self.run_filter()
            return {
                'parameters': self.params,
                'capability_estimates': ces,
                'uncertainty_estimates': ues,
                'log_likelihood': ll
            }

    def run_filter(self):
        p = self.params
        n = len(self.times)
        # Allocate
        c_est = np.zeros(n)
        P_est = np.zeros(n)
        ll = 0.0
        # Initialization
        c_est[0] = p['initial_c']
        P_est[0] = p['initial_variance']
        # First observation likelihood
        h0 = self.logistic(c_est[0])
        H0 = self.logistic_derivative(c_est[0])
        S0 = H0**2 * P_est[0] + p['sigma_nu']**2
        ll += norm.logpdf(self.test_scores[0], h0, np.sqrt(S0))
        # Iterate
        for t in range(1, n):
            dt = self.times[t] - self.times[t-1]
            # Predict
            c_pred = c_est[t-1] + p['mu'] * dt
            P_pred = P_est[t-1] + p['sigma_omega']**2 * dt
            # Observation linearization
            H = self.logistic_derivative(c_pred)
            h_pred = self.logistic(c_pred)
            S = H**2 * P_pred + p['sigma_nu']**2
            # Likelihood
            ll += norm.logpdf(self.test_scores[t], h_pred, np.sqrt(S))
            # Kalman gain
            K = P_pred * H / S
            # Update
            innovation = self.test_scores[t] - h_pred
            c_est[t] = c_pred + K * innovation
            P_est[t] = (1 - K * H) * P_pred
        return c_est, P_est, ll

    def forecast(self, future_times):
        p = self.params
        last = self.times[-1]
        cur_c = self.cap_est[-1]
        cur_P = self.P_est[-1]
        m = len(future_times)
        f_c = np.zeros(m)
        f_P = np.zeros(m)
        for i, t in enumerate(future_times):
            dt = t - last
            f_c[i] = cur_c + p['mu'] * dt
            f_P[i] = cur_P + p['sigma_omega']**2 * dt
        return f_c, f_P

    def plot_results(self):
        # Run filter
        self.cap_est, self.P_est, _ = self.run_filter()
        # Forecast
        last = self.times[-1]
        dt = (self.times[-1] - self.times[0]) / (len(self.times)-1) if len(self.times)>1 else 1
        fut = np.array([last + (i+1)*dt for i in range(10)])
        f_c, f_P = self.forecast(fut)
        # Plot
        fig, (ax1, ax2) = plt.subplots(2,1, figsize=(10,12))
        # Scores
        ax1.scatter(self.times, self.test_scores, label='Observed')
        fit_scores = self.logistic(self.cap_est)
        ax1.plot(self.times, fit_scores, 'r-', label='Fitted')
        fc_scores = self.logistic(f_c)
        ax1.plot(fut, fc_scores, 'r--', label='Forecast')
        # CI on scores
        ci_scores = 1.96 * np.sqrt((self.logistic_derivative(f_c)**2) * f_P)
        ax1.fill_between(fut, np.clip(fc_scores-ci_scores,0,1), np.clip(fc_scores+ci_scores,0,1), alpha=0.1)
        ax1.set_ylim(0,1); ax1.legend()
        # Capability
        ax2.plot(self.times, self.cap_est, 'g-', label='Estimate')
        ci_cap = 1.96 * np.sqrt(self.P_est)
        ax2.fill_between(self.times, self.cap_est-ci_cap, self.cap_est+ci_cap, alpha=0.2)
        ax2.plot(fut, f_c, 'g--', label='Forecast')
        ci_fc = 1.96 * np.sqrt(f_P)
        ax2.fill_between(fut, f_c-ci_fc, f_c+ci_fc, alpha=0.1)
        ax2.legend(); plt.tight_layout()
        return fig

# Example run (requires `times`, `test_scores`):
initial_params = {
    'mu': 0.005,
    'sigma_omega': 0.05,
    'g': 5.0,
    'sigma_nu': 0.07,
    'initial_c': -0.5,
    'initial_variance': 0.1
}

model = EKFModelWithIrregularTimeSteps()
result = model.fit(times, test_scores, initial_params=initial_params, optimize=True)

print("Estimated parameters:")
for k,v in result['parameters'].items():
    print(f"{k}: {v:.4f}")
print(f"Log-likelihood: {result['log_likelihood']:.4f}")

fig = model.plot_results()
plt.show()





########

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.optimize import minimize

class EKFModelWithIrregularTimeSteps:
    """
    Extended Kalman Filter model for latent capability evolution,
    stores one-step-ahead predictive variances for both states and measurements,
    and plots measurement CIs that include measurement noise.
    """
    def __init__(self):
        self.params = None
        self.times = None
        self.test_scores = None
        # filter outputs
        self.cap_est = None        # posterior state means c_{t|t}
        self.P_est = None          # posterior state variances P_{t|t}
        self.c_pred = None         # prior state means  c_{t|t-1}
        self.P_pred = None         # prior state variances P_{t|t-1}
        self.S_pred = None         # prior measurement variances S_t

    def set_parameters(self, params):
        self.params = params

    def logistic(self, c):
        """Observation function h(c)."""
        return 1 / (1 + np.exp(-self.params['g'] * c))

    def logistic_derivative(self, c):
        """dh/dc at c."""
        s = self.logistic(c)
        return self.params['g'] * s * (1 - s)

    def run_filter(self):
        p = self.params
        n = len(self.times)
        # allocate
        c_est  = np.zeros(n)
        P_est  = np.zeros(n)
        c_pred = np.zeros(n)
        P_pred = np.zeros(n)
        S_pred = np.zeros(n)
        ll      = 0.0

        # --- t = 0 (use prior as predictive) ---
        c_pred[0] = p['initial_c']
        P_pred[0] = p['initial_variance']
        H0         = self.logistic_derivative(c_pred[0])
        S_pred[0]  = H0**2 * P_pred[0] + p['sigma_nu']**2
        # log‐likelihood of first obs
        h0 = self.logistic(c_pred[0])
        ll += norm.logpdf(self.test_scores[0], h0, np.sqrt(S_pred[0]))
        # leave posterior = prior at t=0
        c_est[0] = p['initial_c']
        P_est[0] = p['initial_variance']

        # --- loop for t = 1...n-1 ---
        for t in range(1, n):
            dt = self.times[t] - self.times[t-1]
            # 1) Predict
            c_pr = c_est[t-1] + p['mu'] * dt
            P_pr = P_est[t-1] + p['sigma_omega']**2 * dt
            c_pred[t] = c_pr
            P_pred[t] = P_pr

            # 2) Predict measurement
            H      = self.logistic_derivative(c_pr)
            S      = H**2 * P_pr + p['sigma_nu']**2
            S_pred[t] = S
            h_pr   = self.logistic(c_pr)

            # increment log‐likelihood
            ll += norm.logpdf(self.test_scores[t], h_pr, np.sqrt(S))

            # 3) Update
            K      = P_pr * H / S
            innov  = self.test_scores[t] - h_pr
            c_est[t] = c_pr + K * innov
            P_est[t] = (1 - K * H) * P_pr

        return c_est, P_est, c_pred, P_pred, S_pred, ll

    def fit(self, times, test_scores, initial_params=None, optimize=True):
        """
        Fit EKF to data. Returns:
          - parameters
          - posterior and predictive state estimates & vars
          - predictive measurement variances
          - 95% CI on latent states
          - log-likelihood & convergence
        """
        self.times = np.array(times)
        self.test_scores = np.array(test_scores)

        # default initials
        if initial_params is None:
            initial_params = {
                'mu': 0.1,
                'sigma_omega': 0.05,
                'g': 2.0,
                'sigma_nu': 0.05,
                'initial_c': 0.0,
                'initial_variance': 0.1
            }
        names = ['mu', 'sigma_omega', 'g', 'sigma_nu', 'initial_c', 'initial_variance']

        # optional MLE of noise/drift
        if optimize:
            bounds = {
                'mu': (-1.0, 2.0),
                'sigma_omega': (0.001, 1.0),
                'g': (0.1, 10.0),
                'sigma_nu': (0.001, 1.0),
                'initial_c': (-5.0, 2.0),
                'initial_variance': (0.001, 1.0)
            }
            x0   = [initial_params[n] for n in names]
            bnds = [bounds[n] for n in names]
            def nll(theta):
                p = {n: v for n, v in zip(names, theta)}
                self.set_parameters(p)
                _, _, _, _, _, ll = self.run_filter()
                return -ll

            res = minimize(nll, x0, bounds=bnds, method='L-BFGS-B')
            opt = {n: v for n, v in zip(names, res.x)}
            self.set_parameters(opt)
            converged = res.success
        else:
            opt = initial_params
            self.set_parameters(opt)
            converged = True

        # run filter one final time
        ces, P_est, c_pred, P_pred, S_pred, ll = self.run_filter()

        # store internally
        self.cap_est = ces
        self.P_est   = P_est
        self.c_pred  = c_pred
        self.P_pred  = P_pred
        self.S_pred  = S_pred

        # 95% CI on latent capability
        ci_cap = 1.96 * np.sqrt(P_est)
        lower  = ces - ci_cap
        upper  = ces + ci_cap

        return {
            'parameters': opt,
            'capability_estimates': ces,
            'capability_uncertainties': P_est,
            'capability_ci_lower': lower,
            'capability_ci_upper': upper,
            'predictive_states': c_pred,
            'predictive_state_variances': P_pred,
            'predictive_measurement_variances': S_pred,
            'log_likelihood': ll,
            'convergence_status': converged
        }

    def forecast(self, future_times):
        """
        Open-loop forecast of latent state (and you can get
        forecast measurement CIs similarly in plot_results).
        """
        last = self.times[-1]
        cur_c = self.cap_est[-1]
        cur_P = self.P_est[-1]
        m = len(future_times)
        f_c = np.zeros(m)
        f_P = np.zeros(m)
        for i, t in enumerate(future_times):
            dt = t - last
            f_c[i] = cur_c + self.params['mu'] * dt
            f_P[i] = cur_P + self.params['sigma_omega']**2 * dt
        return f_c, f_P

    def plot_results(self):
        """Plot in‐sample one-step-ahead CIs on measurements + forecast."""
        if self.cap_est is None:
            raise RuntimeError("Call fit() first.")

        # in-sample predicted measurement & CI
        z_pred = self.logistic(self.c_pred)
        ci_z   = 1.96 * np.sqrt(self.S_pred)

        # out-of-sample forecast
        last = self.times[-1]
        dt   = (self.times[-1] - self.times[0]) / max(1, len(self.times)-1)
        fut  = np.array([last + (i+1)*dt for i in range(10)])
        f_c, f_P = self.forecast(fut)
        z_fc     = self.logistic(f_c)
        H_fc     = self.logistic_derivative(f_c)
        S_fc     = H_fc**2 * f_P + self.params['sigma_nu']**2
        ci_fc    = 1.96 * np.sqrt(S_fc)

        # latent capability CI
        ci_cap   = 1.96 * np.sqrt(self.P_est)
        ci_cap_f = 1.96 * np.sqrt(f_P)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))

        # --- measurements with one-step-ahead CI ---
        ax1.fill_between(self.times,
                         np.clip(z_pred - ci_z, 0, 1),
                         np.clip(z_pred + ci_z, 0, 1),
                         alpha=0.2, label='95% one-step-ahead CI')
        ax1.fill_between(fut,
                         np.clip(z_fc - ci_fc, 0, 1),
                         np.clip(z_fc + ci_fc, 0, 1),
                         alpha=0.1, label='95% forecast CI')
        ax1.scatter(self.times, self.test_scores, label='Observed', zorder=3)
        ax1.plot(self.times, z_pred, 'r-', label='Predicted', zorder=2)
        ax1.plot(fut, z_fc,        'r--', label='Forecast',  zorder=2)
        ax1.set_ylim(0, 1)
        ax1.set_title('Test Scores with 95% CI (includes measurement noise)')
        ax1.legend()

        # --- latent capability with posterior & forecast CI ---
        ax2.fill_between(self.times,
                         self.cap_est - ci_cap,
                         self.cap_est + ci_cap,
                         color='green', alpha=0.2, label='95% posterior CI')
        ax2.fill_between(fut,
                         f_c - ci_cap_f,
                         f_c + ci_cap_f,
                         color='green', alpha=0.1, label='95% forecast CI')
        ax2.plot(self.times, self.cap_est, 'g-',  label='Estimate', zorder=2)
        ax2.plot(fut,          f_c,       'g--', label='Forecast',  zorder=2)
        ax2.set_title('Latent Capability with 95% CI')
        ax2.legend()

        plt.tight_layout()
        return fig

# --- Example usage ---
# times = [...]           # your array of time points
# test_scores = [...]     # your observations in [0,1]
# initial_params = {
#     'mu': 0.005,
#     'sigma_omega': 0.05,
#     'g': 5.0,
#     'sigma_nu': 0.07,
#     'initial_c': -0.5,
#     'initial_variance': 0.1
# }
# model = EKFModelWithIrregularTimeSteps()
# result = model.fit(times, test_scores, initial_params=initial_params, optimize=True)
# fig = model.plot_results()
# plt.show()

# Example run (requires `times`, `test_scores`):
initial_params = {
    'mu': 0.005,
    'sigma_omega': 0.05,
    'g': 5.0,
    'sigma_nu': 0.07,
    'initial_c': -0.5,
    'initial_variance': 0.1
}
model = EKFModelWithIrregularTimeSteps()
result = model.fit(times, test_scores, initial_params=initial_params, optimize=True)
print("Estimated parameters:")
for k, v in result['parameters'].items():
    print(f"{k}: {v:.4f}")
lower, upper = result['capability_ci_lower'], result['capability_ci_upper']
print("Capability estimates and 95% CI:")
for t, est, lo, hi in zip(times, result['capability_estimates'], lower, upper):
    print(f"t={t}: {est:.3f} [{lo:.3f}, {hi:.3f}]")
print(f"Log-likelihood: {result['log_likelihood']:.4f}")
fig = model.plot_results()
plt.show()





########
# Plot to data
########

# Initial parameter guesses (no c0)
initial_params = {
    'mu': 0.005,            # Positive but small drift
    'sigma_omega': 0.05,    # Moderate process noise
    'g': 5.0,               # Moderate discrimination parameter
    'sigma_nu': 0.07,       # High measurement noise
    'initial_c': -0.5,      # Starting below logistic midpoint
    'initial_variance': 0.1 # Initial uncertainty
}

# Create and fit the model
model = EnKFModelWithIrregularTimeSteps(ensemble_size=100)
result = model.fit(times, test_scores, initial_params=initial_params, optimize=True)

# Inspect results
print("Estimated parameters:")
for key, val in result['parameters'].items():
    print(f"{key}: {val:.4f}")
print(f"Log-likelihood: {result['log_likelihood']:.4f}")

# Plot results
fig = model.plot_results()
plt.show()



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
