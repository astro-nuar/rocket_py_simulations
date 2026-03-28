function [east, north, up] = ecef_to_enu(X, Y, Z, X0, Y0, Z0, lat0, lon0)
    %% Convert ECEF to ENU coordinates relative to reference point

    % Difference from reference
    dX = X - X0;
    dY = Y - Y0;
    dZ = Z - Z0;

    lat0 = deg2rad(lat0);
    lon0 = deg2rad(lon0);

    % Rotation matrix from ECEF to ENU
    sin_lat = sin(lat0);
    cos_lat = cos(lat0);
    sin_lon = sin(lon0);
    cos_lon = cos(lon0);

    R = [-sin_lon,          cos_lon,          0;
         -sin_lat*cos_lon, -sin_lat*sin_lon,  cos_lat;
          cos_lat*cos_lon,  cos_lat*sin_lon,  sin_lat];

    % Transform to ENU
    N = length(dX);
    east = zeros(N, 1);
    north = zeros(N, 1);
    up = zeros(N, 1);

    for i=1:N-1

    enu = R * [dX(i); dY(i); dZ(i)];
    east(i) = enu(1);
    north(i) = enu(2);
    up(i) = enu(3);

    endfor
endfunction
