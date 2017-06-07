'''
Created on 17 mag 2017

@author: Geko
'''


# # Create the kernel and learn AIML files
# kernel = aiml.Kernel()
# kernel.learn("std-startup.xml")
# kernel.respond("load aiml b")
# 
# # Press CTRL-C to break this loop
# while True:
#     print(kernel.respond(input("> ")))
    
def initializeBot():
    import aiml
    kernel = aiml.Kernel()
    kernel.learn("std-startup.xml")
    kernel.respond("load aiml b")
    return kernel