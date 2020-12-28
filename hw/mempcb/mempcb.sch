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
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x39_P2.54mm_Vertical" H 1850 2900 50  0001 C CNN
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
F 2 "mempcb:DIP-32_W15.24mm_ZIF_Socket_LongPads" H 5500 2100 50  0001 C CNN
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
P 6500 4150
F 0 "W4_2" H 6400 4700 50  0000 L CNN
F 1 "0.1\" 1x8" H 6350 4600 50  0000 L CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical" H 6500 4150 50  0001 C CNN
F 3 "~" H 6500 4150 50  0001 C CNN
	1    6500 4150
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x08 W4_1
U 1 1 5FED086C
P 4500 4150
F 0 "W4_1" H 4418 4667 50  0000 C CNN
F 1 "0.1\" 1x8" H 4418 4576 50  0000 C CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical" H 4500 4150 50  0001 C CNN
F 3 "~" H 4500 4150 50  0001 C CNN
	1    4500 4150
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
	4750 2800 4950 2800
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
	6250 1300 6200 1300
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
P 5500 4150
F 0 "U4" H 5500 4717 50  0000 C CNN
F 1 "74LS138" H 5500 4626 50  0000 C CNN
F 2 "Package_DIP:DIP-16_W7.62mm_Socket_LongPads" H 5500 4150 50  0001 C CNN
F 3 "http://www.ti.com/lit/gpn/sn74LS138" H 5500 4150 50  0001 C CNN
	1    5500 4150
	1    0    0    -1  
$EndComp
Wire Wire Line
	6000 3850 6050 3850
Wire Wire Line
	6000 3950 6300 3950
Wire Wire Line
	6000 4050 6300 4050
Wire Wire Line
	6000 4150 6300 4150
Wire Wire Line
	6000 4250 6300 4250
Wire Wire Line
	6000 4350 6300 4350
Wire Wire Line
	6000 4450 6300 4450
Wire Wire Line
	6000 4550 6300 4550
Wire Wire Line
	5000 3850 4700 3850
Wire Wire Line
	5000 3950 4700 3950
Wire Wire Line
	5000 4050 4700 4050
Wire Wire Line
	5000 4150 4700 4150
Wire Wire Line
	5000 4250 4700 4250
Wire Wire Line
	5000 4350 4700 4350
Wire Wire Line
	5000 4450 4700 4450
Wire Wire Line
	5000 4550 4950 4550
Text Label 4750 4550 0    50   ~ 0
GND
Text Label 6050 3850 0    50   ~ 0
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
L Connector_Generic:Conn_01x04 GND/VCC1
U 1 1 5FED18C8
P 9300 4850
F 0 "GND/VCC1" V 9500 5000 50  0000 R CNN
F 1 "0.1\" 1x4" V 9400 4950 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical" H 9300 4850 50  0001 C CNN
F 3 "~" H 9300 4850 50  0001 C CNN
	1    9300 4850
	0    -1   -1   0   
$EndComp
$Comp
L Connector_Generic:Conn_01x04 PULLUP1
U 1 1 6032F1DA
P 8800 4850
F 0 "PULLUP1" V 9000 4950 50  0000 R CNN
F 1 "0.1\" 1x4" V 8900 4950 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical" H 8800 4850 50  0001 C CNN
F 3 "~" H 8800 4850 50  0001 C CNN
	1    8800 4850
	0    -1   -1   0   
$EndComp
Wire Wire Line
	8700 5550 8700 5450
Wire Wire Line
	8700 5150 8700 5050
$Comp
L Device:R R2
U 1 1 603E796E
P 8800 5300
F 0 "R2" V 8800 5300 50  0000 C CNN
F 1 "R" V 8800 5300 50  0001 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 8730 5300 50  0001 C CNN
F 3 "~" H 8800 5300 50  0001 C CNN
	1    8800 5300
	1    0    0    -1  
$EndComp
Wire Wire Line
	8800 5550 8800 5450
Wire Wire Line
	8800 5150 8800 5050
