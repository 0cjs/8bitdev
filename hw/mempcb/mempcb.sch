EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L mempcb:RC6502_Bus J1
U 1 1 5FE89A90
P 1850 2900
F 0 "J1" H 2000 4950 50  0000 C CNN
F 1 "RC6502_Bus" H 1958 4890 50  0001 C CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x39_P2.54mm_Horizontal" H 1850 2900 50  0001 C CNN
F 3 "~" H 1850 2900 50  0001 C CNN
	1    1850 2900
	1    0    0    -1  
$EndComp
$Comp
L mempcb:RC6502_Bus W1
U 1 1 5FE96F9C
P 2700 2900
F 0 "W1" H 2850 4950 50  0000 R CNN
F 1 "RC6502_Bus" H 2300 4850 50  0001 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x39_P2.54mm_Vertical" H 2700 2900 50  0001 C CNN
F 3 "~" H 2700 2900 50  0001 C CNN
	1    2700 2900
	-1   0    0    -1  
$EndComp
$Comp
L mempcb:JEDEC_DIP32_RAM U3
U 1 1 5FEAD713
P 5500 2100
F 0 "U3" H 5500 3267 50  0000 C CNN
F 1 "JEDEC_DIP32_RAM" H 5500 3176 50  0000 C CNN
F 2 "Package_DIP:DIP-32_W15.24mm_Socket_LongPads" H 5500 2100 50  0001 C CNN
F 3 "http://www.futurlec.com/Datasheet/Memory/628128.pdf" H 5500 2100 50  0001 C CNN
	1    5500 2100
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_02x25_Odd_Even J2
U 1 1 5FEB0496
P 8850 2750
F 0 "J2" H 8900 4200 50  0000 C CNN
F 1 "0.1\" 2x25" H 8900 4100 50  0000 C CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_2x25_P2.54mm_Vertical" H 8850 2750 50  0001 C CNN
F 3 "~" H 8850 2750 50  0001 C CNN
	1    8850 2750
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x25 W2_1
U 1 1 5FEB2EF1
P 8250 2750
F 0 "W2_1" H 8250 4200 50  0000 C CNN
F 1 "0.1\" 1x25" H 8250 4100 50  0000 C CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x25_P2.54mm_Vertical" H 8250 2750 50  0001 C CNN
F 3 "~" H 8250 2750 50  0001 C CNN
	1    8250 2750
	-1   0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x25 W2_2
U 1 1 5FEC1F3E
P 9550 2750
F 0 "W2_2" H 9450 4200 50  0000 L CNN
F 1 "0.1\" 1x25" H 9350 4100 50  0000 L CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x25_P2.54mm_Vertical" H 9550 2750 50  0001 C CNN
F 3 "~" H 9550 2750 50  0001 C CNN
	1    9550 2750
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x16 W3_1
U 1 1 5FECEA90
P 4550 2000
F 0 "W3_1" H 4550 2950 50  0000 C CNN
F 1 "0.1\" 1x16" H 4468 2826 50  0000 C CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x16_P2.54mm_Vertical" H 4550 2000 50  0001 C CNN
F 3 "~" H 4550 2000 50  0001 C CNN
	1    4550 2000
	-1   0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x08 W4_2
U 1 1 5FECFD2E
P 6500 4100
F 0 "W4_2" H 6400 4650 50  0000 L CNN
F 1 "0.1\" 1x8" H 6350 4550 50  0000 L CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical" H 6500 4100 50  0001 C CNN
F 3 "~" H 6500 4100 50  0001 C CNN
	1    6500 4100
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x08 W4_1
U 1 1 5FED086C
P 4500 4100
F 0 "W4_1" H 4418 4617 50  0000 C CNN
F 1 "0.1\" 1x8" H 4418 4526 50  0000 C CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical" H 4500 4100 50  0001 C CNN
F 3 "~" H 4500 4100 50  0001 C CNN
	1    4500 4100
	-1   0    0    -1  
$EndComp
Wire Wire Line
	4750 1300 5000 1300
Wire Wire Line
	4750 1400 5000 1400
Wire Wire Line
	4750 1500 5000 1500
Wire Wire Line
	4750 1600 5000 1600
