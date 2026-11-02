# Tag_FW_Chroma - AI Assistant Reference Guide

> **Last Updated**: 2025-11-13
> **Purpose**: Comprehensive reference for AI assistants working with Chroma tag firmware

## Table of Contents
- [Project Overview](#project-overview)
- [Hardware Architecture](#hardware-architecture)
- [Directory Structure](#directory-structure)
- [Build System](#build-system)
- [Key Concepts](#key-concepts)
- [Important Files](#important-files)
- [Development Workflow](#development-workflow)
- [Board Configurations](#board-configurations)
- [Protocol Implementation](#protocol-implementation)
- [Known Issues & Gotchas](#known-issues--gotchas)

---

## Project Overview

**Tag_FW_Chroma** is firmware for Display Data "Chroma" series electronic shelf labels (ESL), allowing them to be repurposed for the OpenEPaperLink project.

### Supported Tags

| Tag Model | Screen Size | SN Format | Build Target | Description |
|-----------|-------------|-----------|--------------|-------------|
| **Chroma29** | 2.9" | JA0xxxxxxxB<br>JC0xxxxxxxB | `chroma29` | B/W or B/W/R display |
| **Chroma29** (8151) | 2.9" | JA1xxxxxxxC | `chroma29_8151` | Variant with different screen controller |
| **Chroma42** | 4.2" | JC0xxxxxxxB | `chroma42` | B/W or B/W/R display |
| **Chroma42** (8176) | 4.2" | JH1xxxxxxxB | `chroma42_8176` | Variant with different screen controller |
| **Chroma74** (Yellow) | 7.4" | JM1xxxxxxxB | `chroma74y` | B/W/Y display |
| **Chroma74** (Red) | 7.4" | JL1xxxxxxxB | `chroma74r` | B/W/R display |

### Key Features
- **CPU**: 8051-based microcontroller (CC111x family)
- **Radio**: Integrated 2.4GHz or Sub-GHz transceiver
- **Display**: E-paper (1bpp or 2bpp)
- **Battery**: CR2450 or similar (months to years runtime)
- **Protocol**: OpenEPaperLink compatible

---

## Hardware Architecture

### Chroma Tag Block Diagram

```
┌─────────────────────────────────────────────┐
│  CC111x SoC (System-on-Chip)                │
│  ┌──────────────┐  ┌────────────────────┐   │
│  │  8051 CPU    │  │  RF Transceiver    │───┼─→ Antenna
│  │  32 KB Flash │  │  2.4GHz / Sub-GHz  │   │
│  │  2 KB RAM    │  └────────────────────┘   │
│  └──────────────┘                            │
│         │                                    │
│    ┌────┴─────┬────────┬────────┬───────┐   │
│    │          │        │        │       │   │
│    ▼          ▼        ▼        ▼       ▼   │
│  GPIO      UART     SPI      ADC     Timer  │
└────┼──────────┼────────┼────────┼───────────┘
     │          │        │        │
     ▼          ▼        ▼        ▼
  [Buttons]  [EEPROM]  [EPD]  [Battery]
                        (E-Paper
                         Display)
```

### Memory Layout

**Flash (32KB)**:
```
0x0000 - 0x7FFF: Code (32KB)
  - Bootloader (optional)
  - Main firmware
  - Font data
  - LUT tables
```

**RAM (2KB)**:
```
0x0000 - 0x00FF: Special Function Registers (SFRs)
0xF000 - 0xFDA2: XRAM (3.5KB usable for variables)
```

**EEPROM (External, varies)**:
```
- Stored images
- Configuration
- Association data
```

---

## Directory Structure

```
Tag_FW_Chroma/
├── Chroma_Tag_FW/                  # Main firmware directory
│   ├── OEPL/                       # OpenEPaperLink-specific code
│   │   ├── Makefile                # Build configuration
│   │   ├── main.c                  # Main loop, tag logic
│   │   ├── powermgt.c/h            # Power management, sleep
│   │   ├── syncedproto.c/h         # Protocol implementation
│   │   ├── userinterface.c/h       # Button handling, NFC
│   │   ├── barcode.c               # Barcode generation
│   │   └── ...
│   │
│   ├── common/                     # Shared code across all tags
│   │   ├── settings.h              # FW version, build settings
│   │   ├── eeprom.c/h              # EEPROM driver
│   │   ├── drawing.c/h             # Drawing primitives
│   │   ├── comms.c/h               # Radio communication
│   │   ├── proto.h                 # Original Dmitry protocol
│   │   └── screen.c                # Screen driver (default)
│   │
│   ├── board/                      # Board-specific configurations
│   │   ├── boardChroma.c           # Common Chroma board code
│   │   ├── boardCommon.h           # Board interface
│   │   ├── chroma29/               # 2.9" specific
│   │   │   ├── board.h             # Pin definitions, LUTs
│   │   │   ├── make.mk             # Build settings
│   │   │   └── screen_8151.c       # Alt screen driver
│   │   ├── chroma42/               # 4.2" specific
│   │   │   └── ...
│   │   └── chroma74/               # 7.4" specific
│   │       └── ...
│   │
│   ├── soc/                        # SoC-specific code
│   │   └── cc111x/                 # CC111x family
│   │       ├── make.mk             # SoC build settings
│   │       ├── radio.c/h           # Radio driver
│   │       ├── adc.c/h             # ADC (battery voltage)
│   │       ├── timer.c/h           # Timers
│   │       ├── sleep.c/h           # Sleep modes
│   │       ├── wdt.c/h             # Watchdog
│   │       └── u1shared.c          # UART driver
│   │
│   ├── cpu/                        # CPU-specific code
│   │   └── 8051/                   # 8051 architecture
│   │       ├── make.mk             # Compiler flags
│   │       ├── asmUtil.c           # Assembly helpers
│   │       └── peep.def            # SDCC peephole optimizer
│   │
│   ├── make/                       # Build system
│   │   ├── common.mk               # Common Makefile rules
│   │   └── rules.mk                # Build rules
│   │
│   ├── builds/                     # Build output (generated)
│   │   ├── chroma29/
│   │   │   └── main.bin            # Binary output
│   │   └── ...
│   │
│   └── add_ota_hdr/                # OTA header tool
│       └── add_ota_hdr.py          # Adds header for OTA updates
│
├── shared/                         # Git submodule (Shared_OEPL_Definitions)
│   └── oepl-proto.h                # Protocol definitions
│
├── sdcc/                           # SDCC build scripts
│   ├── build_sdcc.sh               # Build SDCC from source
│   └── setup_sdcc.sh               # Setup SDCC environment
│
├── build_all.sh                    # Build all tag variants (NEW!)
└── README.md                       # User documentation
```

---

## Build System

### Make-Based Build

The build system uses GNU Make with multiple levels of configuration:

```
OEPL/Makefile
    ↓ includes
make/common.mk (sets up paths, includes board/soc/cpu)
    ↓ includes
board/chroma29/make.mk (board-specific settings)
    ↓ includes
soc/cc111x/make.mk (SoC-specific settings)
    ↓ includes
cpu/8051/make.mk (CPU-specific settings)
    ↓ includes
make/rules.mk (actual build rules)
```

### Build Variables

**Key variables** in `OEPL/Makefile`:

```makefile
BUILD ?= chroma74r                 # Default build target
BOARD = chroma74                   # Board (derived from BUILD)
SOC = cc111x                       # SoC (set by board)
CPU = 8051                         # CPU (set by SoC)
FLAGS += -DBUILD=$(BUILD)          # Pass BUILD to compiler
FLAGS += -DHW_VARIANT=1            # Hardware variant flag
SCREEN_SRC = screen.c              # Screen driver source
```

**Build resolution**:
```
BUILD=chroma29 → BOARD=chroma29, SCREEN_SRC=screen.c
BUILD=chroma29_8151 → BOARD=chroma29, SCREEN_SRC=screen_8151.c, FLAGS+=-DHW_VARIANT=1
BUILD=chroma42_8176 → BOARD=chroma42, SCREEN_SRC=screen_8176.c, FLAGS+=-DHW_VARIANT=1
```

### Compiler: SDCC 4.2.0

**Critical**: SDCC version **MUST** be 4.2.0. Other versions produce broken code.

**Compiler flags** (`cpu/8051/make.mk`):
```makefile
FLAGS += -mmcs51               # Target: MCS-51 (8051)
FLAGS += --std-c2x             # C23 standard
FLAGS += --opt-code-size       # Optimize for size
FLAGS += --peep-file peep.def  # Peephole optimizer
FLAGS += --fomit-frame-pointer # Save stack space
FLAGS += --model-medium        # Medium memory model
FLAGS += --xram-loc 0xf000     # XRAM location
FLAGS += --xram-size 0xda2     # XRAM size (3.5KB)
FLAGS += --code-size 0x8000    # Flash size (32KB)
```

### Build Targets

**Manual build** (single variant):
```bash
cd Chroma_Tag_FW/OEPL
make BUILD=chroma29         # Build
make clean BUILD=chroma29   # Clean
```

**Automated build** (all variants):
```bash
./build_all.sh              # Build all 6 variants
./build_all.sh --clean      # Clean all
./build_all.sh --help       # Show help
```

**Output**:
```
Chroma_Tag_FW/builds/chroma29/
├── main.ihx              # Intel HEX format
├── main.bin              # Raw binary (flash this!)
├── main.map              # Memory map
└── *.rel                 # Relocatable objects
```

---

## Key Concepts

### 1. Tag Lifecycle

```
[Power On / Boot]
       ↓
[Init Hardware]
       ↓
[Associated?] ─No→ [Scan for AP] ─→ [Send Assoc Request]
       ↓                                     ↓
      Yes                             [Receive Assoc Info]
       ↓                                     ↓
[Wake from Sleep] ←───────────────────────────┘
       ↓
[Send Checkin]
       ↓
[Receive Data Avail]
       ↓
[Data pending?] ─No→ [Sleep for nextCheckIn seconds]
       ↓                            ↓
      Yes                           └─→ [Wakeup timer] ─→ [Wake from Sleep]
       ↓
[Request Data Chunks]
       ↓
[Receive & Store in EEPROM]
       ↓
[Verify MD5]
       ↓
[Update Display]
       ↓
[Sleep for nextCheckIn seconds]
```

### 2. Sleep & Power Management

Tags spend >99.9% of time asleep to conserve battery.

**Sleep modes** (`powermgt.c`):
```c
doSleep(uint32_t milliseconds)
```

**Wake sources**:
- Timer (scheduled checkin)
- Button press
- NFC field detection

**Power-saving algorithm**:
- Tracks communication success rate
- Adjusts sleep interval based on AP reliability
- Falls back to longer intervals if AP unreachable

**Sleep value from AP** (`main.c:183-190`):
```c
if (nextCheckInFromAP) {
    // Value is in SECONDS (0-65535)
    doSleep(nextCheckInFromAP * 1000UL);
}
```

### 3. E-Paper Display

**Display Types**:
- **1bpp**: Black/White only (1 bit per pixel)
- **2bpp**: Black/White/Red or Black/White/Yellow (2 bits per pixel)

**Refresh Process**:
1. Clear display (optional)
2. Write pixel data to display buffer
3. Apply waveform (LUT - Look-Up Table)
4. Wait for refresh complete (~2-15 seconds)

**LUT (Look-Up Table)**:
- Controls voltage timing for e-paper refresh
- Different LUTs for different temperatures, colors
- Defined in `board/<variant>/board.h`

### 4. EEPROM Storage

External EEPROM stores:
- Images (compressed or raw)
- Configuration
- Association data
- Fonts (optional)

**Access** (`eeprom.c`):
```c
eeWriteBlock(uint16_t addr, uint8_t *data, uint16_t len);
eeReadBlock(uint16_t addr, uint8_t *data, uint16_t len);
```

### 5. Protocol Flow

**Association**:
```
Tag: [Broadcast] ASSOC_REQ (TagInfo)
AP:  [Unicast]   ASSOC_RESP (AssocInfo)
```

**Checkin**:
```
Tag: [Unicast] CHECKIN (CheckinInfo: battery, temp, RSSI)
AP:  [Unicast] CHECKOUT (PendingInfo: nextCheckIn, update available?)
```

**Data Transfer**:
```
Tag: [Unicast] CHUNK_REQ (offset, length)
AP:  [Unicast] CHUNK_RESP (data chunk)
... repeat until complete
Tag: [Unicast] XFER_COMPLETE
```

---

## Important Files

### `OEPL/main.c`

**Purpose**: Main tag logic loop

**Key Functions**:

**`main()`** - Tag main loop:
```c
void main() {
    initHardware();

    while(1) {
        if (gTagAssociated) {
            tagAssociated();  // Normal operation
        } else {
            TagChanSearch();  // Scan for AP
        }
    }
}
```

**`tagAssociated()`** - When tag is associated with AP (lines 115-195):
```c
void tagAssociated() {
    // Wake up
    initAfterWake();

    // Send checkin, get response
    struct AvailDataInfo *avail = getAvailDataInfo();

    if (avail == NULL) {
        nextCheckInFromAP = 0;  // No response, use algorithm
    } else {
        nextCheckInFromAP = avail->nextCheckIn;  // AP says sleep this long (SECONDS)

        if (avail->dataType != DATATYPE_NOUPDATE) {
            processAvailDataInfo(avail);  // Download & display update
        }
    }

    // Sleep
    if (nextCheckInFromAP) {
        doSleep(nextCheckInFromAP * 1000UL);  // Sleep for AP-specified time
    } else {
        doSleep(getNextSleep() * 1000UL);     // Use power-saving algorithm
    }
}
```

**Key point** (line 185): Sleep value is in **seconds**:
```c
doSleep(nextCheckInFromAP * 1000UL);  // seconds → milliseconds
```

### `OEPL/powermgt.c`

**Purpose**: Power management and sleep

**Key Functions**:

**`doSleep(uint32_t ms)`** - Enter sleep mode
```c
void doSleep(uint32_t t) {
    sleepForMsec(t);  // Configure timer, enter PM2 (deep sleep)
}
```

**`getNextSleep()`** - Power-saving algorithm (lines 111-120):
```c
uint16_t getNextSleep() {
    // Average recent checkin attempt counts
    uint16_t avg = averageAttempts();

    // More attempts = worse connection = longer sleep
    return avg;  // Returns seconds
}
```

**Constants**:
```c
#define INTERVAL_BASE 40                  // Base interval: 40s
#define INTERVAL_AT_MAX_ATTEMPTS 1200     // Max interval: 20 minutes
#define POWER_SAVING_SMOOTHING 5          // Smooth over 5 samples
```

### `OEPL/syncedproto.c`

**Purpose**: Protocol implementation (association, data transfer)

**Key Functions**:

**`getAvailDataInfo()`** - Send checkin, get response:
```c
struct AvailDataInfo* getAvailDataInfo() {
    // Build checkin packet
    struct CheckinInfo checkin;
    checkin.state.batteryMv = gBattV;
    checkin.temperature = gTemperature + CHECKIN_TEMP_OFFSET;

    // Send via radio
    txPkt(&checkin, sizeof(checkin));

    // Wait for response
    struct AvailDataInfo *avail = rxPkt();

    return avail;  // NULL if timeout
}
```

**`processAvailDataInfo()`** - Download and process update (lines 350+):
```c
bool processAvailDataInfo(struct AvailDataInfo *avail) {
    // Determine data type
    if (avail->dataType == DATATYPE_IMG_RAW_1BPP) {
        // Download image chunks
        downloadData(avail->dataVer, avail->dataSize);

        // Verify MD5
        if (!verifyMD5(avail->dataVer)) return false;

        // Display image
        drawImageFromEeprom(imgSlot);

        return true;
    }
    // ... other data types
}
```

### `OEPL/userinterface.c`

**Purpose**: Button handling, NFC detection

**Key Functions**:

**`detectButtonPress()`** - Check if button pressed:
```c
bool detectButtonPress() {
    // Read GPIO
    if (BUTTON_PRESSED) {
        WaitMs(50);  // Debounce
        if (BUTTON_PRESSED) return true;
    }
    return false;
}
```

**`checkNFC()`** - Detect NFC field:
```c
bool checkNFC() {
    // Detect RF field from NFC reader
    // (implementation varies by board)
}
```

### `common/drawing.c`

**Purpose**: Drawing primitives (lines, rectangles, text)

**Key Functions**:
```c
void drawPixel(int16_t x, int16_t y, uint8_t color);
void drawLine(int16_t x0, int16_t y0, int16_t x1, int16_t y1, uint8_t color);
void drawRect(int16_t x, int16_t y, int16_t w, int16_t h, uint8_t color);
void drawText(int16_t x, int16_t y, const char *text, const Font *font, uint8_t color);
```

### `common/eeprom.c`

**Purpose**: External EEPROM driver (I2C)

**Key Functions**:
```c
void eeWriteBlock(uint16_t addr, uint8_t *data, uint16_t len);
void eeReadBlock(uint16_t addr, uint8_t *data, uint16_t len);
void eeErase(uint16_t addr, uint16_t len);
```

### `board/<variant>/board.h`

**Purpose**: Board-specific pin definitions, LUTs

**Example** (`board/chroma29/board.h`):
```c
// Pin definitions
#define EPD_BUSY   P0_0
#define EPD_RESET  P0_1
#define EPD_CS     P0_2
#define EPD_DC     P0_3

// Display resolution
#define SCREEN_WIDTH  296
#define SCREEN_HEIGHT 128

// LUT (waveform)
#define EPD_LUT_DEFAULT  lut_bw_default
extern const uint8_t lut_bw_default[];

// Hardware variant
#ifdef HW_VARIANT
  #define SCREEN_CONTROLLER_8151
#else
  #define SCREEN_CONTROLLER_DEFAULT
#endif
```

### `board/<variant>/screen.c`

**Purpose**: E-paper display driver

**Key Functions**:
```c
void screenInit();
void screenClear();
void screenRefresh();
void screenPowerOff();
void screenDrawPixel(uint16_t x, uint16_t y, uint8_t color);
```

**Driver variants**:
- `screen.c`: Default screen controller
- `screen_8151.c`: Chroma29 variant (8151 controller)
- `screen_8176.c`: Chroma42 variant (8176 controller)

### `shared/oepl-proto.h`

**Purpose**: Shared protocol definitions (Git submodule)

**Key Structures** (see Shared_OEPL_Definitions CLAUDE.md for details):
```c
struct AvailDataInfo {
    uint8_t checksum;
    uint64_t dataVer;
    uint32_t dataSize;
    uint8_t dataType;
    uint8_t dataTypeArgument;
    uint16_t nextCheckIn;  // SECONDS (0-65535)
} __packed;
```

---

## Development Workflow

### 1. Setup Build Environment

**Install SDCC 4.2.0**:

**macOS** (via Homebrew):
```bash
brew install sdcc
sdcc -v  # Verify version 4.2.0
```

**Linux** (build from source):
```bash
cd sdcc
./build_sdcc.sh
source setup_sdcc.sh
```

**Verify**:
```bash
sdcc -v
# Output: SDCC : mcs51 4.2.0 #13081
```

### 2. Clone Repository

```bash
git clone https://github.com/mLupine/Tag_FW_Chroma.git
cd Tag_FW_Chroma
git submodule update --init --recursive  # Fetch shared/ submodule
```

### 3. Build Firmware

**Build all variants** (recommended):
```bash
./build_all.sh
```

**Build single variant**:
```bash
cd Chroma_Tag_FW/OEPL
make BUILD=chroma29
```

**Output**:
```
Chroma_Tag_FW/builds/chroma29/main.bin  ← Flash this file!
```

### 4. Flash Tag

**Hardware needed**:
- CC Debugger (or compatible JTAG adapter)
- Pogo pin adapter or soldered connections

**Connections**:
```
CC Debugger → Tag
    GND    → GND
    3.3V   → VCC
    DC     → Debug Clock
    DD     → Debug Data
    RST    → Reset (optional)
```

**Flash command**:
```bash
# Using cc-tool
cc-tool -e -w Chroma_Tag_FW/builds/chroma29/main.bin -v

# Using CCLoader
python CCLoader.py -e -w main.bin
```

### 5. Debugging

**Serial output** (if enabled):
```c
printf("Debug: Battery %d mV\n", batteryMv);
```

**No UART on production tags** - use LED blinks or NFC for debugging:
```c
// Blink LED pattern for debugging
blinkPattern(0b10101010);
```

**Memory map** (check `main.map`):
```
Code size:    25634 bytes
XRAM usage:   2145 bytes
Stack usage:  estimated 200 bytes
```

### 6. Testing

**Test checklist**:
- [ ] Tag boots, sends association request
- [ ] Tag associates with AP
- [ ] Tag receives data, updates display
- [ ] Tag sleeps for correct duration
- [ ] Battery voltage reported correctly
- [ ] Button press detected
- [ ] NFC works (if applicable)

---

## Board Configurations

### Chroma 29 (2.9")

**Serial Numbers**:
- `JA0xxxxxxxB`: Default variant (`BUILD=chroma29`)
- `JA1xxxxxxxC`: 8151 controller variant (`BUILD=chroma29_8151`)

**Screen**: 296x128, B/W or B/W/R

**Build**:
```bash
make BUILD=chroma29        # Default
make BUILD=chroma29_8151   # 8151 variant
```

**Key Files**:
- `board/chroma29/board.h`
- `board/chroma29/screen.c` (default)
- `board/chroma29/screen_8151.c` (variant)

### Chroma 42 (4.2")

**Serial Numbers**:
- `JC0xxxxxxxB`: Default variant (`BUILD=chroma42`)
- `JH1xxxxxxxB`: 8176 controller variant (`BUILD=chroma42_8176`)

**Screen**: 400x300, B/W or B/W/R

**Build**:
```bash
make BUILD=chroma42        # Default
make BUILD=chroma42_8176   # 8176 variant
```

### Chroma 74 (7.4")

**Serial Numbers**:
- `JM1xxxxxxxB`: Yellow variant (`BUILD=chroma74y`)
- `JL1xxxxxxxB`: Red variant (`BUILD=chroma74r`)

**Screen**: 640x384, B/W/Y or B/W/R

**Build**:
```bash
make BUILD=chroma74y   # Yellow
make BUILD=chroma74r   # Red
```

**Differences**:
- LUT tables (yellow vs red)
- Compilation flag: `-DBWY` (yellow) or `-DBWR` (red)

---

## Protocol Implementation

### Association

**Tag sends** (`PKT_ASSOC_REQ`):
```c
struct TagInfo {
    uint8_t protoVer;           // PROTO_VER_CURRENT
    struct TagState state;      // swVer, hwType, batteryMv
    uint16_t screenPixWidth;    // e.g., 296
    uint16_t screenPixHeight;   // e.g., 128
    uint16_t screenMmWidth;     // Physical width in mm
    uint16_t screenMmHeight;    // Physical height in mm
    uint16_t compressionsSupported;  // Compression types
    uint16_t maxWaitMsec;       // How long to wait for packets
    uint8_t screenType;         // TagScreenEink_BWR_2bpp, etc.
};
```

**AP responds** (`PKT_ASSOC_RESP`):
```c
struct AssocInfo {
    uint32_t checkinDelay;             // Base sleep duration (ms)
    uint32_t retryDelay;               // Retry delay on partial xfer
    uint16_t failedCheckinsTillBlank;  // Blank screen after N failures
    uint16_t failedCheckinsTillDissoc; // Dissociate after N failures
    uint32_t newKey[4];                // Encryption key (if used)
};
```

### Checkin

**Tag sends** (`PKT_CHECKIN`):
```c
struct CheckinInfo {
    struct TagState state;      // swVer, hwType, batteryMv
    uint8_t lastPacketLQI;      // Link quality indicator
    int8_t lastPacketRSSI;      // Signal strength
    uint8_t temperature;        // Temp in °C + offset
};
```

**AP responds** (`PKT_CHECKOUT`):
```c
struct PendingInfo {
    uint64_t imgUpdateVer;      // Image MD5 (if update available)
    uint32_t imgUpdateSize;     // Image size in bytes
    uint64_t osUpdateVer;       // Firmware MD5 (if update available)
    uint32_t osUpdateSize;      // Firmware size in bytes
    uint32_t nextCheckinDelay;  // Sleep duration (milliseconds)
    // NOTE: In OEPL protocol, this is sent as AvailDataInfo with
    //       nextCheckIn field in SECONDS, not PendingInfo
};
```

### Data Transfer

**Tag requests chunk** (`PKT_CHUNK_REQ`):
```c
struct ChunkReqInfo {
    uint64_t versionRequested;  // MD5 of data
    uint32_t offset;            // Byte offset
    uint8_t len;                // Chunk length (max ~80 bytes)
    uint8_t osUpdatePlz : 1;    // Is this firmware (1) or image (0)?
};
```

**AP sends chunk** (`PKT_CHUNK_RESP`):
```c
struct ChunkInfo {
    uint32_t offset;            // Byte offset
    uint8_t osUpdatePlz : 1;    // Firmware or image
    uint8_t data[];             // Actual data (variable length)
};
```

---

## Known Issues & Gotchas

### 1. SDCC Version Critical

❌ **SDCC 4.3.0, 4.4.0 produce broken code**
- Code compiles but doesn't run correctly
- Tags may crash, hang, or behave erratically

✅ **Use SDCC 4.2.0 exactly**
```bash
sdcc -v
# MUST show: SDCC : mcs51 4.2.0 #13081
```

### 2. Memory Constraints

❌ **Exceeding 32KB flash or 3.5KB RAM causes linker errors**

✅ **Monitor memory usage in `main.map`**:
```
Code:  25634 / 32768 bytes (78%)  ← OK
XRAM:   2145 /  3490 bytes (61%)  ← OK
```

**Tips to reduce size**:
- Remove unused fonts
- Disable debug printf
- Optimize LUT tables
- Use --opt-code-size

### 3. Sleep Time Units

❌ **Old code used minutes, new code uses seconds**

✅ **Always seconds** (`main.c:185`):
```c
doSleep(nextCheckInFromAP * 1000UL);  // seconds → ms
```

**Max sleep**: 65535 seconds = 18.2 hours

### 4. Build Target Confusion

❌ **Wrong build target for tag variant**
- `BUILD=chroma29` won't work on `JA1xxxxxxxC` tags

✅ **Check serial number, use correct build**:
```
JA0xxxxxxxB → chroma29
JA1xxxxxxxC → chroma29_8151
JC0xxxxxxxB → chroma29 (29) or chroma42 (42)
JH1xxxxxxxB → chroma42_8176
```

### 5. Flashing Failures

❌ **CC Debugger connection issues**

✅ **Checklist**:
- Green LED on CC Debugger?
- Connections secure (GND, VCC, DC, DD)?
- Tag powered (3.3V)?
- Correct command:
  ```bash
  cc-tool -e -w main.bin -v
  ```

### 6. Display Not Updating

❌ **Common causes**:
- Wrong LUT for temperature
- Incorrect screen driver variant
- EEPROM corruption

✅ **Debug steps**:
1. Verify build target matches tag
2. Check battery voltage (>2.4V)
3. Manually trigger refresh via button
4. Re-flash firmware

### 7. Git Submodule Missing

❌ **Build fails with "oepl-proto.h not found"**

✅ **Initialize submodules**:
```bash
git submodule update --init --recursive
```

### 8. Association Failure

❌ **Tag won't associate with AP**

✅ **Check**:
- AP is on same channel (default: 15)
- Tag is within range
- AP firmware is compatible
- Tag firmware version matches AP expectations

### 9. Power Consumption High

❌ **Battery drains quickly**

✅ **Possible causes**:
- Sleep not working (check `doSleep()`)
- Display not powering off (`screenPowerOff()`)
- Radio staying on
- Too-frequent checkins (reduce `nextCheckIn`)

### 10. Makefile Build Errors

❌ **"No rule to make target..."**

✅ **Common fixes**:
```bash
make clean BUILD=chroma29     # Clean first
make BUILD=chroma29           # Then build

# Or use automated script
./build_all.sh --clean
./build_all.sh
```

---

## Additional Resources

- **Main Repo**: https://github.com/mLupine/Tag_FW_Chroma
- **Shared Definitions**: https://github.com/mLupine/Shared_OEPL_Definitions
- **OpenEPaperLink Wiki**: https://github.com/OpenEPaperLink/OpenEPaperLink/wiki/Chroma-Series-SubGhz-Tags
- **SDCC Manual**: http://sdcc.sourceforge.net/doc/sdccman.pdf
- **8051 Reference**: Various online resources for 8051 architecture

---

## Build Script Reference

### `build_all.sh` (New!)

Automated build script for all Chroma variants.

**Usage**:
```bash
./build_all.sh              # Build all variants
./build_all.sh --clean      # Clean build directories
./build_all.sh --help       # Show help
```

**Features**:
- ✅ Checks for SDCC 4.2.0
- ✅ Offers to install SDCC on macOS (Homebrew)
- ✅ Can build SDCC locally on Linux
- ✅ Builds all 6 variants automatically
- ✅ Displays colored build summary
- ✅ Shows binary sizes

**Output**:
```
═══════════════════════════════════════════════
  OpenEPaperLink Chroma Tag Firmware Builder
  Platform: macOS
═══════════════════════════════════════════════

✓ Found SDCC 4.2.0
Building chroma29...
✓ chroma29 built successfully
...
═══════════════════════════════════════════════
Build Summary
═══════════════════════════════════════════════
✓ chroma29: 25634 bytes
✓ chroma29_8151: 26012 bytes
✓ chroma42: 27103 bytes
✓ chroma42_8176: 27854 bytes
✓ chroma74y: 32741 bytes
✓ chroma74r: 32683 bytes

Total: 6 | Success: 6 | Failed: 0
```

---

**End of Tag_FW_Chroma AI Reference**
