clear all; close all; clc;
pkg load signal
pkg load statistics
addpath(genpath(pwd))

%% ------------------------
%% Simulation parameterss
%% ------------------------
dt = 0.01;   % time step
n_steps = 7200;  % number of iterations

I = eye(3);

O = zeros(3);

%% ------------------------
%% Process noise parameters
%% ------------------------
eta_a  = 5.5;       % m/s²
eta_g  = 0.11;    % rad/s
eta_ba = 1275.3e-6/dt;    % m/s² bias RW
eta_bg = 0.066e-3/dt;    % rad/s bias RW

%% ------------------------
%% Measurement model (GPS + Barometer)
%% ------------------------
sigma_gps_pos = 2;         % GPS position noise (m)
sigma_gps_vel = 0.5;       % GPS velocity noise (m/s)
sigma_baro = 0.2;          % Barometer noise (m)

%% ------------------------
%% Covariance
%% ------------------------
sigma_theta = pi/180*(5);
sigma_a = 5;
sigma_g = 1;

P = blkdiag(
    100*sigma_gps_pos^2*I,
    sigma_gps_vel^2*I,
    sigma_theta^2*I,
    sigma_a^2*I,
    sigma_g^2*I
);

% --------------------------
% Process noise
% --------------------------
Q = blkdiag( ...
    eta_a^2*I, ...
    eta_g^2*I, ...
    eta_ba^2*I, ...
    eta_bg^2*I
);

% -----------------------
% Measurement Jacobian
% -----------------------
H_baro = [0 0 1, zeros(1,12)];  % 1x15
H = [I, O, O, O, O;     % 3x15
     O, I, O, O, O;     % 3x15
     H_baro];           % 1x15

R_pos = eye(3) * (sigma_gps_pos)^2;
R_vel = eye(3) * (sigma_gps_vel)^2;
R_baro = sigma_baro^2;

R = blkdiag(R_pos, R_vel, R_baro);  % 7×7

% Initialization
baro_meas_all = zeros(n_steps,1);
pos_est   = zeros(n_steps, 3);
vel_est   = zeros(n_steps, 3);
quat_est  = zeros(n_steps, 4);
dq_est  = zeros(n_steps, 3);
ba_est    = zeros(n_steps, 3);
bg_est    = zeros(n_steps, 3);
r_est    = zeros(n_steps, 7);
e_state = zeros(n_steps, 12);

a    = zeros(n_steps, 3);
imu_gyro =  zeros(n_steps, 3);
imu_accel =  zeros(n_steps, 3);
gps = zeros(n_steps, 6);
baro = zeros(n_steps, 1);

%% ------------------------
%% Main KF loop (store results)
%% ------------------------
[a, b_true_a, imu_gyro, b_true_g, imu_accel, b_imu_accel, gps, baro, lat0, lon0, el0] = init(n_steps, dt);

%% ------------------------
%% Initial nominal state (row style)
%% ------------------------
p   = [gps(1, 1), gps(1, 2), gps(1, 3)];    % position (m)
v   = [gps(1, 4), gps(1, 5), gps(1, 6)];    % velocity (m/s)

q = [1, 0, 0, 0];

Rrot = Ratt(q);

b_a = [0, 0, 0];             % accel bias
b_g = [0.03, 0.03, 0.03];          % gyro bias

P_store = zeros(15,15,n_steps);

x = [p, v, q, b_a, b_g];

e =0;

for k = 1:n_steps

    % Predict
    w_m = [ imu_gyro(k, 2), imu_gyro(k, 3), 0 ];
    a_m = [ imu_accel(k, 2), imu_accel(k, 3), imu_accel(k, 4)];

      [x_pred, P_pred, w_m, a_m] = KF_predict(x, w_m, a_m, Q, P, Rrot, dt, k);

      p_true = [gps(k, 1), gps(k, 2), gps(k, 3)];
      v_true = [gps(k, 4), gps(k, 5), gps(k, 6)];
      h_true = baro(k, 1);

      z = [ ...
          p_true(1);
          p_true(2);
          p_true(3);
          v_true(1);
          v_true(2);
          v_true(3);
          h_true
          ];

      % Update
      [x_upd, P_upd, r, e, delta_x] = KF_update(x_pred, P_pred, z, H, R, dt, k);

      % Save state for plotting
      pos_est(k,:)  = x_upd(1:3);
      vel_est(k,:)  = x_upd(4:6);
      quat_est(k,:) = x_upd(7:10);
      ba_est(k,:)   = x_upd(11:13);
      bg_est(k,:)   = x_upd(14:16);
      dq_est(k,:)   = delta_x(7:9)';
      r_est(k,:)   = r';
      e_state(k, :) = e';

      pos_true_all(k,:) = p_true;
      vel_true_all(k,:) = v_true;

      % Save/update for next step
      x = x_upd;
      P = P_upd;
      P_store(:,:,k) = P;
end

%% ------------------------
%% Visualization
%% ------------------------
t = dt*(1:n_steps);

% --- Position ---
figure;
colors = lines(3); % distinct colors for X, Y, Z
subplot(3,1,1);
plot(t,pos_true_all(:,1),'--','Color',colors(1,:),'LineWidth',2); hold on;
plot(t,pos_est(:,1),'-','Color',colors(1,:),'LineWidth',2);
xlabel('Time [s]'); ylabel('X [m]'); grid on; title('Position X'); legend('True','Estimated');