Wire Wire Line
	4750 1700 5000 1700
Wire Wire Line
	4750 1800 5000 1800
Wire Wire Line
	4750 1900 5000 1900
Wire Wire Line
	4750 2000 5000 2000
Wire Wire Line
	4750 2100 5000 2100
Wire Wire Line
	4750 2200 5000 2200
Wire Wire Line
	4750 2300 5000 2300
Wire Wire Line
	4750 2400 5000 2400
Wire Wire Line
	4750 2500 5000 2500
Wire Wire Line
	4750 2600 5000 2600
Wire Wire Line
	4750 2700 5000 2700
Wire Wire Line
	4750 2800 5000 2800
Wire Wire Line
	6250 2800 6000 2800
Wire Wire Line
	6250 2700 6000 2700
Wire Wire Line
	6250 2600 6000 2600
Wire Wire Line
	6250 2500 6000 2500
Wire Wire Line
	6250 2400 6000 2400
Wire Wire Line
	6250 2300 6000 2300
Wire Wire Line
	6250 2200 6000 2200
Wire Wire Line
	6250 2100 6000 2100
Wire Wire Line
	6250 2000 6000 2000
Wire Wire Line
	6250 1900 6000 1900
Wire Wire Line
	6250 1800 6000 1800
Wire Wire Line
	6250 1700 6000 1700
Wire Wire Line
	6250 1600 6000 1600
Wire Wire Line
	6250 1500 6000 1500
Wire Wire Line
	6250 1400 6000 1400
Wire Wire Line
	6250 1300 6000 1300
$Comp
L Connector_Generic:Conn_01x16 W3_2
U 1 1 5FECF06C
P 6450 2000
F 0 "W3_2" H 6350 2950 50  0000 L CNN
F 1 "0.1\" 1x16" H 6250 2850 50  0000 L CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x16_P2.54mm_Vertical" H 6450 2000 50  0001 C CNN
F 3 "~" H 6450 2000 50  0001 C CNN
	1    6450 2000
	1    0    0    -1  
$EndComp
Text Label 4750 2800 0    50   ~ 0
GND
Text Label 4750 2700 0    50   ~ 0
D2
Text Label 4750 2600 0    50   ~ 0
D1
Text Label 4750 2500 0    50   ~ 0
D0
Text Label 4750 2400 0    50   ~ 0
A0
Text Label 4750 2300 0    50   ~ 0
A1
Text Label 4750 2200 0    50   ~ 0
A2
Text Label 4750 2100 0    50   ~ 0
A3
Text Label 4750 2000 0    50   ~ 0
A4
Text Label 4750 1900 0    50   ~ 0
A5
Text Label 4750 1800 0    50   ~ 0
A6
Text Label 6050 1800 0    50   ~ 0
A8
Text Label 6050 1900 0    50   ~ 0
A9
Text Label 6050 2100 0    50   ~ 0
~OE
Text Label 6050 2200 0    50   ~ 0
A10
Text Label 6050 2300 0    50   ~ 0
~CE
Text Label 6050 2400 0    50   ~ 0
D7
Text Label 6050 2500 0    50   ~ 0
D6
Text Label 6050 2600 0    50   ~ 0
D5
Text Label 6050 2700 0    50   ~ 0
D4
Text Label 6050 2800 0    50   ~ 0
D3
$Comp
L mempcb:74LS138 U4
U 1 1 5FF60AA3
P 5500 4100
F 0 "U4" H 5500 4667 50  0000 C CNN
F 1 "74LS138" H 5500 4576 50  0000 C CNN
F 2 "Package_DIP:DIP-16_W7.62mm_Socket_LongPads" H 5500 4100 50  0001 C CNN
F 3 "http://www.ti.com/lit/gpn/sn74LS138" H 5500 4100 50  0001 C CNN
	1    5500 4100
	1    0    0    -1  
$EndComp
Wire Wire Line
	6000 3800 6300 3800
Wire Wire Line
	6000 3900 6300 3900
Wire Wire Line
	6000 4000 6300 4000
Wire Wire Line
	6000 4100 6300 4100
Wire Wire Line
	6000 4200 6300 4200
Wire Wire Line
	6000 4300 6300 4300
