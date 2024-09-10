import txt_temp
import Newtem

if __name__ == "__main__":

    #Note that these HAVE to be run in this order or things will break, since they depend on each other
    #run Newtem, which does temperature processing
    Newtem.main()
    #run txt_temp
    txt_temp.main()

    print(f"all files run successfully!")
    