import winreg
# open one of the root keys
# get to the bottom of the registry, key by key
# enumerate values

# winreg.createkey(key, subkey)
# print(winreg.QueryInfoKey(winreg.HKEY_LOCAL_MACHINE))
# print(winreg.EnumKey(winreg.HKEY_LOCAL_MACHINE, 3))

downward_reglist = [
    "HKEY_LOCAL_MACHINE",
    "SOFTWARE",
    "Microsoft",
    "Windows",
    "CurrentVersion",
    "MMDevices",
    "DefaultDeviceHeuristics",
    "Default",
    "Role_0",
    "Factor_1"
]
print()

key = winreg.HKEY_LOCAL_MACHINE #root key
for subkey_name in downward_reglist[1:-1]:
    next_key = winreg.OpenKey(key, subkey_name)
    key = next_key
    # print(key)
    # print(winreg.EnumKey(key, 0))
iterator = 0
enum_str = ''
while enum_str != "Factor_1":
    enum_str = winreg.EnumKey(key, iterator)
    iterator += 1
print(enum_str)
number_of_values = winreg.QueryInfoKey(key)[1]
values_list = [winreg.EnumKey(key, i) for i in range(number_of_values)]
print()
print(values_list)
