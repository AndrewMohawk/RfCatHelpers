# RfCatHelpers
Helper scripts for RfCat devices

# AM OOK Scanner
Script listens for OOK signals (starting with multiple 0's), converts this to binary and compares to other signals it has seen, it will then try and calculate the accurate final signal (based on normalising all the signals).

# AM OOK Transmit
Simple script to take the binary you wish to send and ... well ... send it. Will either convert your binary (by creating the 0's and 1's for AM/OOK) or send out a full binary (if conversion is already done, say from listening with the Scanner)

# PWMScanner
This looks for AM/OOK signals and 'locks' onto them to show you the outputted script as well as offers you the ability to replay a captured signal, useful for basic testing, but ultimately not something you want to use when doing more advanced testing

# RF Jammer
Script to Jam on a single frequency, useful for stopping transmissions from going through to replay them

# RF Simple replay
Listens for a 'packet' ( re.search(r'((0)\2{15,})', x ) and stores a particular amount of these packets (configured) then replays them when the user presses a key

# RF Simple transmit
Resends packets captured from the about (use -o for out/in file for both)

# Dual RF
Ability to use 2 RFCat compatible devices to search and jam -- not recommended for anything but laughing at my code
