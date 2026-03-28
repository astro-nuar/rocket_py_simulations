function [x, y, z] = enu_to_ecef(east, north, up, x0, y0, z0, lat0, lon0)
    %% Convert ENU coordinates back to ECEF relative to a reference point
    lat0 = deg2rad(lat0);
    lon0 = deg2rad(lon0);

    % Rotation matrix from ENU to ECEF (transpose of ECEF->ENU)
    sin_lat = sin(lat0);
    cos_lat = cos(lat0);
    sin_lon = sin(lon0);
    cos_lon = cos(lon0);

    R = [-sin_lon,          -sin_lat*cos_lon,  cos_lat*cos_lon;
          cos_lon,          -sin_lat*sin_lon,  cos_lat*sin_lon;
          0,                 cos_lat,          sin_lat];

    N = length(east);
    x = zeros(N, 1);
    y = zeros(N, 1);
    z = zeros(N, 1);

    for i = 1:N
        ecef_offset = R * [east(i); north(i); up(i)];

        x(i) = x0 + ecef_offset(1);
        y(i) = y0 + ecef_offset(2);
        z(i) = z0 + ecef_offset(3);
    end
endfunction