$Comp
L Device:R R3
U 1 1 60400026
P 8900 5300
F 0 "R3" V 8900 5300 50  0000 C CNN
F 1 "R" V 8900 5300 50  0001 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 8830 5300 50  0001 C CNN
F 3 "~" H 8900 5300 50  0001 C CNN
	1    8900 5300
	1    0    0    -1  
$EndComp
Wire Wire Line
	8900 5550 8900 5450
Wire Wire Line
	8900 5150 8900 5050
$Comp
L Device:R R4
U 1 1 6040C3DC
P 9000 5300
F 0 "R4" V 9000 5300 50  0000 C CNN
F 1 "R" V 9000 5300 50  0001 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 8930 5300 50  0001 C CNN
F 3 "~" H 9000 5300 50  0001 C CNN
	1    9000 5300
	1    0    0    -1  
$EndComp
Wire Wire Line
	9000 5550 9000 5450
Wire Wire Line
	9000 5150 9000 5050
Wire Wire Line
	8700 5550 8800 5550
Connection ~ 8800 5550
Wire Wire Line
	8800 5550 8900 5550
Connection ~ 8900 5550
Wire Wire Line
	8900 5550 9000 5550
$Comp
L Connector_Generic:Conn_01x04 PULLDOWN1
U 1 1 6042687B
P 9800 4850
F 0 "PULLDOWN1" V 10000 5000 50  0000 R CNN
F 1 "0.1\" 1x4" V 9900 4950 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical" H 9800 4850 50  0001 C CNN
F 3 "~" H 9800 4850 50  0001 C CNN
	1    9800 4850
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R5
U 1 1 60426881
P 9700 5300
F 0 "R5" V 9700 5300 50  0000 C CNN
F 1 "R" V 9700 5300 50  0001 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 9630 5300 50  0001 C CNN
F 3 "~" H 9700 5300 50  0001 C CNN
	1    9700 5300
	1    0    0    -1  
$EndComp
Wire Wire Line
	9700 5150 9700 5050
$Comp
L Device:R R6
U 1 1 60426889
P 9800 5300
F 0 "R6" V 9800 5300 50  0000 C CNN
F 1 "R" V 9800 5300 50  0001 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 9730 5300 50  0001 C CNN
F 3 "~" H 9800 5300 50  0001 C CNN
	1    9800 5300
	1    0    0    -1  
$EndComp
Wire Wire Line
	9800 5150 9800 5050
$Comp
L Device:R R7
U 1 1 60426891
P 9900 5300
F 0 "R7" V 9900 5300 50  0000 C CNN
F 1 "R" V 9900 5300 50  0001 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 9830 5300 50  0001 C CNN
F 3 "~" H 9900 5300 50  0001 C CNN
	1    9900 5300
	1    0    0    -1  
$EndComp
Wire Wire Line
	9900 5150 9900 5050
$Comp
L Device:R R8
U 1 1 60426899
P 10000 5300
F 0 "R8" V 10000 5300 50  0000 C CNN
F 1 "R" V 10000 5300 50  0001 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 9930 5300 50  0001 C CNN
F 3 "~" H 10000 5300 50  0001 C CNN
	1    10000 5300
	1    0    0    -1  
$EndComp
Wire Wire Line
	10000 5150 10000 5050
Connection ~ 9000 5550
Text Label 9000 5550 0    50   ~ 0
VCC
$Comp
L Device:R R1
U 1 1 603CD90C
P 8700 5300
F 0 "R1" V 8700 5300 50  0000 C CNN
F 1 "R" V 8700 5300 50  0001 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal" V 8630 5300 50  0001 C CNN
F 3 "~" H 8700 5300 50  0001 C CNN
	1    8700 5300
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x02 PWR1
U 1 1 604FEFCF
P 7900 4850
F 0 "PWR1" H 8200 4850 50  0000 R CNN
F 1 "JST-XH" H 8250 4750 50  0000 R CNN
F 2 "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical" H 7900 4850 50  0001 C CNN
F 3 "~" H 7900 4850 50  0001 C CNN
	1    7900 4850
	0    -1   -1   0   
