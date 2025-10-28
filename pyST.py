import argparse
import re
import pdb
import sys
import math
from pathlib import Path

st_file = ''
python_file = ''
mpc = None

functions = '''
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
'''


var_types = ('BOOL', \
    'SINT', 'INT', 'DINT', 'LINT', \
    'USINT', 'UINT', 'UDINT', 'ULINT', \
    'BYTE', 'WORD', 'DWORD', 'LWORD', \
    'REAL', 'LREAL', \
    'STRING', 'WSTRING', \
    'TIME', 'TOD', 'DATE', 'DTL')

fb_types = ('TON', 'TOF', 'TP', 'CTU', 'CTD', 'PULSE_GEN', \
    'CTUD', 'RS', 'SR', 'F_TRIG', 'R_TRIG')

def getArgs():
    global st_file, python_file, mpc

    parser = argparse.ArgumentParser()
    parser.add_argument(u'-st', metavar = u'name of file with ST code',
                        dest=u'st_file', required=True)

    parser.add_argument(u'-mpc', metavar = u'milliseconds per cycle',
                        dest=u'mpc', required=True)

    if len(sys.argv) < 2:
        print("Useage ST2pyFB.py -st ST-File -mpc milliseconds-per-cycle")
        exit(1)

    args = parser.parse_args(sys.argv[1:])
    st_file = args.st_file

    mpc = args.mpc

    try:
        with open(st_file, 'r') as rf:
            x=1
    except:
        print(f"error: unable to open {st_file}")
        exit(1)

    file_path = Path(st_file).stem
    python_file   = file_path + '.py' 


class Variable:
    def __init__(self, name, vtype, value, vclass, location):
        self.name = name.upper()
        self.type = vtype.upper()
        self.type = self.type.replace(';','')
        self.value = value
        if value is not None:
            self.value = self.value.replace(';','')
        self.vclass = vclass
        self.location = location

