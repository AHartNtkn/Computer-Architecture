"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Initialize our eight registers.
        self.R = [0] * 8
        self.R[7] = 0xF4
        # Initialize program counter
        self.PC = 0
        # Initialize instruction register.
        self.IR = 0
        # Initialize memory address register.
        self.MAR = 0
        # Initialize Memory Data Register
        self.MDR = 0
        # Initialize flags 
        self.FL = 0

        # Initialize memory
        self.RAM = [0] * 256

        # Allow interupts
        self.interupts_enabled = True

        # The system is not halted at startup
        self.HALT = False

        # The program counter is not set by an opcode by default
        self.PC_SET = False

        # Set registers for storing operands
        self.opA = 0
        self.opB = 0

        

    # Named register methods
    def regOP(self, f, i):
        """ Perform operation on register """
        if 0 <= i and i < 8:
            self.R[i] = f(self.R[i]) & 255
    def register(self, num):
        """ Get register associated with 8 bit input """
        return self.R[num & 7]
    @property
    def IM(self):
        return self.R[5]
    def set_IM(self, value):
        self.R[5] = value
    @property
    def IS(self):
        return self.R[6]
    def set_IS(self, value):
        self.R[6] = value

    # Named flag methods
    def flag(self, j):
        """ Get jth flag """
        i = j & 7

        return (self.FL & 2 ** i) >> i
    def set_flag(self, j, b):
        """ Set jth flag to b """
        i = j & 7

        # zero ith bit
        self.FL -= self.FL & 2 ** i
        if b:
            # set ith bit to 1
            self.FL += 2 ** i
    @property
    def L(self):
        # Less-than: during a CMP, set to 1 if registerA
        # is less than registerB, zero otherwise.
        return self.flag(2)
    def set_L(self, b):
        self.set_flag(2, b)
    @property
    def G(self):
        # Greater-than: during a CMP, set to 1 if
        # registerA is greater than registerB, zero otherwise.
        return self.flag(1)
    def set_G(self, b):
        self.set_flag(1, b)
    @property
    def E(self):
        # Equal: during a CMP, set to 1 if registerA is
        # equal to registerB, zero otherwise.
        return self.flag(0)
    def set_E(self, b):
        self.set_flag(0, b)

    # Named RAM methods
    @property
    def I7(self):
        return self.RAM[255]
    @property
    def I6(self):
        return self.RAM[254]
    @property
    def I5(self):
        return self.RAM[253]
    @property
    def I4(self):
        return self.RAM[252]
    @property
    def I3(self):
        return self.RAM[251]
    @property
    def I2(self):
        return self.RAM[250]
    @property
    def I1(self):
        return self.RAM[249]
    @property
    def I0(self):
        return self.RAM[248]

    @property
    def Key(sefl):
        return self.RAM[244]

    def ram_read(self):
        self.MDR = self.RAM[self.MAR]

    def ram_write(self, value, address):
        self.RAM[self.MAR] = self.MDR

    # Stack related methods.
    @property
    def SP(self):
        return self.R[7]
    def set_SP(self, value):
        self.R[7] = value

    def pop(self):
        val = self.RAM[self.SP]
        self.RAM[self.SP] = 0
        self.set_SP((self.SP + 1) & 255)
        return val

    def push(self, val):
        self.set_SP((self.SP - 1) & 255)
        self.RAM[self.SP] = val & 255
    
    # Opcode Functions:
    def create_opcode_table(self):
        self.opcode_table = {}
        self.opcode_table[0x00] = self.NOP
        self.opcode_table[0x01] = self.HLT
        self.opcode_table[0x11] = self.RET
        self.opcode_table[0x13] = self.IRET
        self.opcode_table[0x45] = self.PUSH
        self.opcode_table[0x46] = self.POP
        self.opcode_table[0x47] = self.PRN
        self.opcode_table[0x48] = self.PRA
        self.opcode_table[0x50] = self.CALL
        self.opcode_table[0x52] = self.INT
        self.opcode_table[0x54] = self.JMP
        self.opcode_table[0x55] = self.JEQ
        self.opcode_table[0x56] = self.JNE
        self.opcode_table[0x57] = self.JGT
        self.opcode_table[0x58] = self.JLT
        self.opcode_table[0x59] = self.JLE
        self.opcode_table[0x5A] = self.JGE
        self.opcode_table[0x65] = self.INC
        self.opcode_table[0x66] = self.DEC
        self.opcode_table[0x69] = self.NOT
        self.opcode_table[0x82] = self.LDI
        self.opcode_table[0x83] = self.LD
        self.opcode_table[0x84] = self.ST
        self.opcode_table[0xA0] = self.ADD
        self.opcode_table[0xA1] = self.SUB
        self.opcode_table[0xA2] = self.MUL
        self.opcode_table[0xA3] = self.DIV
        self.opcode_table[0xA4] = self.MOD
        self.opcode_table[0xA7] = self.CMP
        self.opcode_table[0xA8] = self.AND
        self.opcode_table[0xAA] = self.OR
        self.opcode_table[0xAB] = self.XOR
        self.opcode_table[0xAC] = self.SHL
        self.opcode_table[0xAD] = self.SHR
    
    def NOP(self):
        """ No operation. Do nothing for this instruction. """
        pass
    
    def HLT(self):
        """ Halt the CPU (and exit the emulator). """
        self.HALT = True
    
    def RET(self):
        """
        Return from subroutine.

        Pop the value from the top of the stack and store it in the PC.
        """
        self.PC_SET = True
        self.PC = self.pop() 
    
    def IRET(self):
        """
        Return from an interrupt handler.

        The following steps are executed:

            Registers R6-R0 are popped off the stack in that order.
            The FL register is popped off the stack.
            The return address is popped off the stack and stored in PC.
            Interrupts are re-enabled
        """
        self.PC_SET = True
        self.R[6] = self.pop()
        self.R[5] = self.pop()
        self.R[4] = self.pop()
        self.R[3] = self.pop()
        self.R[2] = self.pop()
        self.R[1] = self.pop()
        self.R[0] = self.pop()
        self.FL = self.pop()
        self.PC = self.pop()
        self.interupts_enabled = True
    
    def PUSH(self):
        """
        Push the value in the given register on the stack.
        """
        self.push(self.R[self.opA & 7])
    
    def POP(self):
        """
        Pop the value at the top of the stack into the given register.
        """
        self.R[self.opA & 7] = self.pop()
    
    def PRN(self):
        """
        Print numerical value stored in the given register.
        """
        print(self.R[self.opA & 7])
    
    def PRA(self):
        """
        Print numerical value stored in the given register.
        """
        print(chr(self.R[self.opA & 7]), end='')
    
    def CALL(self):
        """
        Calls a subroutine (function) at the address stored in the register.

        The address of the instruction directly after CALL is pushed onto
        the stack. This allows us to return to where we left off when the
        subroutine finishes executing.

        The PC is set to the address stored in the given register. We jump
        to that location in RAM and execute the first instruction in the
        subroutine. The PC can move forward or backwards from its current 
        location.
        """
        self.PC_SET = True
        self.push((self.PC + 2) & 255)
        self.PC = self.R[self.opA & 7]
    
    def INT(self):
        """
        Issue the interrupt number stored in the given register.

        This will set the _n_th bit in the IS register to
        the value in the given register.
        """
        # TO DO
        PC_SET = True
        pass
    
    def JMP(self):
        """
        Jump to the address stored in the given register.
        """
        self.PC_SET = True
        self.PC = self.R[self.opA & 7]
    
    def JEQ(self):
        """
        If equal flag is set (true),
        jump to the address stored in the given register.
        """
        if self.E:
            self.PC_SET = True
            self.PC = self.R[self.opA & 7]
    
    def JNE(self):
        """
        If E flag is clear (false, 0),
        jump to the address stored in the given register.
        """
        if not self.E:
            self.PC_SET = True
            self.PC = self.R[self.opA & 7]
    
    def JGT(self):
        """
        If greater-than flag is set (true),
        jump to the address stored in the given register.
        """
        if self.G:
            self.PC_SET = True
            self.PC = self.R[self.opA & 7]
    
    def JLT(self):
        """
        If less-than is set (true),
        jump to the address stored in the given register.
        """
        if self.L:
            self.PC_SET = True
            self.PC = self.R[self.opA & 7]
    
    def JLE(self):
        """
        If less-than flag or equal flag is set (true),
        jump to the address stored in the given register.
        """
        if self.L or self.E:
            self.PC_SET = True
            self.PC = self.R[self.opA & 7]
    
    def JGE(self):
        """
        If greater-than flag or equal flag is set (true),
        jump to the address stored in the given register.
        """
        if self.G or self.E:
            self.PC_SET = True
            self.PC = self.R[self.opA & 7]
    
    def INC(self):
        """
        Increment (add 1 to) the value in the given register.
        """
        self.alu('INC', self.opA, self.opB)
    
    def DEC(self):
        """
        Decrement (subtract 1 from) the value in the given register.
        """
        self.alu('DEC', self.opA, self.opB)
    
    def NOT(self):
        """
        Perform a bitwise-NOT on the value in a register,
        storing the result in the register.
        """
        self.alu('NOT', self.opA, self.opB)
    
    def LDI(self):
        """
        Set the value of a register to an integer.
        """
        self.R[self.opA & 7] = self.opB
    
    def LD(self):
        """
        Loads registerA with the value at the memory address stored in registerB.
        """
        self.MAR = self.R[self.opB & 7]
        self.ram_read()
        self.R[self.opA & 7] = self.MDR
    
    def ST(self):
        """
        Store value in registerB in the address stored in registerA.
        """
        self.MAR = self.R[self.opA & 7]
        self.MDR = self.R[self.opB & 7]
        self.ram_write()
    
    def ADD(self):
        """
        Add the value in two registers and store the result in registerA.
        """
        self.alu('ADD', self.opA, self.opB)
    
    def SUB(self):
        """
        Subtract the value in the second register from the first,
        storing the result in registerA.
        """
        self.alu('SUB', self.opA, self.opB)
    
    def MUL(self):
        """
        Multiply the values in two registers together and store the
        result in registerA.
        """
        self.alu('MUL', self.opA, self.opB)
    
    def DIV(self):
        """
        Divide the value in the first register by the value in the second,
        storing the result in registerA.

        If the value in the second register is 0, the system should print
        an error message and halt.
        """
        self.alu('DIV', self.opA, self.opB)
    
    def MOD(self):
        """
        Divide the value in the first register by the value in the second,
        storing the remainder of the result in registerA.

        If the value in the second register is 0, the system should print
        an error message and halt.
        """
        self.alu('MOD', self.opA, self.opB)
    
    def CMP(self):
        """
        Compare the values in two registers.

        If they are equal, set the Equal E flag to 1, otherwise set it to 0.

        If registerA is less than registerB, set the Less-than L flag to 1,
        otherwise set it to 0.

        If registerA is greater than registerB, set the Greater-than G flag
        to 1, otherwise set it to 0.
        """
        self.alu('CMP', self.opA, self.opB)
    
    def AND(self):
        """
        Perform a bitwise-AND between the values in registerA and
        registerB, storing the result in registerA.
        """
        self.alu('AND', self.opA, self.opB)
    
    def OR(self):
        """
        Perform a bitwise-OR between the values in registerA and
        registerB, storing the result in registerA.
        """
        self.alu('OR', self.opA, self.opB)
    
    def XOR(self):
        """
        Perform a bitwise-XOR between the values in registerA and
        registerB, storing the result in registerA.
        """
        self.alu('XOR', self.opA, self.opB)

    def SHL(self):
        """
        Shift the value in registerA left by the number of bits
        specified in registerB, filling the low bits with 0.
        """
        self.alu('SHL', self.opA, self.opB)
    
    def SHR(self):
        """
        Shift the value in registerA right by the number of bits
        specified in registerB, filling the high bits with 0.
        """
        self.alu('SHR', self.opA, self.opB)

    def create_ALU_table(self):
        self.ALU_table = {}
        self.ALU_table["INC"] = self.ALU_INC
        self.ALU_table["DEC"] = self.ALU_DEC
        self.ALU_table["NOT"] = self.ALU_NOT
        self.ALU_table["ADD"] = self.ALU_ADD
        self.ALU_table["SUB"] = self.ALU_SUB
        self.ALU_table["MUL"] = self.ALU_MUL
        self.ALU_table["DIV"] = self.ALU_DIV
        self.ALU_table["MOD"] = self.ALU_MOD
        self.ALU_table["CMP"] = self.ALU_CMP
        self.ALU_table["AND"] = self.ALU_AND
        self.ALU_table["OR"]  = self.ALU_OR
        self.ALU_table["XOR"] = self.ALU_XOR
        self.ALU_table["SHL"] = self.ALU_SHL
        self.ALU_table["SHR"] = self.ALU_SHR
  
    def ALU_INC(self, reg_a, reg_b):
        self.R[reg_a] = (self.R[reg_a] + 1) & 255

    def ALU_DEC(self, reg_a, reg_b):
        self.R[reg_a] = (self.R[reg_a] - 1) & 255

    def ALU_NOT(self, reg_a, reg_b):
        self.R[reg_a] = ~ self.R[reg_a]

    def ALU_ADD(self, reg_a, reg_b):
        self.R[reg_a] = (self.R[reg_a] + self.R[reg_b]) & 255

    def ALU_SUB(self, reg_a, reg_b):
        self.R[reg_a] = (self.R[reg_a] - self.R[reg_b]) & 255

    def ALU_MUL(self, reg_a, reg_b):
        self.R[reg_a] = (self.R[reg_a] * self.R[reg_b]) & 255

    def ALU_DIV(self, reg_a, reg_b):
        if self.R[reg_b] == 0:
            raise Exception("Division by zero error")

        self.R[reg_a] = self.R[reg_a] // self.R[reg_b]

    def ALU_MOD(self, reg_a, reg_b):
        if self.R[reg_b] == 0:
            raise Exception("Division by zero error")

        self.R[reg_a] = self.R[reg_a] % self.R[reg_b]

    def ALU_CMP(self, reg_a, reg_b):
        self.set_L(False)
        self.set_G(False)
        self.set_E(False)

        if self.R[reg_a] < self.R[reg_b]:
            self.set_L(True)
        elif self.R[reg_a] > self.R[reg_b]:
            self.set_G(True)
        else:
            self.set_E(True)

    def ALU_AND(self, reg_a, reg_b):
        self.R[reg_a] = self.R[reg_a] & self.R[reg_b]

    def ALU_OR(self, reg_a, reg_b):
        self.R[reg_a] = self.R[reg_a] | self.R[reg_b]

    def ALU_XOR(self, reg_a, reg_b):
        self.R[reg_a] = self.R[reg_a] ^ self.R[reg_b]

    def ALU_SHL(self, reg_a, reg_b):
        self.R[reg_a] = (self.R[reg_a] << self.R[reg_b]) & 255

    def ALU_SHR(self, reg_a, reg_b):
        self.R[reg_a] = self.R[reg_a] >> self.R[reg_b]

    def alu(self, op, reg_a, reg_b):
        """Perform ALU operations."""
        do = self.ALU_table.get(op, None)

        if do is None:
            raise Exception("Unsupported ALU operation")

        do(reg_a, reg_b)

    def load(self, program):
        """Load a program into memory."""

        self.create_opcode_table()
        self.create_ALU_table()

        address = 0

        for instruction in program:
            self.RAM[address] = instruction
            address += 1

    def step(self):
        """Run a single program step"""
        # Read byte at PC
        self.MAR = self.PC
        self.ram_read()
        self.IR = self.MDR

        # Read byte at PC+1
        self.MAR = (self.MAR + 1) & 255
        self.ram_read()
        self.opA = self.MDR

        # Read byte at PC+2
        self.MAR = (self.MAR + 1) & 255
        self.ram_read()
        self.opB = self.MDR

        # Set flag to see if the PC was set by an opcode
        self.PC_SET = False

        # Run opcode
        op = self.opcode_table.get(self.IR, None)
        if op is None:
            raise Exception(f'Undefined opcode {"0x{:02x}".format(self.IR)}.')
        op()

        # NOTE: The number of bytes an instruction uses can be determined from the
        # two high bits (bits 6-7) of the instruction opcode.
        if not self.PC_SET:
            high6 = (self.IR & 2 ** 6) >> 6
            high7 = (self.IR & 2 ** 7) >> 7

            if high6:
                self.PC = (self.PC + 2) & 255
            if high7:
                self.PC = (self.PC + 3) & 255


    def run(self):
        """Run the CPU."""
        #print("Running program...")

        while not self.HALT:
            self.step()
            #print("PC:", self.PC)


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