$EndComp
Text Label 7900 5300 1    50   ~ 0
VCC
Text Label 8000 5300 1    50   ~ 0
GND
$Comp
L Connector_Generic:Conn_01x02 PWR2
U 1 1 6051B38D
P 8200 4850
F 0 "PWR2" H 8500 4850 50  0000 R CNN
F 1 "JST-XH" H 8550 4750 50  0000 R CNN
F 2 "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical" H 8200 4850 50  0001 C CNN
F 3 "~" H 8200 4850 50  0001 C CNN
	1    8200 4850
	0    -1   -1   0   
$EndComp
Text Label 8200 5300 1    50   ~ 0
VCC
Text Label 8300 5300 1    50   ~ 0
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
P 7350 4850
F 0 "BUSPWR_EN1" H 7850 4850 50  0000 R CNN
F 1 "0.1\" 1x2" H 7750 4750 50  0000 R CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 7350 4850 50  0001 C CNN
F 3 "~" H 7350 4850 50  0001 C CNN
	1    7350 4850
	0    -1   -1   0   
$EndComp
Text Label 7350 5400 1    50   ~ 0
BUS_VCC
Wire Wire Line
	7350 5050 7350 5400
Text Label 7450 5400 1    50   ~ 0
VCC
Wire Wire Line
	7450 5550 7900 5550
Wire Wire Line
	7450 5050 7450 5550
Connection ~ 8700 5550
Wire Wire Line
	7900 5050 7900 5550
Connection ~ 7900 5550
Wire Wire Line
	7900 5550 8200 5550
Wire Wire Line
	8200 5050 8200 5550
Connection ~ 8200 5550
Wire Wire Line
	8200 5550 8700 5550
Wire Wire Line
	8000 5750 8300 5750
Wire Wire Line
	8000 5050 8000 5750
Wire Wire Line
	8300 5050 8300 5750
Connection ~ 8300 5750
Wire Wire Line
	10000 5450 10000 5750
Wire Wire Line
	9900 5450 9900 5750
Connection ~ 9900 5750
Wire Wire Line
	9900 5750 10000 5750
Wire Wire Line
	9800 5450 9800 5750
Connection ~ 9800 5750
Wire Wire Line
	9800 5750 9900 5750
Wire Wire Line
	9700 5450 9700 5750
Wire Wire Line
	9700 5750 9800 5750
Text Label 9000 5750 0    50   ~ 0
GND
Wire Wire Line
	5350 5000 4950 5000
Wire Wire Line
	4950 5000 4950 4550
Connection ~ 4950 4550
Wire Wire Line
	4950 4550 4700 4550
Wire Wire Line
	5650 5000 6050 5000
Wire Wire Line
	6050 5000 6050 3850
Connection ~ 6050 3850
Wire Wire Line
	6050 3850 6300 3850
$Comp
L Device:C C2
U 1 1 5FF0AFCA
P 5500 5000
F 0 "C2" V 5248 5000 50  0000 C CNN
F 1 ".1μF" V 5339 5000 50  0000 C CNN
F 2 "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm" H 5538 4850 50  0001 C CNN
F 3 "~" H 5500 5000 50  0001 C CNN
	1    5500 5000
	0    1    1    0   
$EndComp
$Comp
L Device:C C1
U 1 1 5FF2C1A0
P 5500 3200
F 0 "C1" V 5248 3200 50  0000 C CNN
F 1 ".1μF" V 5339 3200 50  0000 C CNN
F 2 "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm" H 5538 3050 50  0001 C CNN
F 3 "~" H 5500 3200 50  0001 C CNN
	1    5500 3200
	0    1    1    0   
$EndComp
Wire Wire Line
	5350 3200 4950 3200
Wire Wire Line
	4950 3200 4950 2800
Connection ~ 4950 2800
Wire Wire Line
	4950 2800 5000 2800
Wire Wire Line
	5650 3200 6200 3200
