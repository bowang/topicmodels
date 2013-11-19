[x,y,v] = find(A);

f = fopen('termcount.txt', 'wt');
i = 1;
length = size(x, 1);
while i <= length
  docid = y(i);
  m = nnz(A(:,docid));
  fprintf(f, '%d', m);
  while i <= length && y(i) == docid
    fprintf(f, ' %d:%d', x(i), v(i));
    i = i + 1;
  end
  fprintf(f, '\n');
end
fclose(f);
