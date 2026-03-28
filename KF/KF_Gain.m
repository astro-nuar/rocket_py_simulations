function K = KF_Gain(P_pred, C, R)
    K = P_pred * C' / (C * P_pred * C' + R);
end
