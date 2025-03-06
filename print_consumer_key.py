import ovh

def main():
    client = ovh.Client()

    ck = client.new_consumer_key_request()
    ck.add_recursive_rules(ovh.API_READ_WRITE, "/domain/zone")

    # Request token
    validation = ck.request()

    print("Please visit %s to authenticate" % validation['validationUrl'])
    input("and press Enter to continue...")

    # Print nice welcome message
    print("Your 'consumerKey' is '%s'" % validation['consumerKey'])

if __name__ == "__main__":
    main()