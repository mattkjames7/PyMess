#include "gamma.h"

/*this is the Spouge gamma function code stolen from rosettacode.org*/
double GammaSpouge(double z) {
	
	double c[A];
	double accm;
	int k;
	double k_fact = 1.0;
	
	c[0] = sqrt(2.0*M_PI);
	for (k=1;k<A;k++) {
		c[k] = exp(A-k) * pow(A-k,k-0.5) / k_fact;
		k_fact *= -k;
	}
	
	accm = c[0];
	for (k=1;k<A;k++) {
		accm += c[k]/(z+k);
	}
	accm *= exp(-(z+A)) * pow(z+A,z+0.5);
	return accm/z;
}
