import os, re, math, time


def sani(_x, _s, _sop): #Function to sanitize input
    _x
    while True:
        _y = input(_s)
        if type(_y) == str:
            if 'back' == _y.lower():
                return _y.lower()
            elif 'exit' == _y.lower():
                exit()           
        if type(_y) == _x:
            if _sop:
                for i in _sop:
                    if i == _y:
                        return _y
            if not _sop:
                return _y
            else:
                print("Unaccepted input, please try again.")
        try:
            if _x == int:
                _y = int(_y)
                if _sop:
                    for i in _sop:
                        if i == _y:
                            return _y
                if not _sop:
                    return _y
                else:
                    print("Unaccepted input, please try again.")
        except ValueError:
            print("Unaccepted input, please try again.")

def clear(): #Function to clear terminal
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')
        
def progressBar(iterable, prefix='', suffix='', decimals=1, length=50, fill='', printEnd="\r"): # Visual progress bar function
    """
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    if len(iterable) > 0:
        total = len(iterable)
    else:
        return

    def printProgressBar(iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                         (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)

    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)    

def valid_ip(address): # Function validates IP address format of data, and returns bool

    match = re.match(
        '''(\d+)(?<!10)\.(\d+)(?<!192\.168)(?<!172\.(1[6-9]|2\d|3[0-1]))\.(\d+)\.(\d+)''', address)

    if bool(match):
        return True
    else:
        return False

def alert_age(_c, _a): # Returns difference in provided epochs in minutes
    return (_c - _a) / 60

def age_convert(_g): # Function to convert to pretty numbers
    _day = math.floor(_g / 1440)
    _lm = round(_g % 1440)
    _hour = math.floor(_lm / 60)
    _min = _g - (_day*1440) - (_hour*60)
    r = {
        "min": _min,
        "lm": _lm,
        "hour": _hour,
        "day": _day
    }
    return r

def ip_in_prefix(ip_address, prefix): # Functions to check if IP is inside of subnet, accepts IP and IP/SUB as input, returns true or false
    # CIDR based separation of address and network size
    [prefix_address, net_size] = prefix.split("/")
    # Convert string to int
    net_size = int(net_size)
    # Get the network ID of both prefix and ip based net size
    prefix_network = get_addr_network(prefix_address, net_size)
    ip_network = get_addr_network(ip_address, net_size)
    return ip_network == prefix_network

def get_addr_network(address, net_size):
    # Convert ip address to 32 bit binary
    ip_bin = ip_to_binary(address)
    # Extract Network ID from 32 binary
    network = ip_bin[0:32-(32-net_size)]
    return network

def ip_to_binary(ip):
    octet_list_int = ip.split(".")
    octet_list_bin = [format(int(i), '08b') for i in octet_list_int]
    binary = ("").join(octet_list_bin)
    return binary

def menu_disp(_mit, _itf, _int, usr_prompt): # Menu Displayer
    opt_ = list(range(1,(len(_mit)+1)))
    while True:
        clear()
        print(_int)
        count = 1
        for i in _mit:
            print(f'{count} -- {i}')
            count += 1
        print("-----------------------------------------------------")
        j = sani(int, usr_prompt, opt_)
        if type(j) == int: j = j - 1
        if str(j) == 'back':
            return False
        else:
            if j < len(_itf):
                _itf[j]()
                break
            else:
                print("No Menu Option!")
                time.sleep(1)