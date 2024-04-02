# UBM I2C Analyzer

This High Level Analyzer will parse I2C traffic from a UBM host to a UBM controller.
It will decode the commands read from or written to the UBM controller and print out the parsed data
in a readable format to the terminal.
It will also keep track of the number of times a command has been accessed and print that along with the parsed data
to allow the user to correlate parsed data to when the command was accessed in the logic capture. 

## Prerequisites
You will need to know the UBM Controllers 7-bit target address. All UBM controllers most host the UBM FRU at 8-bit address 0xAE (7-bit 0x57).

## Getting Started

1. Select and setup the I2C signal from Saleae
2. Add the UBM I2C Analyzer and select the I2C signal analyzer as the input
3. Input the UBM Controller's 7-bit address in hex format (0x55)