Wire Wire Line
	6000 4400 6300 4400
Wire Wire Line
	6000 4500 6300 4500
Wire Wire Line
	5000 3800 4700 3800
Wire Wire Line
	5000 3900 4700 3900
Wire Wire Line
	5000 4000 4700 4000
Wire Wire Line
	5000 4100 4700 4100
Wire Wire Line
	5000 4200 4700 4200
Wire Wire Line
	5000 4300 4700 4300
Wire Wire Line
	5000 4400 4700 4400
Wire Wire Line
	5000 4500 4700 4500
Text Label 4750 4500 0    50   ~ 0
GND
Text Label 6050 3800 0    50   ~ 0
VCC
Wire Wire Line
	8450 1550 8650 1550
Wire Wire Line
	8450 1650 8650 1650
Wire Wire Line
	8450 1750 8650 1750
Wire Wire Line
	8450 1850 8650 1850
Wire Wire Line
	8450 1950 8650 1950
Wire Wire Line
	8450 2050 8650 2050
Wire Wire Line
	8450 2150 8650 2150
Wire Wire Line
	8450 2250 8650 2250
Wire Wire Line
	8450 2350 8650 2350
Wire Wire Line
	8450 2450 8650 2450
Wire Wire Line
	8450 2550 8650 2550
Wire Wire Line
	8450 2650 8650 2650
Wire Wire Line
	8450 2750 8650 2750
Wire Wire Line
	8450 2850 8650 2850
Wire Wire Line
	8450 2950 8650 2950
Wire Wire Line
	8450 3050 8650 3050
Wire Wire Line
	8450 3150 8650 3150
Wire Wire Line
	8450 3250 8650 3250
Wire Wire Line
	8450 3350 8650 3350
Wire Wire Line
	8450 3450 8650 3450
Wire Wire Line
	8450 3550 8650 3550
Wire Wire Line
	8450 3650 8650 3650
Wire Wire Line
	8450 3750 8650 3750
Wire Wire Line
	8450 3850 8650 3850
Wire Wire Line
	8450 3950 8650 3950
Wire Wire Line
	9150 1550 9350 1550
Wire Wire Line
	9150 1650 9350 1650
Wire Wire Line
	9150 1750 9350 1750
Wire Wire Line
	9150 1850 9350 1850
Wire Wire Line
	9150 1950 9350 1950
Wire Wire Line
	9150 2050 9350 2050
Wire Wire Line
	9150 2150 9350 2150
Wire Wire Line
	9150 2250 9350 2250
Wire Wire Line
	9150 2350 9350 2350
Wire Wire Line
	9150 2450 9350 2450
Wire Wire Line
	9150 2550 9350 2550
Wire Wire Line
	9150 2650 9350 2650
Wire Wire Line
	9150 2750 9350 2750
Wire Wire Line
	9150 2850 9350 2850
Wire Wire Line
	9150 2950 9350 2950
Wire Wire Line
	9150 3050 9350 3050
Wire Wire Line
	9150 3150 9350 3150
Wire Wire Line
	9150 3250 9350 3250
Wire Wire Line
	9150 3350 9350 3350
Wire Wire Line
	9150 3450 9350 3450
Wire Wire Line
	9150 3550 9350 3550
Wire Wire Line
	9150 3650 9350 3650
Wire Wire Line
	9150 3750 9350 3750
Wire Wire Line
	9150 3850 9350 3850
Wire Wire Line
	9150 3950 9350 3950
Wire Wire Line
	2050 1000 2500 1000
Wire Wire Line
	2050 1100 2500 1100
Wire Wire Line
	2050 1200 2500 1200
Wire Wire Line
	2050 1300 2500 1300
Wire Wire Line
	2050 1400 2500 1400
Wire Wire Line
	2050 1500 2500 1500
Wire Wire Line
	2050 1600 2500 1600
Wire Wire Line
	2050 1700 2500 1700
Wire Wire Line
	2050 1800 2500 1800
Wire Wire Line
	2050 1900 2500 1900
Wire Wire Line
	2050 2000 2500 2000
Wire Wire Line
	2050 2100 2500 2100
Wire Wire Line
	2050 2200 2500 2200
