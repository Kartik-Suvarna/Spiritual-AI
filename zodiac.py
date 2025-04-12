import requests

baseUrl = "http://sandipbgt.com/theastrologer/api"

def getSigns():
  return requests.get(f"{baseUrl}/sunsigns").json()

def getHoroscope(sign, timeframe):
  return requests.get(f"{baseUrl}/horoscope/{sign}/{timeframe}").json()


signs = getSigns()


print("")
print("Here is a list of all the signs you can choose from:")

for sign in signs:
    print(f" - {sign}")

signToFetch = input("\nPlease type a sign to receive your horoscope for today:\n")
print(signToFetch)
horoscope = getHoroscope(signToFetch, "today")

print(horoscope['horoscope'])