
def main(): 

    from argparse import ArgumentParser

    parser = ArgumentParser(description='Remove Headers, Footers, and Forward page from a'
                             'تخليص الإبريز في تلخيص باريز ')
    
    parser.add_argument('infile', help="Input text file")
    args = parser.parse_args()

    with open (args.infile, "r", encoding='utf-8') as infile: 
            text = infile.read()
            print(f"Word count: {len(text.split()):,}")

if __name__ == "__main__":
    main()