class ConvertorApp:
    def __init__(self, st_file):
        self.st_file = st_file

    def convert(self):
        with open(self.st_file,'r') as rf:
            st_code = rf.read()

        converted_code = self.convert_st_to_python(st_code)
        return converted_code

    def convert_st_to_python(self, st_code):
        variables = {}

        # get rid of configuration block if present
        config_pattern = r"CONFIGURATION(.*?)END_CONFIGURATION"
        config_match = re.search(config_pattern, st_code, re.DOTALL)
        if config_match:
            st_code = re.sub(config_pattern, '', st_code, flags=re.DOTALL)

        # scrap off PROGRAM and END_PROGRAM
        st_code = st_code.replace('END_PROGRAM','')

        first = st_code.find('PROGRAM')
        last  = st_code[first:].find('\n')
        if first>0:
            front = st_code[:first-1]
        else:
            front = ''
        back  = st_code[last+1:]
        st_code = front+back

        # replace line by line comment
        lines = st_code.split('\n')
        trans = []
        for line in lines: 
            if line.find('(*') > -1:
                first = line.find('(*')
                last  = line.find('*)')
                line = line[:first]+'//'+line[first+2:last] 
            trans.append(line)

        st_code = '\n'.join(trans)
 
        var_blk_desc = (\
            ('all', r"VAR\s+(.*?)END_VAR"),\
            ('input', r"VAR_INPUT (.*?)END_VAR"), \
            ('output', r"VAR_OUTPUT (.*?)END_VAR"), \
            ('in_out', r"VAR_IN_OUT (.*?)END_VAR"), \
            ('global', r"VAR_GLOBAL (.*?)END_VAR"), \
            ('external', r"VAR_EXTERNAL (.*?)END_VAR"), \
            ('temp', r"VAR_TEMP (.*?)END_VAR"))

        variable_class = {} 
        ret_code = ""
        python_code = ""
        
        for var_class, var_declaration_pattern in var_blk_desc:
            variable_class[var_class] = []

            # for each variable block type find all instances
            var_blks = re.finditer(var_declaration_pattern, st_code, re.IGNORECASE | re.DOTALL)
            holding = []
            for var_blk in var_blks:
                holding.append(var_blk)     
        
            var_blks = reversed(holding)
            for var_declaration in var_blks:    
                (start, end) = var_declaration.span()
                remainder = st_code[end+1:]

                var_blk = var_declaration.group(1)
 
                trans_lines = ['//START_BLK']
                var_lines = var_blk.split('\n')
                for line in var_lines:
                    if len(line)>0:
                        line = line.strip()
                        if line.startswith('//'):
                            trans_lines.append(line)
                            continue

                        # look for initial assignments 
                        split_line = line.split(":=", maxsplit=1)
                        if len(split_line) > 1:

                            # var_value is the initialization value
                            var_first, var_value = split_line
                            var_value = var_value.strip()
                            if var_value.find('//') > -1:
                                var_value = var_value[:var_value.find('//')]

                            var_name, var_type = var_first.split(":", maxsplit=1)

                            var_type = var_type.replace(';','')
                            var_type = var_type.strip()
                            if var_type.find('//') > -1:
                                var_type = var_type[:var_type.find('//')]
                            var_type = var_type.strip()

                            var_name = var_name.strip()

                            var_loc = None
                            if var_name.find(' AT %') > -1:
                                idx = var_name.find(' %') 
                                var_loc = var_name[idx+2:].strip() 
                                var_name = var_name[:var_name.find(' AT %')].strip()
                             
                            vname_list = var_name.split(',')
                            
                            for vname in vname_list:   
                                # variables indexed by name gives the variable type, which might be a function block
                                variables[vname] = Variable(vname, var_type, var_value, var_class, var_loc)

                            var_name = var_name.replace(',','=')

                            new_line = f"{var_name} = {var_value}"

                            if line.find('//') > -1:
                                new_line = new_line + line[line.find('//'):]

                            trans_lines.append(new_line)

                        else:
                            var_value = None
                            var_declaration = split_line[0]
                            if var_declaration.find(':') > -1:
                                var_name, var_type = var_declaration.split(":", maxsplit=1)

                                var_type = var_type.replace(';','')
                                if var_type.find('//') > -1:
                                    var_type = var_type[:var_type.find('//')]
                                var_type = var_type.strip()

                                var_name = var_name.strip()
                                var_loc = None
                                if var_name.find(' AT %') > -1:
                                    idx = var_name.find(' %') 
                                    var_loc = var_name[idx+3:].strip() 

                                # if the type is a function block then should the value
                                # be a call to an instance of it?
                                var_inst = None
                                if var_type not in var_types:
                                    # for a function block call an empty constructor
                                    var_inst = f"{var_type}()"
                                    var_value = var_inst
 
                                if var_type not in var_types:
                                    print(f"Variable {var_name} with unrecognized type {var_type}")
                                var_value = None

                                if var_inst is None:
                                    variables[var_name] = Variable(var_name, var_type, None, var_class, var_loc)
                                    variable_class[var_class].append( variables[var_name] )
                                    var_name = var_name.replace(',','=')
                                    new_line = f"{var_name} = {var_value}"
                                else:
                                    variables[var_name] = Variable(var_name, var_type, var_inst, var_class, var_loc)
                                    variable_class[var_class].append( variables[var_name] )
                                    new_line = f"{var_name} = {var_inst}"

                            else:
                                new_line = split_line[0]

                            trans_lines.append(new_line)

                trans_lines.append('//END_BLK\n')
                trans_blk = '\n'.join(trans_lines)+'\n//START_BLK\n//START_MAIN\n//START_BLK\n'
                #replace the variable block in place

                st_code = st_code[:start]+trans_blk+st_code[end+1:]

        end_var = st_code.find('//START_BLK\n//START_MAIN')
        var_blks = st_code[:end_var]+'//START_BLK\n//START_MAIN\n//START_BLK\n'

        main_prg = remainder

        # convert the rest of it
        main_prg = self.convert_segment(variables, main_prg)
        main_prg = var_blks+main_prg
 
        python_code = self.clean_up_python_code(main_prg)

        return python_code

    def convert_segment(self, var_dict, code):
        # find outside construct, if any
        first_if = code.find('IF')
        first_case = code.find('CASE')

        first_for = code.find('FOR')
        first_while = code.find('WHILE')
        first_repeat = code.find('REPEAT')

        code_type = None
        first_idx = -1

        if first_if > -1:
            code_type = 'IF'
            first_idx = first_if

        if first_case > -1 and (code_type is None or first_case < first_idx):
            code_type = 'CASE'
            first_idx = first_case

        if first_for > -1 and (code_type is None or first_for < first_idx):
            code_type = 'FOR'
            first_idx = first_for

        if first_while > -1 and (code_type is None or first_while < first_idx):
            code_type = 'WHILE'
            first_idx = first_while

        if first_repeat > -1 and (code_type is None or first_repeat < first_idx):
            code_type = 'REPEAT'
            first_idx = first_repeat

        # convert the lines prior to the first control structure
        if code_type is not None:
            trans_code = self.convert_statements(var_dict, code[:first_idx])
        else:
            # convert the whole thing
            trans_code = self.convert_statements(var_dict, code)
            return trans_code
    
        match code_type:
            # the first control structure is an IF
            case 'IF':
                outside_if     = first_idx
                outside_then   = code.find('THEN')

                # find all END_IFs between outside_if and the end of the code
                endifs = find_instances('END_IF', code[outside_if+1:], outside_if+1)

                outside_endif = None
                # find first one for which the number of intervening IF/END_IF's are equal
                for endif_instance in endifs: 
                    ifs    = find_instances('IF', code[outside_if+1:endif_instance], outside_if+1)
                    endifs = find_instances('END_IF', code[outside_if+1:endif_instance], outside_if+1)

                    if len(ifs) == len(endifs):
                        outside_endif = endif_instance
                        break

                if outside_endif is None:
                    print("ouch 1")
                    pdb.set_trace()
                    print("ouch 1")

                if_cond        = get_condition(code[outside_if+2:outside_then])
                trans_code     += 'if '+if_cond+' :\n//START_BLK'
            
                # see if there is an ELSE between outside_then and outside_endif
                outside_else = None
                first_else = code[outside_then:outside_endif].find('ELSE')
                if first_else > -1:

                    # find all elses between here and outside_endif
                    elses = find_instances('ELSE', code[outside_then+4:outside_endif], outside_then+4)

                    # for each count the number of IFs and END_IFs between outside_if+2 and it
                    for else_instance in elses:
                        ifs       = find_instances('IF', code[outside_then+4:else_instance], 0)
                        end_ifs   = find_instances('END_IF', code[outside_then+4:else_instance], 0)
                        if len(ifs) == len(end_ifs):
                            outside_else = else_instance
                            break

                    if outside_else is None:
                        print("ouch 2")
                        pdb.set_trace()
                        print("ouch 2")

                    # convert the segment between outside_then+4 and outside_else
                    trans_code += self.convert_segment(var_dict, code[outside_then+4:outside_else])+'\n//END_BLK\n'
                    trans_code += 'else:\n//START_BLK'

                    # convert the segment between outside_else+4 and outside_endif
                    trans_code += self.convert_segment(var_dict, code[outside_else+4:outside_endif])+'\n//END_BLK\n'

                else:
                    trans_code += self.convert_segment(var_dict, code[outside_then+4:outside_endif])+'\n//END_BLK\n'
    
                # convert the rest of the code
                trans_code += self.convert_segment(var_dict, code[outside_endif+6:])
                return trans_code

            case 'CASE':
                outside_case   = first_idx
                case_end       = code.rfind('END_CASE;')

                of_key         = code.find('OF')
                case_check     = code[first_idx+4:of_key]
                trans_match    = case_check.strip()

                case_block     = code[of_key+2:case_end]

                trans_code     += f"match {case_check}:\n//START_BLK\n"

                # strip the lines of the case_block of any comments
                case_block = strip_comments(case_block)

                # find the case markers
                cmp = r"[a-zA-Z0-9_]+:[^=]"
                cases = re.finditer(cmp, case_block, re.IGNORECASE | re.DOTALL)
                   
                markers = [] 
                for choice in cases:
                    (bm, end) = choice.span()
                    for idx in range(bm+1,end):
                        if case_block[idx] == ':':
                            markers.append((bm,idx)) 

                # create the case descriptions
                case_rep = [] 
                for idx in range (0, len(markers)):
                    (start_cond, end_cond) = markers[idx]
                    cond = case_block[start_cond:end_cond]
 
                    if idx < len(markers)-1:
                        block = case_block[end_cond+1:markers[idx+1][0]]
                    else:
                        block = case_block[end_cond+1:]

                    block += '//END_BLK\n'
                    case_rep.append((cond, block)) 

                for (cond, block) in case_rep: 
                    trans_code += f"case {cond}:\n//START_BLK"
                    trans_code += self.convert_segment(var_dict, block)

                trans_code = trans_code+'\n//END_BLK\n'+self.convert_segment(var_dict, code[case_end+8:])
                return trans_code

            case 'FOR':
                for_loop_pattern = r"FOR\s+(.*?)\s*:=\s*(.*?)\s+TO\s+(.*?)\s+DO\s+(.*?)\s+END_FOR"
                for_loop = re.search(for_loop_pattern, code)
                loop_var = for_loop.group(1)
                loop_lower = for_loop.group(2)
                loop_upper = for_loop.group(3)
                loop_body  = for_loop.group(4)

                outside_for = code.find('FOR ') 
                outside_do  = code[outside_for+4:].find(' DO')+outside_for+4
                
                # find all the END_FOR;  from outside_for to the end of the code 
                endfors = find_instances('END_FOR;', code[outside_for+4:], outside_for+4)

                # find the first where the number of FOR and END_FOR between it and the 
                # outside FOR balance each other
                 
                outside_endfor = None
                # find first one for which the number of intervening FOR/END_FORs are equal
                for endfor_instance in endfors: 
                    fors    = find_instances('FOR', code[outside_for+4:endfor_instance], outside_for+4)
                    endfors = find_instances('END_FOR;', code[outside_for+4:endfor_instance], outside_for+4)

                    if len(fors) == len(endfors):
                        outside_endfor = endfor_instance
                        break

                # the body of the for loop is between outside_do + 3 and outside_endfor
                for_body = code[outside_do+3:outside_endfor]
            
                trans_code += f"for {loop_var} in range({loop_lower}, ({loop_upper})+1):\n//START_BLK"
                trans_code += self.convert_segment(var_dict, for_body)+'\n//END_BLK\n' 
                trans_code += self.convert_segment(var_dict, code[outside_endfor+7:])
                return trans_code

            case 'WHILE':
                while_loop_pattern = r"WHILE\s+(.*?)\s+DO"
                while_loop = re.search(while_loop_pattern, code)
                loop_var = while_loop.group(1)

                outside_while = code.find('WHILE ') 
                outside_do    = code[outside_while+6:].find(' DO')+outside_while+6
                 
                # find all the END_WHILE;  from outside_do to the end of the code 
                endwhiles = find_instances('END_WHILE;', code[outside_while+6:], outside_while+6)

                # find the first where the number of WHILE and END_WHILE between it and the 
                # outside WHILE balance each other
                 
                outside_endwhile = None
                # find first one while which the number of intervening FOR/END_FORs are equal
                for endwhile_instance in endwhiles: 
                    whiles    = find_instances('WHILE ', code[outside_while+6:endwhile_instance], outside_while+6)
                    endwhiles = find_instances('END_WHILE;', code[outside_while+6:endwhile_instance], outside_while+6)

                    if len(whiles) == len(endwhiles):
                        outside_endwhile = endwhile_instance
                        break

                # the body of the while loop is between outside_do + 3 and outside_endwhile
                while_body = code[outside_do+3:outside_endwhile]

                trans_code += f"while {loop_var}:\n//START_BLK"
                trans_code += self.convert_segment(var_dict, while_body)+'\n//END_BLK\n' 
                trans_code += self.convert_segment(var_dict, code[outside_endwhile+9:])
                return trans_code

            case 'REPEAT':
                repeat_loop_pattern = r"REPEAT\s+(.*?)UNTIL\s+"
                outside_repeat = code.find("REPEAT")


                # find all the UNTILs;  from outside_repeat to the end of the code 
                untils = find_instances('UNTIL', code[outside_repeat+6:], outside_repeat+6)

                # find the first where the number of REPEAT and END_REPEAT between it and the 
                # outside REPEAT balance each other
                 
                outside_until = None
                # find first repeat which the number of intervening REPEAT/END_REPEAT are equal
                for until_instance in untils: 
                    repeats    = find_instances('REPEAT ', code[outside_repeat+6:until_instance], outside_repeat+6)
                    endrepeats = find_instances('END_REPEAT;', code[outside_repeat+6:until_instance], outside_repeat+6)

                    if len(repeats) == len(endrepeats):
                        outside_until = until_instance
                        break

                # the body of the repeat loop is between outside_repeat + 6 and outside_until
                outside_endrepeat = code[outside_until+5:].find('END_REPEAT;')+outside_until+5
                condition = code[outside_until+5:outside_endrepeat].strip()

                repeat_body = code[outside_repeat+6:outside_until]

                trans_code += f"while True:\n//START_BLK\n"
                trans_code += self.convert_segment(var_dict, repeat_body)+'\n' 
                trans_code += f"if {condition}:\n//START_BLK\nbreak\n//END_BLK\n//END_BLK"
                trans_code += self.convert_segment(var_dict, code[outside_endrepeat+11:])
                return trans_code

    
    def convert_statements(self, var_dict, code):
        lines = code.split('\n')

        rtn = []
 
        statements = code.split(';')
        for statement in statements:
            # if an assignment, change the assignment operator
            if statement.find(':=') > -1:
                statement = statement.replace(':=', '=')

            # if a call to a function block, alter
            words = statement.split()

            # look for instances where a FB variable looks like it is being called
            for word in words: 
                for var_name, var_inst in var_dict.items():
                    tst_var_name = var_name+'('
                    if word.find(tst_var_name) > -1 and var_inst.vclass is not None:
                        statement = statement.replace(var_name, var_name+'.call')
                        break 

            rtn.append(statement)
            
        return ' '.join(rtn)

    def convert_fb(self, var_dict, st_code):
        lines = st_code.split('\n')
        rtn = []
        for line in lines:
            trimmed = line
            if line.find('//') > -1:
                trimmed = line[: line.find('//')]

            words = trimmed.split()

            # look for instances where a FB variable looks like it is being called
            for word in words: 
                for var_name, var_inst in var_dict.items():
                    tst_var_name = var_name+'('
                    if word.find(tst_var_name) > -1 and var_inst.vclass is not None:
                        line = line.replace(var_name, var_name+'.call')
                        break 

            rtn.append(line)
            
        return '\n'.join(rtn)     

    def clean_up_python_code(self, python_code):

        # Replace ST keywords with Python keywords...
        python_code = re.sub(r"\bRETURN\b", "return", python_code, flags=re.IGNORECASE)
        python_code = re.sub(r"\bEXIT\b", "break", python_code, flags=re.IGNORECASE)
        python_code = re.sub(r"\bfalse\b", "False", python_code, flags=re.IGNORECASE)
        python_code = re.sub(r"\btrue\b", "True", python_code, flags=re.IGNORECASE)
        python_code = python_code.replace(":=", "=")
        python_code = python_code.replace(";", "")
        python_code = python_code.replace("?", ":")
        python_code = python_code.strip()

        # Add newline at the end if not present
        if not python_code.endswith("\n"):
            python_code += "\n"

        # Replace duplicate empty lines
        python_code = re.sub(r"\n\s*\n{2,}", "\n\n", python_code)

        # do alignment
        lines = python_code.split('\n')
        rtn = []
        indentStep = '    '
        indent = ''
        indentCnt = 0

        for line in lines:
            line = line.strip()
            if line.startswith('//START_BLK'):
                indentCnt += 1
                indentArray = [indentStep]*indentCnt
                indent = ''.join(indentArray)
                continue

            if line.startswith('//END_BLK'):
                if indentCnt > 0:
                    indentCnt -= 1

                indentArray = [indentStep]*indentCnt
                indent = ''.join(indentArray)
                continue 
   
            line = indent+line
            rtn.append(line)

        python_code = '\n'.join(rtn)

        # convert in-line comments
        python_code = python_code.replace('//','#')

        return python_code


