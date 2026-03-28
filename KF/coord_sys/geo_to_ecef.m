function [x, y, z] = geo_to_ecef(lat, lon, el, lat0, lon0)

    % Earth properties (WGS84)
    a = 6378137; # [m]
    e2 = 0.00669437999014;

    % Convert lat/lon to local Cartesian coordinates (meters)
    % Make sure lat/lon are in radians
    lat  = deg2rad(lat);
    lon  = deg2rad(lon);
    lat0 = deg2rad(lat0);
    lon0 = deg2rad(lon0);

    Ncurv = a ./ sqrt(1 - e2 .* sin(lat).^2);
    h = el;

    N = length(lat);

    x = zeros( N, 1);
    y = zeros( N, 1);
    z = zeros( N, 1);

    for i=1:N

      x(i) = (Ncurv(i) + h(i)) * cos(lat(i)) * cos(lon(i));
      y(i) = (Ncurv(i) + h(i)) * cos(lat(i)) * sin(lon(i));
      z(i) = ((1 - e2) * Ncurv(i) + h(i)) * sin(lat(i));
  endfor

endfunction