subplot(3,1,2);
plot(t,pos_true_all(:,2),'--','Color',colors(2,:),'LineWidth',2); hold on;
plot(t,pos_est(:,2),'-','Color',colors(2,:),'LineWidth',2);
xlabel('Time [s]'); ylabel('Y [m]'); grid on; title('Position Y');

subplot(3,1,3);
plot(t,pos_true_all(:,3),'--','Color',colors(3,:),'LineWidth',2); hold on;
plot(t,pos_est(:,3),'-','Color',colors(3,:),'LineWidth',2);
xlabel('Time [s]'); ylabel('Z [m]'); grid on; title('Position Z');

% --- Velocity ---
figure;
subplot(3,1,1);
plot(t,vel_true_all(:,1),'--','Color',colors(1,:),'LineWidth',2); hold on;
plot(t,vel_est(:,1),'-','Color',colors(1,:),'LineWidth',2);
xlabel('Time [s]'); ylabel('V_x [m/s]'); grid on; title('Velocity X'); legend('True','Estimated');

subplot(3,1,2);
plot(t,vel_true_all(:,2),'--','Color',colors(2,:),'LineWidth',2); hold on;
plot(t,vel_est(:,2),'-','Color',colors(2,:),'LineWidth',2);
xlabel('Time [s]'); ylabel('V_y [m/s]'); grid on; title('Velocity Y');

subplot(3,1,3);
plot(t,vel_true_all(:,3),'--','Color',colors(3,:),'LineWidth',2); hold on;
plot(t,vel_est(:,3),'-','Color',colors(3,:),'LineWidth',2);
xlabel('Time [s]'); ylabel('V_z [m/s]'); grid on; title('Velocity Z');

% --- Quaternion ---
figure;
colors_quat = lines(4);
for i=1:4
    plot(t,quat_est(:,i),'-','Color',colors_quat(i,:),'LineWidth',2); hold on;
end
xlabel('Time [s]'); ylabel('q'); title('Quaternion Components'); grid on;
legend('q_0','q_1','q_2','q_3');

% --- Accelerometer bias ---
figure;
colors_acc = lines(3);
for i=1:3
    plot(t, ba_est(:,i),'-','Color',colors_acc(i,:),'LineWidth',2);
 hold on;
end
xlabel('Time [s]'); ylabel('Bias [m/s^2]'); title('Accelerometer Bias'); grid on;
legend('b_{ax}','b_{ay}','b_{az}');

% --- Gyroscope bias ---
figure;
colors_gyro = lines(3);
for i=1:3
    plot(t,bg_est(:,i),'-','Color',colors_gyro(i,:),'LineWidth',2); hold on;
end
xlabel('Time [s]'); ylabel('Bias [rad/s]'); title('Gyroscope Bias'); grid on;
legend('b_{gx}','b_{gy}','b_{gz}');

% --- Residual ---
figure;
colors_res = lines(6);

for i = 1:6
    plot(t, e_state(:,i), '-', 'Color', colors_res(i,:), 'LineWidth', 2);
    hold on;
end

N = length(t)-1;

line([t(1) t(N)], [0.995 0.995], 'Color', 'k', 'LineStyle', '--', 'LineWidth', 2);
line([t(1) t(N)], [-0.995 -0.995], 'Color', 'k', 'LineStyle', '--', 'LineWidth', 2);

xlabel('Time [s]');
ylabel('Normalized Residual');
title('Residual (Normalized)');
grid on;
legend('r_x','r_y','r_z','r_{vx}','r_{vy}','r_{vz}');

% --- Covariance diagonals ---
P_diag = zeros(n_steps,15);
for k = 1:n_steps
    P_diag(k,:) = diag(P_store(:,:,k));
end

% Position covariance
figure;
for i=1:3
    plot(t,P_diag(:,i),'-','Color',colors(i,:),'LineWidth',2); hold on;
end
xlabel('Time [s]'); ylabel('Variance [m^2]'); title('Position Covariance');
legend('P_x','P_y','P_z'); grid on;

% Velocity covariance
figure;
for i=1:3
    plot(t,P_diag(:,3+i),'-','Color',colors(i,:),'LineWidth',2); hold on;
end
xlabel('Time [s]'); ylabel('Variance [(m/s)^2]'); title('Velocity Covariance');
legend('P_{vx}','P_{vy}','P_{vz}'); grid on;

% Attitude covariance
figure;
for i=1:3
    plot(t,P_diag(:,6+i),'-','Color',colors_quat(i,:),'LineWidth',2); hold on;
end
xlabel('Time [s]'); ylabel('Variance [rad^2]'); title('Attitude Error Covariance');
legend('\theta_x','\theta_y','\theta_z'); grid on;

% Accelerometer bias covariance
figure;
for i=1:3
    plot(t,P_diag(:,9+i),'-','Color',colors_acc(i,:),'LineWidth',2); hold on;
end
xlabel('Time [s]'); ylabel('Variance [(m/s^2)^2]'); title('Accelerometer Bias Covariance');
legend('b_{ax}','b_{ay}','b_{az}'); grid on;

% Gyro bias covariance
figure;
for i=1:3
    plot(t,P_diag(:,12+i),'-','Color',colors_gyro(i,:),'LineWidth',2); hold on;
end
xlabel('Time [s]'); ylabel('Variance [(rad/s)^2]'); title('Gyro Bias Covariance');
legend('b_{gx}','b_{gy}','b_{gz}'); grid on;
