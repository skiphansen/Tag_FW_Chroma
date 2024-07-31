import argparse

class SnException(Exception):
    pass

def patch_sn(file_path, sn):
    try:
        with open(file_path, "r+b") as file:
            #mac_bytes = bytearray.fromhex(mac.replace(':', ''))
            #while len(mac_bytes) < 8:
            #    mac_bytes[:0] = bytearray(b'\x00')
            #mac_bytes.reverse()  # Reverse the byte order

            file.seek(0x7ffe)
            offset = file.read(2)
            SnOffset = (offset[1] << 8) + offset[0]
            file.seek(SnOffset)
            bin = file.read(2)
            tag_type = bin.decode("utf-8")
            if sn[0:2] != tag_type[0:2]:
                print(f'Invalid SN, first two letters much be "{tag_type}" for this tag type')
                raise SnException()
            bin = file.read(4)
            new_sn = bytes.fromhex(sn[2:10])
            file.seek(SnOffset+2)
            file.write(new_sn)
            file.close()
            print(f'SN changed from {tag_type[0:2]}{bin.hex()} to {sn}')

    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    except SnException:
        pass

def sn_help():
    print('Invalid SN.')
    print('The SN must be 2 letters, 8 digits and one letter. For example "JM10339094B".')

def validate_arguments(args):
    result = False
    SN = args.SN.upper()
    sn_len = len(SN)
    if sn_len != 10 and sn_len != 11:
        pass
    elif not SN[0:2].isalpha() or not SN[2:10].isdigit():
        pass
    else:
        result = True

    if not result:
        sn_help()

    return result

def main():
    parser = argparse.ArgumentParser(description="Patch serial number in a binary firmware file for a Chroma tag")
    parser.add_argument("SN", help="New Serial Number")
    parser.add_argument("filename", help="Binary file to patch (.bin or .hex)")

    args = parser.parse_args()


    if not validate_arguments(args):
        return
    
    patch_sn(args.filename, args.SN.upper())

if __name__ == "__main__":
    main()
