import random

def identify(features):

    scanners = [
        "Canon LiDE 120",
        "HP ScanJet Pro 2500",
        "Epson V600"
    ]

    scanner = random.choice(scanners)

    confidence = round(random.uniform(80,95),2)

    return {
        "scanner":scanner,
        "confidence":confidence
    }