Wire Wire Line
	6200 3200 6200 1300
Connection ~ 6200 1300
Wire Wire Line
	6200 1300 6000 1300
$Comp
L Connector_Generic:Conn_01x08 W5_2
U 1 1 5FF51E6E
P 6500 5800
F 0 "W5_2" H 6400 6350 50  0000 L CNN
F 1 "0.1\" 1x8" H 6350 6250 50  0000 L CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical" H 6500 5800 50  0001 C CNN
F 3 "~" H 6500 5800 50  0001 C CNN
	1    6500 5800
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x08 W5_1
U 1 1 5FF51E74
P 4500 5800
F 0 "W5_1" H 4418 6317 50  0000 C CNN
F 1 "0.1\" 1x8" H 4418 6226 50  0000 C CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical" H 4500 5800 50  0001 C CNN
F 3 "~" H 4500 5800 50  0001 C CNN
	1    4500 5800
	-1   0    0    -1  
$EndComp
$Comp
L mempcb:74LS138 U5
U 1 1 5FF51E7A
P 5500 5800
F 0 "U5" H 5500 6367 50  0000 C CNN
F 1 "74LS138" H 5500 6276 50  0000 C CNN
F 2 "Package_DIP:DIP-16_W7.62mm_Socket_LongPads" H 5500 5800 50  0001 C CNN
F 3 "http://www.ti.com/lit/gpn/sn74LS138" H 5500 5800 50  0001 C CNN
	1    5500 5800
	1    0    0    -1  
$EndComp
Wire Wire Line
	6000 5500 6050 5500
Wire Wire Line
	6000 5600 6300 5600
Wire Wire Line
	6000 5700 6300 5700
Wire Wire Line
	6000 5800 6300 5800
Wire Wire Line
	6000 5900 6300 5900
Wire Wire Line
	6000 6000 6300 6000
Wire Wire Line
	6000 6100 6300 6100
Wire Wire Line
	6000 6200 6300 6200
Wire Wire Line
	5000 5500 4700 5500
Wire Wire Line
	5000 5600 4700 5600
Wire Wire Line
	5000 5700 4700 5700
Wire Wire Line
	5000 5800 4700 5800
Wire Wire Line
	5000 5900 4700 5900
Wire Wire Line
	5000 6000 4700 6000
Wire Wire Line
	5000 6100 4700 6100
Wire Wire Line
	5000 6200 4950 6200
Text Label 4750 6200 0    50   ~ 0
GND
Text Label 6050 5500 0    50   ~ 0
VCC
Wire Wire Line
	5350 6650 4950 6650
Wire Wire Line
	4950 6650 4950 6200
Connection ~ 4950 6200
Wire Wire Line
	4950 6200 4700 6200
Wire Wire Line
	5650 6650 6050 6650
Wire Wire Line
	6050 6650 6050 5500
Connection ~ 6050 5500
Wire Wire Line
	6050 5500 6300 5500
$Comp
L Device:C C3
U 1 1 5FF51E9A
P 5500 6650
F 0 "C3" V 5248 6650 50  0000 C CNN
F 1 ".1μF" V 5339 6650 50  0000 C CNN
F 2 "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm" H 5538 6500 50  0001 C CNN
F 3 "~" H 5500 6650 50  0001 C CNN
	1    5500 6650
	0    1    1    0   
$EndComp
Wire Wire Line
	8300 5750 9200 5750
Wire Wire Line
	9500 5550 9500 5050
Wire Wire Line
	9000 5550 9400 5550
Wire Wire Line
	9400 5050 9400 5550
Connection ~ 9400 5550
Wire Wire Line
	9400 5550 9500 5550
Wire Wire Line
	9200 5050 9200 5750
Connection ~ 9200 5750
Wire Wire Line
	9200 5750 9300 5750
Wire Wire Line
	9300 5050 9300 5750
Wire Wire Line
	9700 5750 9300 5750
Connection ~ 9700 5750
Connection ~ 9300 5750
$EndSCHEMATC
