import json
import pandas as pd
from datetime import datetime
import re
import os  # To extract file names from paths

# Load the JSON file
with open('chat_data.json', 'r') as file:
    data = json.load(file)

# Function to extract content after the timestamp
def extract_content_after_timestamp(content, timestamp):
    try:
        # Match the timestamp in the content
        timestamp_pattern = re.escape(timestamp)
        split_content = re.split(timestamp_pattern, content, maxsplit=1)
        if len(split_content) > 1:
            return split_content[1].strip()  # Return content after the timestamp
        return content.strip()  # If no match, return the original content
    except Exception as e:
        return content.strip()  # Fallback in case of errors

# Function to clean up the extracted content
def clean_extracted_content(content, author, attachments, images):
    # Remove non-breaking spaces and extra newlines
    content = re.sub(r"Â|\s+", " ", content)
    # Remove the author's name if present in the content
    content = re.sub(rf"\b{re.escape(author)}\b", "", content, flags=re.IGNORECASE)
    # Remove file names (attachments and images) from the content
    for attachment in attachments:
        content = content.replace(attachment, "")
    for image in images:
        content = content.replace(image, "")
    # Remove extra spaces
    content = content.strip()
    return content

# Function to safely parse timestamps
def parse_timestamp(timestamp):
    try:
        return datetime.strptime(timestamp, "%m/%d %I:%M %p").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None  # Return None for invalid timestamps

# Process the JSON data
cleaned_data = []
for message in data:
    parsed_timestamp = parse_timestamp(message["timestamp"])  # Safely parse the timestamp
    attachments = [att["name"] for att in message.get("attachments", [])]
    images = [os.path.basename(img["local_path"]) for img in message.get("images", []) if img["download_status"] == "success"]  # Extract image file names
    raw_content = extract_content_after_timestamp(message["content"], message["timestamp"])
    cleaned_message = {
        "Chat Name": message["chat_name"],
        "Message ID": message["message_id"],
        "Author": message["author"],
        "Timestamp": parsed_timestamp,
        "Content": clean_extracted_content(raw_content, message["author"], attachments, images),  # Clean the extracted content
        "Attachments": ", ".join(attachments) if attachments else "",  # Convert list to string or empty string
        "Images": ", ".join(images) if images else ""  # Convert list to string or empty string
    }
    cleaned_data.append(cleaned_message)

# Convert to a DataFrame
df = pd.DataFrame(cleaned_data)

# Save to a CSV file
df.to_csv('cleaned_chat_data_with_content.csv', index=False)

print("JSON data cleaned and saved as 'cleaned_chat_data_with_content.csv'")
