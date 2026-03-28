function [x_upd, P_upd, r, e, delta_x] = KF_update(x, P_pred, z, H, R, dt, k)

    p   = [ x(1), x(2), x(3) ];      % 1x3 row
    v   = [ x(4), x(5), x(6) ];      % 1x3 row
    qk  = [ x(7), x(8), x(9), x(10) ]; % 1x4 row quaternion
    b_a = [ x(11), x(12), x(13) ];   % 1x3 row
    b_g = [ x(14), x(15), x(16) ];   % 1x3 row

    x_pred = x(:);
    p = p(:)';     % force 1x3
    v = v(:)';     % 1x3
    qk = qk(:)';   % 1x4
    b_a = b_a(:)'; % 1x3
    b_g = b_g(:)'; % 1x3

    h = [ p(:); v(:); p(3)];

    r = z - h;

    K = KF_Gain(P_pred, H, R);

    delta_x = K * r;

    if rem(dt*k, 0.04)==0
    % position
    p = p + delta_x(1:3)';

    % Velocity
    v = v + delta_x(4:6)';
    endif

    theta = norm(delta_x(7:9));
    if theta > 0.1
      delta_theta = delta_x(7:9) * 0.1 / theta;
    else
      delta_theta = delta_x(7:9);
    end

    % Small-angle quaternion update
    dq = [1, 0.5*delta_x(7:9)'];   % 1x4 row
    dq = dq / norm(dq);
    qk = quatmulti(dq, qk);
    qk = qk / norm(qk);

    % Accelerometer bias
    b_a = b_a + delta_x(10:12)';

    % Gyro bias
    b_g = b_g + delta_x(13:15)';

    % --------------------------
    % Updated covariance
    % --------------------------
    P_upd = (eye(15) - K*H) * P_pred * (eye(15) - K*H)' + K*R*K';

    qk = qk';

    v_m = (z(1:3)' - p) /dt;
    alpha = 1;
    v = alpha*v + (1-alpha)*(v_m);

    e = [delta_x(1:3)', delta_x(4:6)', delta_x(10:12)', delta_x(13:15)'];

    % --------------------------
    % Pack updated nominal state
    % --------------------------
    x_upd = [p, v, qk, b_a, b_g];
end
