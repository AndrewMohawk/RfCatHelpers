# RfCatHelpers
Helper scripts for RfCat devices

# AM OOK Scanner
Script listens for OOK signals (starting with multiple 0's), converts this to binary and compares to other signals it has seen, it will then try and calculate the accurate final signal (based on normalising all the signals).

# AM OOK Transmit
Simple script to take the binary you wish to send and ... well ... send it. Will either convert your binary (by creating the 0's and 1's for AM/OOK) or send out a full binary (if conversion is already done, say from listening with the Scanner)

