#include <stdio.h>

int main(void) {
  int n, i, fact;

  printf("Positive integer:");
  n = 10;
  fact = 1;
  scanf("%d", &n);
  
  for(i = 1; i<=n; i++) 
    fact = fact*i;

  printf("Factorial %d = %d\n", n, fact);
}
