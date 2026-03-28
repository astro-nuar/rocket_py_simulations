function [x_pred, P_pred, w_m, a_m] = KF_predict(x, w_m, a_m, Q, P, R, dt, k)

    g = [0, 0, -9.81];   % row for consistency

    % --------------------------
    % Extract states
    % --------------------------
    p   = [ x(1), x(2), x(3) ];      % 1x3 row
    v   = [ x(4), x(5), x(6) ];      % 1x3 row
    qk  = [ x(7), x(8), x(9), x(10) ]; % 1x4 row quaternion
    b_a = [ x(11), x(12), x(13) ];   % 1x3 row
    b_g = [ x(14), x(15), x(16) ];   % 1x3 row

    % Convert to column for matrix multiplication
    w_m = w_m(:);      % 3x1
    a_m = a_m(:);      % 3x1
    g_col = g(:);      % 3x1
    p   = p(:);
    v   = v(:);
    qk  = qk(:);
    b_a = b_a(:);
    b_g = b_g(:);

    % --------------------------
    % Bias-correct IMU
    % --------------------------
    a = a_m - b_a;
    w = w_m - b_g;

    R = Ratt(qk);

    p = p + v*dt + (R*a + g_col)*dt^2/2;
    v = v + (R*a + g_col) * dt;

    Omega = [  0      -w(1) -w(2) -w(3);
             w(1)  0        w(3) -w(2);
             w(2) -w(3)  0        w(1);
             w(3)  w(2) -w(1)  0 ];

    qk = qk + 0.5 * Omega * qk * dt;
    qk = qk / norm(qk);

    % Biases stay the same
    b_a = b_a;
    b_g = b_g;

    % Ensure everything is row for x_pred
    p = p(:)';     % force 1x3
    v = v(:)';     % 1x3
    qk = qk(:)';   % 1x4
    b_a = b_a(:)'; % 1x3
    b_g = b_g(:)'; % 1x3

    % Pack predicted nominal state
    x_pred = [p, v, qk, b_a, b_g];   % 1x16 row

    % --------------------------
    % Error-state Jacobian (15x15)
    % --------------------------
    O = zeros(3);
    I = eye(3);

    F = [
        O,  I,    O,         O,     O;
        O,  O, -R*Skew(a), -R,   O;
        O,  O, -Skew(w),    O,  -R;
        O,  O,    O,            O,   O;
        O,  O,    O,            O,   O
    ];

    Phi = eye(15) + F*dt;

    % Noise injection
    G = [
        O,  O, O, O;
        -I, O, O, O;
        O, -I, O, O;
        O,  O, I, O;
        O,  O, O, I
        ];

    % Discrete process noise
    Qd = G * Q * G' * dt;

    % --------------------------
    % Covariance propagation
    % --------------------------
    P_pred = Phi * P * Phi' + Qd;
end

