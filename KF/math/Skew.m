function S = Skew(w)

    wx = w(1);
    wy = w(2);
    wz = w(3);

    S = [  0   -wz   wy;
          wz     0  -wx;
         -wy    wx    0 ];

end

