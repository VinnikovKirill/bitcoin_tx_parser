#the code below parses bitcoin transactions obtained from txs_raw.txt file
#each transaction is byte string written in different line
#also there is a dictionary based on opcodes.txt file
#keep in mind that 2 symbols in string = 1 byte
 
import binascii

f2 = open('opcodes.txt', 'r')
f = open('txs_raw.txt', 'r')

d_1 = [] #make a dict out of opcodes file
for line in f2:
    line = line.replace('\'', '').replace('\n', '').split(':') #formatting strings for dict function to work properly
    d_1.append(line)
d_1 = dict(d_1)

d_2 = {'fd':2, 'fe':4, 'ff':8} #varint keys, values are bytes
d_3 = {0:'inputs:', 1:'outputs:'} #used in printing result later on

def convert_to_script(raw_script_string): #converting raw hex string to script langauge
    result_string = ''
    while raw_script_string != '':
        temp = raw_script_string[:2]
        if temp not in d_1.keys():
            bytesize = int(temp, 16)
            raw_script_string = raw_script_string[2:]

            result_string += (str(int(raw_script_string[:bytesize * 2], 16))) + ' '
            raw_script_string = raw_script_string[bytesize * 2:]
        else:
            result_string += d_1.get(temp) + ' '
            raw_script_string = raw_script_string[2:]
    return result_string        

def hex_to_little_endian(hex_string): #turns hex_string to little endian, returns bytes
    return binascii.hexlify(bytearray.fromhex(hex_string)[::-1])

def return_var_int(tx_string): #returns int value of varint, also returns changed tx_string (without varint)
    temp = tx_string[:2]
    if temp not in d_2.keys():
        return tx_string[2:], int(temp, 16)
    else:
        hex_string = tx_string[2:d_2.get(temp) * 2]
        return tx_string[(d_2.get(temp) * 2) + 2:], int(hex_to_little_endian(hex_string), 16)

def parse_exits(s): #defines how many outputs are in tx, puts them all in the list while parsing returns changed string
    exits_list = []
    s, n_outputs = return_var_int(s) #nubmer of outputs in transaction
    for i in range(n_outputs):
        temp_list = []
        temp_list.append(int(s[:16], 16)) # 8bytes, 8 * 2 = 16

        s = s[16:]
        s, script_pub_key_size = return_var_int(s) #same goes here, look at the initial method

        temp_list.append(script_pub_key_size)
        script_pub_key = s[:script_pub_key_size * 2] #same goes here

        temp_list.append(convert_to_script(script_pub_key))
        s = s[script_pub_key_size * 2:]
        
        exits_list.append(temp_list)
    return s, exits_list

def parse_inputs(s): #defines how many inputs are in tx, puts them all in the list while parsing, returns changed string 
    inputs_list = []
    s, n_input = return_var_int(s) #nubmer of inputs in transaction
    for i in range(n_input):
        temp_list = []

        temp_list.append(s[:64]) #txid
        s = s[64:]

        temp_list.append(s[:8]) #vout
        s = s[8:]

        s, script_sig_size = return_var_int(s)

        temp_list.append(script_sig_size)
        script_sig = s[:script_sig_size * 2]

        temp_list.append(convert_to_script(script_sig))
        s = s[script_sig_size * 2:]

        temp_list.append(s[:8])
        s = s[8:]

        inputs_list.append(temp_list)
    return s, inputs_list

count = 0
lines  = f.readlines()
for st in lines:
    general_output = []

    general_output.append(st[:8])
    st = st[8:]

    st, inputs_list = parse_inputs(st)
    general_output.append(inputs_list)

    st, outputs_list = parse_exits(st)
    general_output.append(outputs_list)

    general_output.append(st[:8])
    st = st[8:]

    var = 0

    #READ THIS BEFORE CHECKING OUTPUT OF THE PROGRAM!
    #inputs and outputs are printed as a list with exclamation string over

    #inputs format: TXID, VOUT, ScriptSigSize, ScriptSig, Sequence

    #outputs format: Value, ScriptPubKeySize, ScriptPubKey

    for i in general_output:
        if isinstance(i, list):
            print(d_3.get(var))
            for j in i:
                print(j, '\n')
            var += 1
        else:
            print(i, '\n')

    print("----------")
    count += 1

print(count, "txes")

f2.close()
f.close()
