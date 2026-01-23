
import requests
import json
import os

def check_models():
    try:
        response = requests.get("https://openrouter.ai/api/v1/models")
        response.raise_for_status()
        data = response.json()
        
        print("Searching for Qwen VL models...")
        found = False
        for model in data["data"]:
            name = model["name"].lower()
            mid = model["id"].lower()
            if "qwen" in name and "vl" in name:
                print(f"ID: {model['id']}")
                print(f"Name: {model['name']}")
                print(f"Pricing: {model.get('pricing')}")
                print("-" * 20)
                found = True
        
        if not found:
            print("No models found matching 'qwen' and 'vl'")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_models()
