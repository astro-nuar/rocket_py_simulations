function [xEast, yNorth, zUp, vxEast, vyNorth, vzUp ] = gnss_receiver(path_sensors, lat, lon, el, lat0, lon0, acc, dt)

  ax = acc(:,1);
  ay = acc(:,2);
  az = acc(:,3);

  N =length(lat);

  x = zeros( N, 1);
  y = zeros( N, 1);
  z = zeros( N, 1);

  xEast = zeros( N, 1);
  yNorth = zeros( N, 1);
  zUp = zeros( N, 1);

  [x, y, z] = geo_to_ecef(lat, lon, el, lat0, lon0);

  x0 = x(1);
  y0 = y(1);
  z0 = z(1);

  [xEast, yNorth, zUp] = ecef_to_enu(x, y, z, x0, y0, z0, lat0, lon0);

  %% ------------------------------------
  %% Please remove before implementation
  filepath = fullfile(path_sensors, "exported_velocity_data.csv");
  velocity = csvread(filepath, 1, 0);

  N = min([
    length(xEast),
    length(yNorth),
    length(zUp),
    rows(velocity)
  ]);

  xEast  = xEast(1:N);
  yNorth = yNorth(1:N);
  zUp    = zUp(1:N);

  vx = zeros(N,1);
  vy = zeros(N,1);
  vz = zeros(N,1);

  vx = velocity(:,2);
  vy = velocity(:,3);
  vz = velocity(:,4);

  vxEast = vx;
  vyNorth = vy;
  vzUp = vz;

  %% Please remove before implementation
  %% ------------------------------------

  ##  fs = 100;      % Sample freq (Hz)
  ##  fc = 50;        % Freq Cutoff (Hz)
  ##  n = 4;          % Order (24 dB/oitava)
  ##
  ##  Wc = fc / (fs / 2);
  ##  [b, a] = butter(n, Wc, 'low');
  ##
  ##  ax = filter(b,a, ax);
  ##  ay = filter(b,a, ay);
  ##  az = filter(b,a, az);
  ##
  ##  vxEast = simpson_rule(ax/9.81-1, dt)
  ##  vyNorth = simpson_rule(ay/9.81-1, dt);
  ##  vzUp = simpson_rule(az/9.81-1, dt);

  % Last element same as previous to keep length N
  %[vxEast, vyNorth, vzUp] = ecef_to_enu(vx, vy, vz, 0, 0, 0, lat0, lon0);

  endfunction
