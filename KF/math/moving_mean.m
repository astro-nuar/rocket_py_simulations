function [y]=moving_mean(x)

  N = length(x);
  y = zeros(1, N+4);

  for i=1:N-3
    y(i) = 200 + (x(i)+x(i+1)+x(i+2)+x(i+3))/4;
  endfor

  endfunction
