#!/bin/env python3
# -*-coding: utf-8 -*-


from construct import (
    Struct,
    Const,
    Int8un,
    Int16un,
    Padding,
    Int32un,
    Int64un,
    ConstructError,
)
import sys


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} [a.out]")
        exit(1)

    with open(sys.argv[1], "rb") as f:
        bytes = f.read()
        format = Struct(
            "signature" / Const(b"\x7fELF"),
            "_class" / Int8un,
            "endian" / Int8un,
            "version" / Int8un,
            "abi" / Int8un,
            Padding(8),
            "type" / Int16un,
            "machine" / Int16un,
            "version" / Int32un,
            "entry_point" / Int64un,
            "program_header_offset" / Int64un,
            "section_header_offset" / Int64un,
            "flags" / Int32un,
            "header_size" / Int16un,
            "entry_size" / Int16un,
            "entry_count" / Int16un,
            "section_size" / Int16un,
            "section_count" / Int16un,
            "section_names_index" / Int16un,
        )
        try:
            data = format.parse(bytes)
        except ConstructError as e:
            print(e)
            exit(1)

        print("\n***ELF HEADER***")

        print(f"Class: {e_class[data._class]}")

        if data.endian in e_endian.keys():
            print(f"{sys.argv[1]} is {e_endian[data.endian]} endian.")
        else:
            print(f"e_endian is not defined: {data.endian}")

        print(f"Version: {data.version}")

        print(f"ABI: {e_osabi[data.abi]}")

        if data.machine in e_machine.keys():
            print(f"Machine: {e_machine[data.machine]}")
        else:
            print(f"e_machine is not defined: {data.machine}")

        if data.type in e_type.keys():
            print(f"Type: {e_type[data.type]}")
        else:
            print(f"e_type is not defined: {data.type}")

        print(f"Entry point: {hex(data.entry_point)}")

        print(f"Program header offset: {hex(data.program_header_offset)}")

        print (f"Section header offset: {hex(data.section_header_offset)}")

        print(f"Flags: {hex(data.flags)}")

        print(f"Header size: {hex(data.header_size)} ({int(data.header_size)} bytes)")

        print(f"Entry size: {hex(data.entry_size)} ({int(data.entry_size)} bytes per program table header entry)")

        print(f"Entry count: {hex(data.entry_count)} ({int(data.entry_count)})")

        print(f"Section size: {hex(data.section_size)} ({int(data.section_size)} bytes per section header table entry)")

        print(f"Section count: {hex(data.section_count)} ({int(data.section_count)})")

        print(f"Index with section names: {hex(data.section_names_index)}")

        # program header struct
        ph_format = Struct(
            "type" / Int32un,
            "flags" / Int32un,
            "offset" / Int64un,
            "virtual_address" / Int64un,
            "physical_address" / Int64un,
            "size_file" / Int64un,
            "size_memory" / Int64un,
            "alignment" / Int64un,
        )
        
        
        # section header struct
        sh_format = Struct(
            "name" / Int32un, 
            "type" / Int64un,
            "flags" / Int64un,
            "virtual_address" / Int64un, # virtual address of section in memory
            "offset" / Int64un, 
            "size" / Int32un,
            "link_index" / Int32un, # contains section index of associated section
            "info" / Int32un, # contains extra info about section
            "address_align" / Int64un, # required alignment
            "entry_size" / Int64un, # size for fized size entries
        )
        
        print("\n***PROGRAM HEADER TABLE***")

        
        for i in range(int(data.entry_count)):

            try:
                f.seek(0x40 + 0x38*i,0)
                bytes = f.read()
                ph_data = ph_format.parse(bytes)
            except ConstructError as e:
                print(e)
                exit(1)

            if ph_data.type in e_ph_type.keys():
                print(f"Type: {e_ph_type[ph_data.type]}")
            else:
                print(f"e_type is not defined: {ph_data.type}")
        
            if ph_data.flags in e_ph_flags.keys():
                print(f"Flags: {e_ph_flags[ph_data.flags]}")
            else:
                print(f"e_ph_type is not defined: {ph_data.flags}")

            print(f"Offset: {hex(ph_data.offset)}")

            print(f"Virtual Addr: {hex(ph_data.virtual_address)}")

            print(f"Alignment: {hex(ph_data.alignment)}")

            print()
        




def hexdump(b: bytes) -> None:
    import binascii

    i = 0
    while i < len(b):
        for _ in range(4):
            block = b[i : i + 8]
            if block:
                print(binascii.hexlify(block), end=" ")
            i += 8
            print()


# ELF Header Format Dictionaries
# Referenced from https://www.sco.com/developers/gabi/latest/ch4.eheader.html

e_endian = {
    1: "Little",
    2: "Big",
}

e_class = {
    1: "32-bit",
    2: "64-bit",
}

e_osabi = {
    0: "System V",
}

# TODO: determine if the OS and processor specific values are needed
e_type = {
    0x0000: "No file type",
    0x0001: "Relocatable file",
    0x0002: "Executable file",
    0x0003: "Shared object file",
    0x0004: "Core file",
    0xFE00: "Operating system-specific",
    0xFEFF: "Operating system-specific",
    0xFF00: "Processor-specific",
    0xFFFF: "Processor-specific",
}

