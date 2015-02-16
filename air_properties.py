import math

def calc_Pws(T):
    c1 = -7.85951783
    c2 = 1.84408259
    c3 = -11.7866497
    c4 = 22.6807411
    c5 = -15.9618719
    c6 = 1.80122502
    v = 1 - (273+T)/647.096 
    Pws = 22064000*math.exp((647.096/(273+T))*(c1*v + c2*v**1.5 + c3*v**3 + c4*v**3.5 + c5*v**4 + c6*v**7.5))
    return Pws

def calcdewpoint_simple(T, RH): 
    #AUGUST-ROCHE-MAGNUS APPROXIMATION
    #VALID FOR T from 0 to 60 C
    #VALID FOR RH from 1 to 100%
    dp = 243.04*(math.log(RH/100)+((17.625*T)/(243.04+T)))/(17.625-math.log(RH/100)-((17.625*T)/(243.04+T)))
    return dp

def calcdewpoint_complex(T, RH):
    if -20 <= T < 50:
        A = 6.116441
	m = 7.591386
	tn = 240.7263
    elif 50 <= T < 100:
        A = 6.004918
	m = 7.337936
	tn = 229.3975
    elif 100 <= T < 150:
        A = 5.856548
	m = 7.27731
	tn = 225.1033
    elif 150 <= T < 200:
        A = 6.002859
	m = 7.290361
	tn = 227.1704
    elif 200 <= T < 350:
        A = 9.980622
	m = 7.388931
	tn = 263.1239
    Pw = (calc_Pws(T)*RH/100.0)/100.0
    td = tn/((m/math.log10(Pw/A))-1)
    return td

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

