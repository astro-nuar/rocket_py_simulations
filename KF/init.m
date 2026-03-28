function [high_g_accel, high_g_bias, imu_gyro, imu_gyro_bias, imu_accel, imu_accel_bias, gps, baro, lat0, lon0, el0] = init(n_steps, dt)

  % Path to sensor data
  path_sensors = "C:\\Users\\Claudio Manuel\\Desktop\\NOVA-FCT\\ASTRO\\KF\\sensors_data";

  % Filenames
  high_g_file    = "exported_Accelerometer_0_data.csv";
  imu_accel_file = "exported_Accelerometer_1_data.csv";
  imu_gyro_file  = "exported_Gyroscope_2_data.csv";
  gps_file_name  = "exported_GnssReceiver_data.csv";
  baro_file_name = "exported_Barometer_data.csv";

  high_accel_bias_file = "exported_acc_bias_0_data.csv";
  imu_accel_bias_file = "exported_acc_bias_1_data.csv";
  imu_gyro_bias_file = "exported_gyro_bias_data.csv";

  % 3-axis sensors
  three_axis_files = {high_g_file, imu_accel_file, imu_gyro_file, high_accel_bias_file, imu_accel_bias_file, imu_gyro_bias_file};
  three_axis_sensors = cell(1, length(three_axis_files));

  % Load 3-axis sensors
  for i = 1:length(three_axis_files)

     filepath = fullfile(path_sensors, three_axis_files{i});

     three_axis_sensors{i} = csvread(filepath, 1, 0);  % Skip header

  endfor

  high_g_accel    = three_axis_sensors{1};
  imu_accel       = three_axis_sensors{2};
  imu_gyro        = three_axis_sensors{3};
  high_g_bias     = three_axis_sensors{4};
  imu_accel_bias  = three_axis_sensors{5};
  imu_gyro_bias   = three_axis_sensors{6};

  % Load GPS
  gps_pos_wgs = csvread(fullfile(path_sensors, gps_file_name), 1, 0);

  lat = gps_pos_wgs(:,2);
  lat0 = lat(1);
  lon = gps_pos_wgs(:,3);
  lon0 = lon(1);
  el = gps_pos_wgs(:,4);
  el0 = el(1);
  N = length(lat);

  x = zeros( N, 1);
  y = zeros( N, 1);
  z = zeros( N, 1);
  vx = zeros( N, 1);
  vy = zeros( N, 1);
  vz = zeros( N, 1);

  [x, y, z, vx, vy, vz] = gnss_receiver(path_sensors, lat, lon, el, lat0, lon0, imu_accel, dt);

  gps = [x, y, -z, vx, vy, vz];

  % Load Barometer
  baro_pressure = csvread(fullfile(path_sensors, baro_file_name), 1, 0);

  baro = std_atmosphere_model(baro_pressure(:,2));

endfunction