Wire Wire Line
	2050 2300 2500 2300
Wire Wire Line
	2050 2400 2500 2400
Wire Wire Line
	2050 2500 2500 2500
Wire Wire Line
	2050 2600 2500 2600
Wire Wire Line
	2050 2800 2500 2800
Wire Wire Line
	2050 2900 2500 2900
Wire Wire Line
	2050 3000 2500 3000
Wire Wire Line
	2050 3100 2500 3100
Wire Wire Line
	2050 3200 2500 3200
Wire Wire Line
	2050 3300 2500 3300
Wire Wire Line
	2050 3400 2500 3400
Wire Wire Line
	2050 3500 2500 3500
Wire Wire Line
	2050 3600 2500 3600
Wire Wire Line
	2050 3700 2500 3700
Wire Wire Line
	2050 3800 2500 3800
Wire Wire Line
	2050 3900 2500 3900
Wire Wire Line
	2050 4000 2500 4000
Wire Wire Line
	2050 4100 2500 4100
Wire Wire Line
	2050 4200 2500 4200
Wire Wire Line
	2050 4300 2500 4300
Wire Wire Line
	2050 4400 2500 4400
Wire Wire Line
	2050 4500 2500 4500
Wire Wire Line
	2050 4600 2500 4600
Wire Wire Line
	2050 4700 2500 4700
Wire Wire Line
	2050 4800 2500 4800
Text Label 2100 3600 0    50   ~ 0
D0
Text Label 2100 3700 0    50   ~ 0
D1
Text Label 2100 3800 0    50   ~ 0
D2
Text Label 2100 3900 0    50   ~ 0
D3
Text Label 2100 4000 0    50   ~ 0
D4
Text Label 2100 4100 0    50   ~ 0
D5
Text Label 2100 4200 0    50   ~ 0
D6
Text Label 2100 4300 0    50   ~ 0
D7
Text Label 2100 2500 0    50   ~ 0
A0
Text Label 2100 2400 0    50   ~ 0
A1
Text Label 2100 2300 0    50   ~ 0
A2
Text Label 2100 2200 0    50   ~ 0
A3
Text Label 2100 2100 0    50   ~ 0
A4
Text Label 2100 2000 0    50   ~ 0
A5
Text Label 2100 1900 0    50   ~ 0
A6
Text Label 2100 1800 0    50   ~ 0
A7
Text Label 2100 1700 0    50   ~ 0
A8
Text Label 2100 1600 0    50   ~ 0
A9
Text Label 2100 1500 0    50   ~ 0
A10
Text Label 6050 1300 0    50   ~ 0
VCC
$Comp
L Connector_Generic:Conn_01x04 HIGH1
U 1 1 5FED18C8
P 3850 5900
F 0 "HIGH1" V 4050 5950 50  0000 R CNN
F 1 "0.1\" 1x4" V 3950 6000 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical" H 3850 5900 50  0001 C CNN
F 3 "~" H 3850 5900 50  0001 C CNN
	1    3850 5900
	0    -1   -1   0   
$EndComp
$Comp
L Connector_Generic:Conn_01x04 LOW1
U 1 1 603235A5
P 4400 5900
F 0 "LOW1" V 4600 5950 50  0000 R CNN
F 1 "0.1\" 1x4" V 4500 6000 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical" H 4400 5900 50  0001 C CNN
F 3 "~" H 4400 5900 50  0001 C CNN
	1    4400 5900
	0    -1   -1   0   
$EndComp
$Comp
L Connector_Generic:Conn_01x04 PULLUP1
U 1 1 6032F1DA
P 3350 5900
F 0 "PULLUP1" V 3550 6000 50  0000 R CNN
F 1 "0.1\" 1x4" V 3450 6000 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical" H 3350 5900 50  0001 C CNN
F 3 "~" H 3350 5900 50  0001 C CNN
	1    3350 5900
	0    -1   -1   0   
$EndComp
Wire Wire Line
	3250 6600 3250 6500
Wire Wire Line
	3250 6200 3250 6100
