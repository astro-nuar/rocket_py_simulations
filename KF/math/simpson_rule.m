function [y]=simpson_rule(x, dt)

  N = length(x);
  y = zeros(1, N);

  for i=4:int16(N/2)

    y(i) = x(1)*dt + dt/3 *( x(i-2)+ 4*x(i-1) + x(i) );

  endfor

  endfunction
