from retriever import get_disease_information


prediction = {
    "crop": "ragi",
    "disease": "ragi_seedling",
    "confidence": 0.8045
}


disease_key = prediction["disease"]

information = get_disease_information(disease_key)


print("\nDetected disease:")
print(information["name"])

print("\nDescription:")
print(information["description"])

print("\nCauses:")
for cause in information["causes"]:
    print("-", cause)

print("\nManagement:")
for item in information["management"]:
    print("-", item)