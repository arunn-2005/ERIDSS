from app.services.pii_detector import detect_pii, mask_pii


text = """
Ravi Kumar works in the Finance Department.

Ravi Kumar email address is ravi.kumar@gmail.com.

His phone number is +91 9876543210.

The server IP address is 192.168.1.25.
"""


results = detect_pii(text)


print("===== DETECTED PII =====")

for result in results:

    print(
        result["pii_type"],
        "=>",
        text[result["start"]:result["end"]],
        "=>",
        result["score"]
    )


sanitized_text = mask_pii(
    text,
    results
)


print("\n===== ORIGINAL TEXT =====")

print(text)


print("\n===== SANITIZED TEXT =====")

print(sanitized_text)