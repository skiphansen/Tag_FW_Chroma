import argparse
import zlib

class SnException(Exception):
    pass

def patch_sn(file_path, sn):
    try:
        with open(file_path, "r+b") as file:
            #mac_bytes = bytearray.fromhex(mac.replace(':', ''))
            #while len(mac_bytes) < 8:
            #    mac_bytes[:0] = bytearray(b'\x00')
            #mac_bytes.reverse()  # Reverse the byte order

            ota_offset = 0
            #file.seek(9)
            bin = bytearray(file.read())
            if len(bin) == 32768:
                print("Patching full binary file")
                pass

            else:
                tag_type = bin[9:15].decode("utf-8")
                if tag_type == 'chroma':
                    # ota file
                    if bin[8] == 1:
                        print("Patching ota file")
                        ota_offset = 25
                    else:
                        print(f'Header version {bin[8]} is not supported')
                        raise SnException()
                else:
                    print(f'File not recognized as full binary or ota file')
                    raise SnException()

            SnOffset = (bin[32767 + ota_offset] << 8) + bin[32766 + ota_offset]
            SnOffset += ota_offset
            tag_type = bin[SnOffset:SnOffset+2].decode("utf-8")
            if sn[0:2] != tag_type:
                print(f'Invalid SN, first two letters much be "{tag_type}" for this tag type')
                raise SnException()
            new_sn = bytes.fromhex(sn[2:10])
            print(f'SN changed from {tag_type}{bin[SnOffset+2:SnOffset+6].hex()} to {sn}')
            file.seek(SnOffset+2)
            file.write(new_sn)
            if ota_offset != 0:
                bin[SnOffset+2:SnOffset+6] = new_sn
                crc = zlib.crc32(bin[ota_offset:])
                file.seek(0)
                file.write(crc.to_bytes(4,'little'))
            file.close()

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
