import sys
import os
import pdb


def MAX(a,b):
    return max(a,b)

def MIN(a,b):
    return min(a,b) 

def ABS(x):
    return abs(x)

def SQRT(x):
    return math.sqrt(x)

def EXPT(x, exp):
    return math.pow(x,exp)

def LN(x):
    return math.log(x)

def LOG(x)
    return math.log(x,10)

def EXP(x):
    return math.exp(x)

def SIN(x):
    return math.sin(x)

def COS(x):
    return math.cos(x)

def TAN(x):
    return math.tan(x)

def ASIN(x):
    return math.asin(x)
 
def ACOS(x):
    return math.acos(x)
 
def ATAN(x):
    return math.atan(x)

def LIMIT(mn, x, mx):
    if x < mn:
        return mn
    if mx < x:
        return mx
    return x

def TRUNC(x):
    return int(x)

def MOD(n,m):
    return n%m

def BOOL_TO_INT(b):
    return int(b)

def INT_TO_DINT(x):
    return x

def REAL_TO_INT(x):
    return int(x)

def TO_SINT(x):
    return int(x)

def TO_INT(x):
    return int(x)

def TO_DINT(x):
    return int(x)

def TO_LINT(x):
    return int(x)

def TO_REAL(x):
    return float(x)

def TO_STRING(x):
    return f"{x}"

def TO_WSTRING(x):
    return f"{x}"

def LEFT(s,L):
    return s[:L]

def RIGHT(s,L):
    n = len(s)
    return s[n-L:]

def MID(s, n, k):
    return s[k:k+n]

def LEN(s):
    return len(s)

def CONCAT(s1,s2):
    return s1+s2

def SEL(b, in0, in1):
    if b:
        return in1
    return in0

def MUX(*args):
    k = args[0]
    return args[k-1]

def MOVE(x):
    return x

def st2py():
    pump1_start = True
    pump1_work = False
    pump1_speed_in = 50
    pump1_speed_out = 50
    pump1_temp = 0
    pump1_pressure = 0
    pump1_valve1 = False
    pump1_valve2 = False
    pump1_valve3 = False
    pump2_start = False
    pump2_work = False
    pump2_speed_in = 50
    pump2_speed_out = 50
    pump2_temp = 0
    pump2_pressure = 0
    pump2_valve1 = False
    pump2_valve2 = False
    pump2_valve3 = False
    pressure_in = 2758
    pressure_out = 6205
    flow_rate_in = 4
    flow_rate_out = 4
    temp_in = 15
    temp_out = 15
    

    while True:
        
        pressure_in = 2758
        pressure_out = 2658
        temp_in = 15
        temp_out = 15
        pump2_temp = 15
        pump1_temp = 15
        flow_rate_in = 4
        
        if pump1_start == True :
            pump1_work = True
            pump1_valve1 = True
            pump1_valve2 = True
            pump1_valve3 = False
            pump1_speed_out = pump1_speed_in
            
            pressure_in = pressure_in - pump1_speed_out
            
            pump1_pressure = pressure_out + 11 * pump1_speed_out
            pressure_out = pump1_pressure - 50
            
            pump1_pressure = pressure_out
            temp_out = temp_out + 1
            pump1_temp = temp_out
            
            
        else:
            pump1_work = False
            pump1_valve1 = False
            pump1_valve2 = False
            pump1_valve3 = True
            pump1_speed_out = 0
            
        
        if pump2_start == True :
            pump2_work = True
            pump2_valve1 = True
            pump2_valve2 = True
            pump2_valve3 = False
            pump2_speed_out = pump2_speed_in
            
            pressure_in = pressure_in - pump2_speed_out
            
            pump2_pressure = pressure_out + 11 * pump2_speed_out
            pressure_out = pump2_pressure - 50
            temp_out = temp_out + 1
            pump2_temp = temp_out
            
            
        else:
            pump2_work = False
            pump2_valve1 = False
            pump2_valve2 = False
            pump2_valve3 = True
            pump2_speed_out = 0
            
        
        flow_rate_in = pressure_in / 90
        flow_rate_out = pressure_out / 90
        
if __name__ == "__main__":
    st2py()

