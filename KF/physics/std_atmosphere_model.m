function [hagl]=std_atmosphere_model(P)

  # sea level info
  T0 =288.15;
  P0 =101325;
  L0=0.0065;

  g = 9.8;        # [m/s^2]
  M = 0.0289644;  # [kg/mol]
  R = 8.31447;     # [J/molk]

  hagl = T0*( (P/P0).^(R*L0/(g*M)) -1)/L0;

  endfunction
