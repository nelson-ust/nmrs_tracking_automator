
import subprocess

users_response =int(input("What form do you want to work with? 1-Pharmacy Form, 2 - Lab, 3 - Client Tracking..."))

 # Switch statement in python
match users_response:
    case 1:
        subprocess.run(['python', '/services/tracking.py'])
        print("Tracking Entries is completed")
    case  2:
        pass
    case 3:
        pass
    case 3:
        pass
