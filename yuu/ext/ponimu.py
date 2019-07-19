# Will be added depending on the situation
# Still need to figure out some encryption in the Authorization Header

# Authorization Header are different while parsing the web and fetching key + m3u8 + video.

# Authorization header used while fetching key and m3u8 are encrypted with AES-CTR-128
# They add a current time in milisecond to the original Authorization and encrypt it with them
# Example: eyRasdiuahsidhqwe|1563504400803
# Then they'll encrypt that
# After that, the encrypted are decoded as Hex and appended `1563504400803` time again
# Example: rrqiweuosjaod|1563504400803
# That will be used as the new Authorization.
# They use a counter that I still need to understand because the javascript are obfuscated

# Need help to deobfuscate the javascript that used to encrypt the Header
# If anyone interested at helping me, contact me at Discord: N4O#8868
# Or email me at: noaione0809@gmail.com