#ifndef CHIP8_H
#define CHIP8_H

#include <cstdint>
#include <array>

class Chip8 {
public:
    Chip8();  // Constructor

    void LoadProgram(const char* filename);  // Load CHIP-8 program into memory
    void EmulateCycle();  // Fetch, decode, execute

private:
    // Memory and registers
    std::array<uint8_t, 4096> memory{};  // 4KB RAM
    std::array<uint8_t, 16> V{};  // 16 general-purpose registers
    uint16_t I = 0;  // Index register
    uint16_t PC = 0x200;  // Program counter (starts at 0x200)

    // Stack and stack pointer
    std::array<uint16_t, 16> stack{};
    uint8_t SP = 0;

    // Timers
    uint8_t delay_timer = 0;
    uint8_t sound_timer = 0;
    uint16_t opcode; //current instruction
};

#endif