$Comp
L Device:R R2
U 1 1 603E796E
P 3350 6350
F 0 "R2" V 3350 6350 50  0000 C CNN
F 1 "R" V 3350 6350 50  0001 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 3280 6350 50  0001 C CNN
F 3 "~" H 3350 6350 50  0001 C CNN
	1    3350 6350
	1    0    0    -1  
$EndComp
Wire Wire Line
	3350 6600 3350 6500
Wire Wire Line
	3350 6200 3350 6100
$Comp
L Device:R R3
U 1 1 60400026
P 3450 6350
F 0 "R3" V 3450 6350 50  0000 C CNN
F 1 "R" V 3450 6350 50  0001 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 3380 6350 50  0001 C CNN
F 3 "~" H 3450 6350 50  0001 C CNN
	1    3450 6350
	1    0    0    -1  
$EndComp
Wire Wire Line
	3450 6600 3450 6500
Wire Wire Line
	3450 6200 3450 6100
$Comp
L Device:R R4
U 1 1 6040C3DC
P 3550 6350
F 0 "R4" V 3550 6350 50  0000 C CNN
F 1 "R" V 3550 6350 50  0001 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 3480 6350 50  0001 C CNN
F 3 "~" H 3550 6350 50  0001 C CNN
	1    3550 6350
	1    0    0    -1  
$EndComp
Wire Wire Line
	3550 6600 3550 6500
Wire Wire Line
	3550 6200 3550 6100
Wire Wire Line
	3250 6600 3350 6600
Connection ~ 3350 6600
Wire Wire Line
	3350 6600 3450 6600
Connection ~ 3450 6600
Wire Wire Line
	3450 6600 3550 6600
$Comp
L Connector_Generic:Conn_01x04 PULLDOWN1
U 1 1 6042687B
P 4900 5900
F 0 "PULLDOWN1" V 5100 6050 50  0000 R CNN
F 1 "0.1\" 1x4" V 5000 6000 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical" H 4900 5900 50  0001 C CNN
F 3 "~" H 4900 5900 50  0001 C CNN
	1    4900 5900
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R5
U 1 1 60426881
P 4800 6350
F 0 "R5" V 4800 6350 50  0000 C CNN
F 1 "R" V 4800 6350 50  0001 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 4730 6350 50  0001 C CNN
F 3 "~" H 4800 6350 50  0001 C CNN
	1    4800 6350
	1    0    0    -1  
$EndComp
Wire Wire Line
	4800 6200 4800 6100
$Comp
L Device:R R6
U 1 1 60426889
P 4900 6350
F 0 "R6" V 4900 6350 50  0000 C CNN
F 1 "R" V 4900 6350 50  0001 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 4830 6350 50  0001 C CNN
F 3 "~" H 4900 6350 50  0001 C CNN
	1    4900 6350
	1    0    0    -1  
$EndComp
Wire Wire Line
	4900 6200 4900 6100
$Comp
L Device:R R7
U 1 1 60426891
P 5000 6350
F 0 "R7" V 5000 6350 50  0000 C CNN
F 1 "R" V 5000 6350 50  0001 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 4930 6350 50  0001 C CNN
F 3 "~" H 5000 6350 50  0001 C CNN
	1    5000 6350
	1    0    0    -1  
$EndComp
Wire Wire Line
	5000 6200 5000 6100
$Comp
L Device:R R8
U 1 1 60426899
P 5100 6350
F 0 "R8" V 5100 6350 50  0000 C CNN
F 1 "R" V 5100 6350 50  0001 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 5030 6350 50  0001 C CNN
F 3 "~" H 5100 6350 50  0001 C CNN
	1    5100 6350
	1    0    0    -1  
$EndComp
Wire Wire Line
	5100 6200 5100 6100
Wire Wire Line
	3550 6600 3750 6600
Wire Wire Line
	4050 6100 4050 6600
Connection ~ 3550 6600
Wire Wire Line
	3950 6100 3950 6600
Connection ~ 3950 6600
Wire Wire Line
	3950 6600 4050 6600
Wire Wire Line
	3850 6100 3850 6600
Connection ~ 3850 6600
Wire Wire Line
	3850 6600 3950 6600
Wire Wire Line
	3750 6100 3750 6600
Connection ~ 3750 6600
Wire Wire Line
	3750 6600 3850 6600
