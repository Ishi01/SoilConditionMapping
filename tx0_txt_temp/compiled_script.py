import tx0_to_txt_offset
import txt_temp
import Newtem

if __name__ == "__main__":

    #Note that these HAVE to be run in this order or things will break, since they depend on each other
    #run tx0_to_txt_offset
    #tx0_to_txt_offset.main()
    #run Newtem
    Newtem.main()
    #run txt_temp
    txt_temp.main()

    print(f"all files run successfully!")
    