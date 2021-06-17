import winreg
# open one of the root keys
# get to the bottom of the registry, key by key
# enumerate values

# winreg.createkey(key, subkey)
# print(winreg.QueryInfoKey(winreg.HKEY_LOCAL_MACHINE))
# print(winreg.EnumKey(winreg.HKEY_LOCAL_MACHINE, 3))

'''downward_reglist = [
    "HKEY_LOCAL_MACHINE",
    "SOFTWARE",
    "Microsoft",
    "Windows",
    "CurrentVersion",
    "MMDevices",
    "DefaultDeviceHeuristics",
    "Default",
    "Role_0",
    "Factor_0"
]'''
print()

def open_regkey_from_path(key_path: str):
    downward_reglist = key_path.split("\\")[1:]
    print(downward_reglist)
    key = winreg.HKEY_LOCAL_MACHINE #root key
    for subkey_name in downward_reglist[1:]:
        next_key = winreg.OpenKey(key, subkey_name)
        key = next_key
    bottom_key_dir_name = downward_reglist[-1]
    return key

def get_regkey_values(key):
    number_of_values_in_key = winreg.QueryInfoKey(key)[1]
    print(f"Regkey has {number_of_values_in_key} values in it")
    values_list = [winreg.EnumValue(key, i) for i in range(number_of_values_in_key)]
    print()
    for value in values_list:
        value_name, value_type, value_value = value
        print(value_name, value_value)
    if not values_list: print("Comports haven't been found")
    return values_list

#def get_specific_value_in_key(key, value_name)
#return value_value

'''def swipe_across_the_key(key, bottom_key_dir_name: str):
    pass
    iterator = 0
    enum_str = ''
    while enum_str != bottom_key_dir_name:
        enum_str = winreg.EnumKey(key, iterator)
        iterator += 1
    print(enum_str)
    number_of_values_in_key = winreg.QueryInfoKey(key)[1]
    print(number_of_values_in_key)
    values_list = [winreg.EnumKey(key, i) for i in range(number_of_values_in_key)]
    print()
    print(values_list)
    if not values_list:
        print("Comports haven't been found")'''
    

key = open_regkey_from_path("Компьютер\HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft"
           + "\Windows\CurrentVersion\MMDevices\\"
           + "DefaultDeviceHeuristics\Default\Role_0\Factor_0")

values_list = get_regkey_values(key)

#BTHENUM key is needed
