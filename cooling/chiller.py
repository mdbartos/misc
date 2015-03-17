import pandas as pd
import numpy as np


#Wmu = sigma*(Wout - Win)

Td = np.arange(0,100) #C

c1 = -7.85951783
c2 = 1.84408259
c3 = -11.7866497
c4 = 22.6807411
c5 = -15.9618719
c6 = 1.80122502

v = 1 - (273+Td)/647.096

Pws = 22064000*np.exp((647.096/(273+Td))*(c1*v + c2*v**1.5 + c3*v**3 + c4*v**3.5 + c5*v**4 + c6*v**7.5))

Ptot = 101.325*1000 #N/m2
w_iso = 0.0064

w_sat = (0.622*Pws/(101325-Pws))

psat_w = pd.DataFrame(index=Td, data={'Pws':Pws, 'w_sat':w_sat}).reindex(np.arange(0,100,0.01)).interpolate()

#### SATURATION TEMP AT SPECIFIC HUMIDITY

(psat_w['w_sat']-0.0064).apply(lambda x: abs(x)).idxmin()

#### ITER METHOD TO SOLVE Twet

def calc_Pws(T):
    c1 = -7.85951783
    c2 = 1.84408259
    c3 = -11.7866497
    c4 = 22.6807411
    c5 = -15.9618719
    c6 = 1.80122502
    v = 1 - (273+Td)/647.096
    
    Pws = 22064000*np.exp((647.096/(273+Td))*(c1*v + c2*v**1.5 + c3*v**3 + c4*v**3.5 + c5*v**4 + c6*v**7.5))

    return Pws

def calcdewpoint_simple(T, RH): 
    #AUGUST-ROCHE-MAGNUS APPROXIMATION
    #VALID FOR T from 0 to 60 C
    #VALID FOR RH from 1 to 100%
    dp = 243.04*(math.log(RH/100)+((17.625*T)/(243.04+T)))/(17.625-math.log(RH/100)-((17.625*T)/(243.04+T)))
    return dp

def calcdewpoint_complex(T, RH):


def calcwetbulb(Edifference,Twguess,Ctemp,MBpressure,E,previoussign,incr):
    while (abs(Edifference) > 0.05):
        Ewguess = 6.112 * math.exp((17.67 * Twguess) / (Twguess + 243.5))
        Eguess = Ewguess - MBpressure * (Ctemp - Twguess) * 0.00066 * (1 + (0.00115 * Twguess))
        Edifference = E - Eguess
        if (Edifference == 0):
            break
        else:
            if (Edifference < 0):
                cursign = -1
                if (cursign != previoussign):
                    previoussign = cursign
                    incr = incr/10
                else:
                    incr = incr
            else:
                cursign = 1
                if (cursign != previoussign):
                    previoussign = cursign
                    incr = incr/10
                else:
                    incr = incr
        if (abs(Edifference) <= 0.05):
            break
        else:
            print Twguess, incr
            Twguess = Twguess + incr * previoussign
            print Twguess, incr
    wetbulb = Twguess
    return wetbulb	

def esubx(temp):
    Ex = 6.112 * math.exp((17.67 * temp) / (temp + 243.5))
    return Ex

calcwetbulb(1, 12.0, 15.0, 100.0, esubx(12.0), 1, 10.0)
