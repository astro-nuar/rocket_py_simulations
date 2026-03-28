function M = Ratt(q)

    qw = q(1);
    q1 = q(2);
    q2 = q(3);
    q3 = q(4);

    qv = [q1; q2; q3];

    M = (qw^2 - qv.'*qv)*eye(3) ...
        + 2*(qv*qv.') ...
        + 2*qw*Skew(qv);

end

