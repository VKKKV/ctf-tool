# from hard.hard2 import main

def main():
    chosen = int(input('Write a Level (1-B): '), 16)
    app: function = lambda: 1

    match chosen:
        case 0x1: # Hard
            from hard1 import app
        case 0x2:
            from hard2 import app
        case 0x3:
            from hard3 import app
        case 0x4:
            from hard4 import app
        case 0x5:
            pass
        case 0x6:
            pass
        case 0x7: # Too Much!
            from too_much1 import app
        case 0x8:
            pass
        case 0x9:
            pass
        case 0xA:
            pass
        case 0xB:
            pass
        case _:
            return
    app()


if __name__ == '__main__':
    main()