Text Label 3550 6600 0    50   ~ 0
VCC
$Comp
L Device:R R1
U 1 1 603CD90C
P 3250 6350
F 0 "R1" V 3250 6350 50  0000 C CNN
F 1 "R" V 3250 6350 50  0001 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 3180 6350 50  0001 C CNN
F 3 "~" H 3250 6350 50  0001 C CNN
	1    3250 6350
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x02 PWR1
U 1 1 604FEFCF
P 2450 5900
F 0 "PWR1" H 2750 5900 50  0000 R CNN
F 1 "JST-XH" H 2800 5800 50  0000 R CNN
F 2 "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical" H 2450 5900 50  0001 C CNN
F 3 "~" H 2450 5900 50  0001 C CNN
	1    2450 5900
	0    -1   -1   0   
$EndComp
Text Label 2450 6350 1    50   ~ 0
VCC
Text Label 2550 6350 1    50   ~ 0
GND
$Comp
L Connector_Generic:Conn_01x02 PWR2
U 1 1 6051B38D
P 2750 5900
F 0 "PWR2" H 3050 5900 50  0000 R CNN
F 1 "JST-XH" H 3100 5800 50  0000 R CNN
F 2 "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical" H 2750 5900 50  0001 C CNN
F 3 "~" H 2750 5900 50  0001 C CNN
	1    2750 5900
	0    -1   -1   0   
$EndComp
Text Label 2750 6350 1    50   ~ 0
VCC
Text Label 2850 6350 1    50   ~ 0
GND
Text Label 2100 2600 0    50   ~ 0
GND
Wire Wire Line
	2050 2700 2500 2700
Text Label 2100 2700 0    50   ~ 0
BUS_VCC
$Comp
L Connector_Generic:Conn_01x02 BUSPWR_EN1
U 1 1 60556D43
P 1900 5900
F 0 "BUSPWR_EN1" H 2400 5900 50  0000 R CNN
F 1 "0.1\" 1x2" H 2300 5800 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 1900 5900 50  0001 C CNN
F 3 "~" H 1900 5900 50  0001 C CNN
	1    1900 5900
	0    -1   -1   0   
$EndComp
Text Label 1900 6450 1    50   ~ 0
BUS_VCC
Wire Wire Line
	1900 6100 1900 6450
Text Label 2000 6450 1    50   ~ 0
VCC
Wire Wire Line
	2000 6600 2450 6600
Wire Wire Line
	2000 6100 2000 6600
Connection ~ 3250 6600
Wire Wire Line
	2450 6100 2450 6600
Connection ~ 2450 6600
Wire Wire Line
	2450 6600 2750 6600
Wire Wire Line
	2750 6100 2750 6600
Connection ~ 2750 6600
Wire Wire Line
	2750 6600 3250 6600
Wire Wire Line
	2550 6800 2850 6800
Wire Wire Line
	2550 6100 2550 6800
Wire Wire Line
	2850 6100 2850 6800
Connection ~ 2850 6800
Wire Wire Line
	2850 6800 4300 6800
Wire Wire Line
	5100 6500 5100 6800
Wire Wire Line
	5000 6500 5000 6800
Connection ~ 5000 6800
Wire Wire Line
	5000 6800 5100 6800
Wire Wire Line
	4900 6500 4900 6800
Connection ~ 4900 6800
Wire Wire Line
	4900 6800 5000 6800
Wire Wire Line
	4800 6500 4800 6800
Connection ~ 4800 6800
Wire Wire Line
	4800 6800 4900 6800
Wire Wire Line
	4600 6100 4600 6800
Connection ~ 4600 6800
Wire Wire Line
	4600 6800 4800 6800
Wire Wire Line
	4500 6100 4500 6800
Connection ~ 4500 6800
Wire Wire Line
	4500 6800 4600 6800
Wire Wire Line
	4400 6100 4400 6800
Connection ~ 4400 6800
Wire Wire Line
	4400 6800 4500 6800
Wire Wire Line
	4300 6100 4300 6800
Connection ~ 4300 6800
Wire Wire Line
	4300 6800 4400 6800
Text Label 3550 6800 0    50   ~ 0
GND
$EndSCHEMATC
