from presidio_analyzer import AnalyzerEngine


analyzer = AnalyzerEngine()


def detect_pii(text: str):

    results = analyzer.analyze(
        text=text,
        language="en"
    )

    pii_results = []

    for result in results:

        pii_results.append({
            "pii_type": result.entity_type,
            "start": result.start,
            "end": result.end,
            "score": result.score
        })

    return pii_results