def strip_comments(blk):
    lines = blk.split('\n')
    rtn = []
    for line in lines:
        if line.find('(*') > -1 and line.find('*)') > -1:
            continue
        start = line.find('//')
        if start > -1:
            line = line[:start]
        rtn.append(line.strip())

    return '\n'.join(rtn)

def get_condition(clause):
    if clause.find('=')> -1 and clause.find('<=') == -1 and clause.find('>=') == -1:
        clause = clause.replace('=','==') 
    return clause.strip()
    

def trans_condition(pattern, code):
        matches = re.finditer(pattern, code, re.IGNORECASE | re.DOTALL)
        fill = []
        for test_clause in matches:
            # transform any '=' which is not part of '<=' or '>=' into '=='
            (srt,end) = test_clause.span()
            clause = code[srt:end+1]
            if clause.find('=')> -1 and clause.find('<=') == -1 and clause.find('>=') == -1:
                here = clause.find('=')
                fill.append(here+srt)

        for idx in reversed(range(0,len(fill))):
            here = fill[idx]
            code = code[:here]+'='+code[here:]

        return code

def find_instances(substr, mainstr, offset):
    locs = []
    while True:
        nxt_loc = mainstr.find(substr)
        if nxt_loc > -1:
            locs.append(nxt_loc+offset)
            mainstr = mainstr[nxt_loc+len(substr):]
        else:
            break
    return locs
 

add_st2py  = 'def st2py():\n'
entry_call = 'if __name__ == "__main__":\n    st2py()\n'
imports    = ('sys','os','pdb')



def add_imports():
    rtn = []
    for module in imports:
        rtn.append(f"import {module}")
    return '\n'.join(rtn)+'\n'

def add_functions():
    return functions

if __name__ == "__main__":
    getArgs()

    convertor = ConvertorApp(st_file)
    python_code = convertor.convert()

    python_code = python_code.replace('#START_MAIN','while True:')
    python_code = add_imports()+'\n'+add_functions()+'\n'+add_st2py+python_code+'\n'+entry_call+'\n'

    with open(python_file, 'w') as wf:
        wf.write(python_code) 