e_machine = {
    0: "No machine",
    1: "AT&T WE 32100",
    2: "SPARC",
    3: "Intel 80386",
    4: "Motorola 68000",
    5: "Motorola 88000",
    6: "Intel MCU",
    7: "Intel 80860",
    8: "MIPS I Architecture",
    9: "IBM System/370 Processor",
    10: "MIPS RS3000 Little-endian",
    11 - 14: "Reserved for future use",
    15: "Hewlett-Packard PA-RISC",
    16: "Reserved for future use",
    17: "Fujitsu VPP500",
    18: "Enhanced instruction set SPARC",
    19: "Intel 80960",
    20: "PowerPC",
    21: "64-bit PowerPC",
    22: "IBM System/390 Processor",
    23: "IBM SPU/SPC",
    24 - 35: "Reserved for future use",
    36: "NEC V800",
    37: "Fujitsu FR20",
    38: "TRW RH-32",
    39: "Motorola RCE",
    40: "ARM 32-bit architecture (AARCH32)",
    41: "Digital Alpha",
    42: "Hitachi SH",
    43: "SPARC Version 9",
    44: "Siemens TriCore embedded processor",
    45: "Argonaut RISC Core, Argonaut Technologies Inc.",
    46: "Hitachi H8/300",
    47: "Hitachi H8/300H",
    48: "Hitachi H8S",
    49: "Hitachi H8/500",
    50: "Intel IA-64 processor architecture",
    51: "Stanford MIPS-X",
    52: "Motorola ColdFire",
    53: "Motorola M68HC12",
    54: "Fujitsu MMA Multimedia Accelerator",
    55: "Siemens PCP",
    56: "Sony nCPU embedded RISC processor",
    57: "Denso NDR1 microprocessor",
    58: "Motorola Star*Core processor",
    59: "Toyota ME16 processor",
    60: "STMicroelectronics ST100 processor",
    61: "Advanced Logic Corp. TinyJ embedded processor family",
    62: "AMD x86-64 architecture",
    63: "Sony DSP Processor",
    64: "Digital Equipment Corp. PDP-10",
    65: "Digital Equipment Corp. PDP-11",
    66: "Siemens FX66 microcontroller",
    67: "STMicroelectronics ST9+ 8/16 bit microcontroller",
    68: "STMicroelectronics ST7 8-bit microcontroller",
    69: "Motorola MC68HC16 Microcontroller",
    70: "Motorola MC68HC11 Microcontroller",
    71: "Motorola MC68HC08 Microcontroller",
    72: "Motorola MC68HC05 Microcontroller",
    73: "Silicon Graphics SVx",
    74: "STMicroelectronics ST19 8-bit microcontroller",
    75: "Digital VAX",
    76: "Axis Communications 32-bit embedded processor",
    77: "Infineon Technologies 32-bit embedded processor",
    78: "Element 14 64-bit DSP Processor",
    79: "LSI Logic 16-bit DSP Processor",
    80: "Donald Knuth's educational 64-bit processor",
    81: "Harvard University machine-independent object files",
    82: "SiTera Prism",
    83: "Atmel AVR 8-bit microcontroller",
    84: "Fujitsu FR30",
    85: "Mitsubishi D10V",
    86: "Mitsubishi D30V",
    87: "NEC v850",
    88: "Mitsubishi M32R",
    89: "Matsushita MN10300",
    90: "Matsushita MN10200",
    91: "picoJava",
    92: "OpenRISC 32-bit embedded processor",
    93: "ARC International ARCompact processor (old spelling/synonym: EM_ARC_A5)",
    94: "Tensilica Xtensa Architecture",
    95: "Alphamosaic VideoCore processor",
    96: "Thompson Multimedia General Purpose Processor",
    97: "National Semiconductor 32000 series",
    98: "Tenor Network TPC processor",
    99: "Trebia SNP 1000 processor",
    100: "STMicroelectronics (www.st.com) ST200 microcontroller",
    101: "Ubicom IP2xxx microcontroller family",
    102: "MAX Processor",
    103: "National Semiconductor CompactRISC microprocessor",
    104: "Fujitsu F2MC16",
    105: "Texas Instruments embedded microcontroller msp430",
    106: "Analog Devices Blackfin (DSP) processor",
    107: "S1C33 Family of Seiko Epson processors",
    108: "Sharp embedded microprocessor",
    109: "Arca RISC Microprocessor",
    110: "Microprocessor series from PKU-Unity Ltd. and MPRC of Peking University",
    111: "eXcess: 16/32/64-bit configurable embedded CPU",
    112: "Icera Semiconductor Inc. Deep Execution Processor",
    113: "Altera Nios II soft-core processor",
    114: "National Semiconductor CompactRISC CRX microprocessor",
    115: "Motorola XGATE embedded processor",
    116: "Infineon C16x/XC16x processor",
    117: "Renesas M16C series microprocessors",
    118: "Microchip Technology dsPIC30F Digital Signal Controller",
    119: "Freescale Communication Engine RISC core",
    120: "Renesas M32C series microprocessors",
    121 - 130: "Reserved for future use",
    131: "Altium TSK3000 core",
    132: "Freescale RS08 embedded processor",
    133: "Analog Devices SHARC family of 32-bit DSP processors",
    134: "Cyan Technology eCOG2 microprocessor",
    135: "Sunplus S+core7 RISC processor",
    136: "New Japan Radio (NJR) 24-bit DSP Processor",
    137: "Broadcom VideoCore III processor",
    138: "RISC processor for Lattice FPGA architecture",
    139: "Seiko Epson C17 family",
    140: "The Texas Instruments TMS320C6000 DSP family",
    141: "The Texas Instruments TMS320C2000 DSP family",
    142: "The Texas Instruments TMS320C55x DSP family",
    143: "Texas Instruments Application Specific RISC Processor, 32bit fetch",
    144: "Texas Instruments Programmable Realtime Unit",
    145 - 159: "Reserved for future use",
    160: "STMicroelectronics 64bit VLIW Data Signal Processor",
    161: "Cypress M8C microprocessor",
    162: "Renesas R32C series microprocessors",
    163: "NXP Semiconductors TriMedia architecture family",
    164: "QUALCOMM DSP6 Processor",
    165: "Intel 8051 and variants",
    166: "STMicroelectronics STxP7x family of configurable and extensible RISC processors",
    167: "Andes Technology compact code size embedded RISC processor family",
    168: "Cyan Technology eCOG1X family",
    169: "Dallas Semiconductor MAXQ30 Core Micro-controllers",
    170: "New Japan Radio (NJR) 16-bit DSP Processor",
    171: "M2000 Reconfigurable RISC Microprocessor",
    172: "Cray Inc. NV2 vector architecture",
    173: "Renesas RX family",
    174: "Imagination Technologies META processor architecture",
    175: "MCST Elbrus general purpose hardware architecture",
    176: "Cyan Technology eCOG16 family",
    177: "National Semiconductor CompactRISC CR16 16-bit microprocessor",
    178: "Freescale Extended Time Processing Unit",
    179: "Infineon Technologies SLE9X core",
    180: "Intel L10M",
    181: "Intel K10M",
    182: "Reserved for future Intel use",
    183: "ARM 64-bit architecture (AARCH64)",
    184: "Reserved for future ARM use",
    185: "Atmel Corporation 32-bit microprocessor family",
    186: "STMicroeletronics STM8 8-bit microcontroller",
    187: "Tilera TILE64 multicore architecture family",
    188: "Tilera TILEPro multicore architecture family",
    189: "Xilinx MicroBlaze 32-bit RISC soft processor core",
    190: "NVIDIA CUDA architecture",
    191: "Tilera TILE-Gx multicore architecture family",
    192: "CloudShield architecture family",
    193: "KIPO-KAIST Core-A 1st generation processor family",
    194: "KIPO-KAIST Core-A 2nd generation processor family",
    195: "Synopsys ARCompact V2",
    196: "Open8 8-bit RISC soft processor core",
    197: "Renesas RL78 family",
    198: "Broadcom VideoCore V processor",
    199: "Renesas 78KOR family",
    200: "Freescale 56800EX Digital Signal Controller (DSC)",
    201: "Beyond BA1 CPU architecture",
    202: "Beyond BA2 CPU architecture",
    203: "XMOS xCORE processor family",
    204: "Microchip 8-bit PIC(r) family",
    205 - 209: "Reserved by Intel",
    210: "KM211 KM32 32-bit processor",
    211: "KM211 KMX32 32-bit processor",
    212: "KM211 KMX16 16-bit processor",
    213: "KM211 KMX8 8-bit processor",
    214: "KM211 KVARC processor",
    215: "Paneve CDP architecture family",
    216: "Cognitive Smart Memory Processor",
    217: "Bluechip Systems CoolEngine",
    218: "Nanoradio Optimized RISC",
    219: "CSR Kalimba architecture family",
    220: "Zilog Z80",
    221: "Controls and Data Services VISIUMcore processor",
    222: "FTDI Chip FT32 high performance 32-bit RISC architecture",
    223: "Moxie processor family",
    224: "AMD GPU architecture",
    243: "RISC-V",
}

# Program Header Format dictionaries
e_ph_type = {
    0x00: "Unused entry",
    0x01: "Loadable segment",
    0x02: "Dynamic linking information",
    0x03: "Interpreter information",
    0x04: "Auxiliary information",
    0x05: "Reserved",
    0x06: "Segment containing program header table itself",
    0x07: "Thread-Local Storage template",
    0x60000000: "Reserved inclusive range",
    0x6FFFFFFF: "Reserved inclusive range",
    0x70000000: "Reserved inclusive range",
    0x7FFFFFFF: "Reserved inclusive range",
}

e_ph_flags = {
    0x01: "--X",
    0x02: "-W-",
    0x03: "-WX",
    0x04: "R--",
    0x05: "R-X",
    0x06: "RW-",
    0x07: "RWX",
}


if __name__ == "__main__":
    main()
